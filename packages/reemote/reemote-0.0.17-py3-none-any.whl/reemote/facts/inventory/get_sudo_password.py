from reemote.command import Command

class Get_sudo_password:
    def __repr__(self):
        return f"Get_sudo_password()"

    @staticmethod
    async def _get_sudo_password_callback(host_info, global_info, command, cp, caller):
        return global_info["sudo_password"]

    def execute(self):
        r = yield Command(
            f"{self}",
            local=True,
            callback=self._get_sudo_password_callback,
            caller=self
        )
