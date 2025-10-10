import sys
import os

from .runner_factory import Runner, Factory

_SYSTEM_FACTORY = None


class PythonREPL(Runner):

    ICON = ("icons.flow", "python")
    TAGS = ["Scripting"]

    @classmethod
    def runner_name(cls):
        return "Python"

    def keep_terminal(self):
        return False

    def executable(self):
        return sys.executable

    def argv(self):
        return []


class CMD(Runner):

    TAGS = ["Scripting"]
    ICON = ("icons.flow", "workstation")

    def show_terminal(self):
        return True

    def keep_terminal(self):
        return True

    def executable(self):
        return "echo"

    def argv(self):
        return "Here is a terminal, have fun!".split()


class Explorer(Runner):

    ICON = ("icons.flow", "explorer")
    TAGS = ["Open", "Reveal"]

    @classmethod
    def runner_name(cls):
        return "Explorer"

    def show_terminal(self):
        # This is needed for explorer to behave correctly :/
        return True

    def keep_terminal(self):
        return False

    def executable(self):
        return "explorer.exe"


def get_system_factory():
    global _SYSTEM_FACTORY
    if _SYSTEM_FACTORY is None:
        factory = Factory("System")
        if os.name == "nt":
            factory.ensure_runner_type(Explorer)
            factory.ensure_runner_type(CMD)
        factory.ensure_runner_type(PythonREPL)
        _SYSTEM_FACTORY = factory
    return _SYSTEM_FACTORY
