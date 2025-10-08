from reemote.command import Command

class Get_host:
    def __repr__(self):
        return f"Get_host()"

    @staticmethod
    async def _get_host_callback(host_info, global_info, command, cp, caller):
        return host_info["host"]

    def execute(self):
        r = yield Command(
            f"{self}",
            local=True,
            callback=self._get_host_callback,
            caller=self
        )
