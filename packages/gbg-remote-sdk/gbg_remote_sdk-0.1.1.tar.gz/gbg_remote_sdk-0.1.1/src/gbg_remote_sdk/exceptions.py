class GbgRemoteApiError(Exception):
    pass


class NoGbgProgramLoadedError(GbgRemoteApiError):
    def __init__(self, *, attempted_action: str):
        super().__init__(f"No GBG program is loaded. Attempted action cannot be completed: {attempted_action}")


class WorkcellProcessNotAvailableError(GbgRemoteApiError):
    def __init__(self, *, process_name: str, available_process_names: list[str]):
        super().__init__(
            f"Workcell process not available: {process_name}\nAvailable processes: {', '.join(available_process_names)}"
        )


class GbgVariableNotFoundError(GbgRemoteApiError):
    def __init__(self, variable_name: str):
        super().__init__(f"Variable not found: {variable_name}")
