from pydantic import BaseModel


class WorkcellProcessParameter(BaseModel):
    variable_name: str
    variable_value: bool | int | float | str | None

    @property
    def variable_value_in_gbg_format(self) -> str:
        """Convert the variable value to a string that GBG can understand."""
        if self.variable_value is None:
            return ""
        if isinstance(self.variable_value, bool):
            return "True" if self.variable_value else "False"
        if isinstance(self.variable_value, (float, int)):
            if int(self.variable_value) == self.variable_value:
                return str(int(self.variable_value))
        return str(self.variable_value)
