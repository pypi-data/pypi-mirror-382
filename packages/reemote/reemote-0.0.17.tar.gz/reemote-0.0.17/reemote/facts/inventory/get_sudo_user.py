from reemote.command import Command

class Get_sudo_user:
    def __repr__(self):
        return f"Get_sudo_user()"

    @staticmethod
    async def _get_sudo_user_callback(host_info, global_info, command, cp, caller):
        return global_info["sudo_user"]

    def execute(self):
        r = yield Command(
            f"{self}",
            local=True,
            callback=self._get_sudo_user_callback,
            caller=self
        )
