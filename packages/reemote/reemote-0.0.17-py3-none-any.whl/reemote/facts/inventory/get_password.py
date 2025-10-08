from reemote.command import Command

class Get_password:
    def __repr__(self):
        return f"Get_password()"

    @staticmethod
    async def _get_password_callback(host_info, global_info, command, cp, caller):
        return host_info["password"]

    def execute(self):
        r = yield Command(
            f"{self}",
            local=True,
            callback=self._get_password_callback,
            caller=self
        )
