import io
import logging
from collections.abc import Callable
from functools import partial
from ipaddress import IPv4Address
from pathlib import Path
from time import perf_counter_ns
from typing import Any
from typing import cast

import requests
from zeep import Client
from zeep.exceptions import Fault
from zeep.transports import Transport

from .constants import INSTRUMENT_STATUS_VARIABLE_NAME_SUFFIX
from .constants import InstrumentName
from .constants import InstrumentStatus
from .constants import OrderStatus
from .constants import ProgramStatus
from .exceptions import GbgVariableNotFoundError
from .exceptions import NoGbgProgramLoadedError
from .exceptions import WorkcellProcessNotAvailableError
from .models import WorkcellProcessParameter

logger = logging.getLogger(__name__)


class GbgRemoteSdk:
    def __init__(self, *, hostname: str | IPv4Address = "localhost", port: int = 8080, route: str = "/GBGRemote"):
        super().__init__()
        path_to_wsdl = Path(__file__).parent / "vendor_files" / "wsdl.xml"
        # TODO: obtain the WSDL from the API endpoint and compare it to the local copy to ensure it matches expectations
        with path_to_wsdl.open("r", encoding="utf-8") as f:
            original_wsdl = f.read()
        endpoint = f"http://{hostname!s}:{port}{route}"
        wsdl_with_desired_endpoint = original_wsdl.replace("http://localhost:8080/GBGRemote", endpoint)
        self._client = Client(
            io.StringIO(wsdl_with_desired_endpoint),
            transport=Transport(
                timeout=0.5,  # pyright: ignore[reportArgumentType] # zeep says it only wants ints, but it's just passing it to requests, which accepts floats
                operation_timeout=3,
            ),
        )
        self._short_timeout_client = Client(
            self._client.wsdl,
            transport=Transport(
                timeout=0.5,  # pyright: ignore[reportArgumentType] # zeep says it only wants ints, but it's just passing it to requests, which accepts floats
                operation_timeout=0.5,
            ),
        )
        self.hostname = str(hostname)  # tried converting everything to Ipv4address, but it didn't work with localhost
        self.port = port
        self.route = route

    # Known problems: GetStatus will return "Running" even when an error is thrown (later version of GBG fixes this)
    # GetStatusDetails just appears to return an empty string (although maybe if there was an error, it would return something more meaningful)
    # There's no way to specifically get a list of instruments in the workcell---the workaround is just check all variable names for things that end in `.status`
    # There's no known way to tell if GBG is simulating an instrument within a workcell
    def _invoke_request(self, request: Callable[[], Any]) -> Any:  # noqa: ANN401 # yes, Any is generally bad, but zeep WSDL is terribly typed
        start_time = perf_counter_ns()
        response = request()
        end_time = perf_counter_ns()
        logger.debug(  # TODO: figure out how to include the request name and parameters in the log
            "Invoked GBG Remote API method ", extra={"gbg_remote_api_call_duration_ns": end_time - start_time}
        )
        return response

    def is_simulated(self) -> bool:
        try:
            response = self._invoke_request(self._client.service.GetIsSimulated)
        except Fault as e:
            if "Object reference not set to an instance of an object" in str(e):
                raise NoGbgProgramLoadedError(attempted_action="GetIsSimulated") from e
            raise  # pragma: no cover # not worth triggering a different type of error just to hit this default re-raise
        response = cast(bool, response)
        assert isinstance(response, bool), (
            f"Expected response to be of type bool, but got type {type(response)} for {response}"
        )
        return response

    def get_loaded_program(self) -> str | None:
        response = cast(str, self._invoke_request(self._client.service.GetLoadedProgram))
        assert isinstance(response, str), (
            f"Expected response to be of type str, but got type {type(response)} for {response}"
        )
        if response == "None":
            return None
        return response

    def is_api_reachable(self) -> bool:
        try:
            self._invoke_request(
                self._short_timeout_client.service.GetLoadedProgram
            )  # arbitrary API call that should always succeed
        except requests.exceptions.ConnectionError:
            return False
        return True

    def get_status(self) -> ProgramStatus:
        response = cast(str, self._invoke_request(self._client.service.GetStatus))
        assert isinstance(response, str), (
            f"Expected response to be of type str, but got type {type(response)} for {response}"
        )
        return ProgramStatus(response)

    def get_variable_names(self) -> list[str]:
        response = self._invoke_request(self._client.service.GetVariableNames)
        if (
            response is None
        ):  # there should never actually be no variables...this is what happens when no program is loaded
            raise NoGbgProgramLoadedError(attempted_action="GetVariableNames")
        response = cast(list[str], response)
        assert isinstance(response, list), (
            f"Expected response to be of type list, but got type {type(response)} for {response}"
        )
        return response

    def get_variable_value(self, variable_name: str) -> str | None:
        try:
            response = self._invoke_request(partial(self._client.service.GetVariableValue, variable_name))  # pyright: ignore[reportUnknownArgumentType] # the WSDL is not typed
        except Fault as e:
            if "Get Variable Value could not find a variable named" in str(e):
                raise GbgVariableNotFoundError(variable_name) from e
            raise  # pragma: no cover # not worth triggering a different type of error just to hit this default re-raise
        if response is None:
            return None
        response = cast(str, response)
        assert isinstance(response, str), (
            f"Expected response to be of type str, but got type {type(response)} for {response}"
        )

        return response

    def get_instrument_statuses(self) -> dict[InstrumentName, InstrumentStatus]:
        statuses: dict[InstrumentName, InstrumentStatus] = {}
        try:
            variable_names = self.get_variable_names()
        except NoGbgProgramLoadedError as e:
            raise NoGbgProgramLoadedError(attempted_action="GetInstrumentStatuses") from e
        for variable_name in variable_names:
            if variable_name.endswith(INSTRUMENT_STATUS_VARIABLE_NAME_SUFFIX):
                instrument_name = variable_name[: -len(INSTRUMENT_STATUS_VARIABLE_NAME_SUFFIX)]
                status = self.get_variable_value(variable_name)
                statuses[instrument_name] = InstrumentStatus.UNKNOWN if status is None else InstrumentStatus(status)
        return statuses

    def start_workcell_process(
        self, *, process_name: str, order_id: str, parameters: list[WorkcellProcessParameter]
    ) -> str:
        """Start a workcell process and return the RunID that was started."""
        available_processes = self.get_available_workcell_processes()
        if process_name not in available_processes:
            raise WorkcellProcessNotAvailableError(
                process_name=process_name, available_process_names=available_processes
            )

        # many things were attempted to use native python data structures of list/dict, but nothing worked except this
        array_type = self._client.get_type(  # pyright: ignore[reportUnknownMemberType] # zeep WSDL is not typed
            "{http://schemas.microsoft.com/2003/10/Serialization/Arrays}ArrayOfKeyValueOfstringstring"
        )
        assert array_type is not None, "Failed to get the ArrayOfKeyValueOfstringstring type from the WSDL"

        parsed_parameters = array_type(
            KeyValueOfstringstring=[
                {"Key": param.variable_name, "Value": param.variable_value_in_gbg_format} for param in parameters
            ]
        )

        response = self._invoke_request(
            partial(  # pyright: ignore[reportUnknownArgumentType] # the WSDL is not typed
                self._client.service.Run,
                workcellProcessName=process_name,
                orderId=order_id,
                parameters=parsed_parameters,
            )
        )
        assert isinstance(response, str), (
            f"Expected response to be of type str, but got type {type(response)} for {response}"
        )
        return response

    def get_order_status(self, order_id: str) -> OrderStatus:
        response = self._invoke_request(
            partial(  # pyright: ignore[reportUnknownArgumentType] # the WSDL is not typed
                self._client.service.GetOrderStatus, orderId=order_id
            )
        )
        assert isinstance(response, str), (
            f"Expected response to be of type str, but got type {type(response)} for {response}"
        )
        return OrderStatus(response)

    def get_available_workcell_processes(self) -> list[str]:
        response = self._invoke_request(self._client.service.GetAvailableWorkcellProcesses)
        assert isinstance(response, list), (
            f"Expected response to be of type list, but got type {type(response)} for {response}"
        )
        return cast(list[str], response)
