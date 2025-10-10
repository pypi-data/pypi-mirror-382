from kabaret.app._actor import Actor, Cmd, Cmds

from .. import runner_factory
from ..runners import get_system_factory


class SubprocessManagerCmds(Cmds):
    pass


@SubprocessManagerCmds.cmd
class List_Runner_Infos(Cmd):
    """
    Returns an ordered list of dicts with keys:
        (
            id,
            label,
            name,
            icon,
            version,
            is_running,
            log_path,
            command,
            last_run_time,
            pid,
            return_code,
        )
    """
    def _decode(self):
        pass

    def _execute(self):
        return self.actor().get_runner_infos()


@SubprocessManagerCmds.cmd
class Get_Runner_Info(Cmd):
    """
    Returns a dict describing the runner instance
    with the given index
    """
    def _decode(self, rid):
        self._rid = rid

    def _execute(self):
        return self.actor().get_runner_info(
            self._rid
        )


@SubprocessManagerCmds.cmd
class Get_Runner_Versions(Cmd):
    def _decode(self, runner_name, tags=[]):
        self.runner_name = runner_name
        self.tags = tags

    def _execute(self):
        return (
            self.actor()
            .get_factories()
            .get_runner_versions(self.runner_name, self.tags)
        )


@SubprocessManagerCmds.cmd
class Launch_Runner_Instance(Cmd):
    """
    Launches the runner subprocess.
    """
    def _decode(self, rid):
        self._rid = rid

    def _execute(self):
        runner = self.actor().get_runner(
            self._rid
        )
        runner.run()


@SubprocessManagerCmds.cmd
class Terminate_Runner_Instance(Cmd):
    """
    Terminates the runner subprocess.
    """
    def _decode(self, rid):
        self._rid = rid

    def _execute(self):
        runner = self.actor().get_runner(
            self._rid
        )
        runner.terminate()


@SubprocessManagerCmds.cmd
class Kill_Runner_Instance(Cmd):
    """
    Kills the runner subprocess.
    """
    def _decode(self, rid):
        self._rid = rid

    def _execute(self):
        runner = self.actor().get_runner(
            self._rid
        )
        runner.kill()


@SubprocessManagerCmds.cmd
class Delete_Runner_Instance(Cmd):
    """
    Delete the runner from the list of
    stored runner instances.
    """
    def _decode(self, rid):
        self._rid = rid

    def _execute(self):
        return self.actor().delete_runner(
            self._rid
        )


@SubprocessManagerCmds.cmd
class Run(Cmd):
    def _decode(
        self,
        runner_name,
        tags=[],
        version=None,
        label=None,
        extra_argv=[],
        extra_env={},
        extra_handlers=[]
    ):
        self.runner_name = runner_name
        self.tags = tags
        self.version = version
        self.label = label
        self.extra_argv = extra_argv
        self.extra_env = extra_env
        self.extra_handlers = extra_handlers

    def _execute(self):
        rid = self.actor().run(
            self.runner_name,
            self.tags,
            self.version,
            self.label,
            self.extra_argv,
            self.extra_env,
            self.extra_handlers
        )
        return rid


class SubprocessManager(Actor):
    def __init__(self, session):
        super(SubprocessManager, self).__init__(session)
        # self._manager = manager.SubprocessManager()
        self._factories = runner_factory.Factories()
        self._subprocess_manager = runner_factory.SubprocessManager()

        # Add default factories:
        self._factories.ensure_factory(get_system_factory())

    def _create_cmds(self):
        return SubprocessManagerCmds(self)

    def get_factories(self):
        return self._factories

    def create_new_factory(self, name):
        return self._factories.create_new_factory(name)

    def ensure_factory(self, runner_factory):
        self._factories.ensure_factory(runner_factory)
        self.session().dispatch_event(
            "subprocess_manager.factory_added", factory_name=runner_factory.name
        )

    def get_runner_infos(self):
        """
        Return a list of dict with keys:
            label, name, icon, version, is_running, log_path
        """
        return self._subprocess_manager.get_runner_infos()
    
    def get_runner_info(self, rid):
        return self._subprocess_manager.get_runner_info(rid)
    
    def get_runner(self, rid):
        return self._subprocess_manager.get_runner(rid)
    
    def delete_runner(self, rid):
        deleted = self._subprocess_manager.delete_runner(rid)
        if not deleted:
            self.log("Could not delete runner with id %s" % rid)
        
        return deleted

    def run(
        self,
        runner_name,
        tags=[],
        version=None,
        label=None,
        extra_argv=[],
        extra_env={},
        extra_handlers=[]
    ):
        runner = self._factories.get_runner(
            runner_name, tags, version, label, extra_argv, extra_env, extra_handlers
        )
        if runner is None:
            self.session().log_error(
                f'No runner found with name \'{runner_name}\' and tags {tags}'
            )
            rid = None
        else:
            rid = self._subprocess_manager.run(runner)
        return rid
