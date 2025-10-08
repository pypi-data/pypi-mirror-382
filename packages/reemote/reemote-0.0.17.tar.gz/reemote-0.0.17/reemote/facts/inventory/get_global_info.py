from reemote.command import Command

class Get_global_info:
    def __init__(self, field=None):
        if field is not None and not isinstance(field, str):
            raise ValueError("Field must be a string or None")
        self.field = field

    def __repr__(self):
        return f"Get_host_info(field={self.field})"

    async def _get_global_info_callback(self, host_info, global_info, command, cp, caller):
        return global_info.get(self.field)

    def execute(self):
        r = yield Command(
            f"{self}",
            local=True,
            callback=self._get_global_info_callback,
            caller=self
        )