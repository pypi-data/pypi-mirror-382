from reemote.command import Command

class Get_username:
    def __repr__(self):
        return f"Get_username()"

    @staticmethod
    async def _get_username_callback(host_info, global_info, command, cp, caller):
        return host_info["username"]

    def execute(self):
        r = yield Command(
            f"{self}",
            local=True,
            callback=self._get_username_callback,
            caller=self
        )
