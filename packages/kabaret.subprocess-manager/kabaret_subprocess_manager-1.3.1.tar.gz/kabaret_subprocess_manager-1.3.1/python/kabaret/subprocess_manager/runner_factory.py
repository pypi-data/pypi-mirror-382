import os
import subprocess
import time
import uuid
import pathlib
import re
from datetime import datetime
from threading import Thread

import logging

logger = logging.getLogger('kabaret')


class RunnerHandler(Thread):

    def __init__(self, runner):
        Thread.__init__(self)
        self.runner = runner

    def run(self):
        while self.runner.is_running() and self.runner.extra_handlers is not None:

            for handler in self.runner.extra_handlers:
                log_path = self.runner.get_log_path()
                whence = min(os.path.getsize(log_path), handler['whence'])

                # Open part of the log
                with open(log_path, 'rb') as f_log:
                    f_log.seek(-whence, 2)
                    log = f_log.read().decode('utf-8')

                # Check the next handler if there is no matching pattern
                m = re.search(handler['pattern'], log)
                if m is None:
                    continue

                # Ignore INFO handler type (TODO: Make specific use case)
                if handler['handler_type'] != 'INFO':
                    # Don't append handler if already catched
                    if any(h['description'] == handler['description'] for h in self.runner.handlers_catch) is False:
                        # Open the full log for find line number
                        with open(log_path) as f_log:
                            full_log = f_log.readlines()

                        line_number = [x for x in range(len(full_log)) if re.search(handler['pattern'], full_log[x])][0]

                        # Append handler to catch list
                        self.runner.handlers_catch.append(dict(
                            handler_type=handler['handler_type'],
                            description=handler['description'],
                            match='\n'.join(m.groups()) if m.groups() else m.group(0),
                            line=line_number
                        ))

                        logger.info(f"[RUNNER] {handler['description']}: {self.runner.runner_name()} - {self.runner.label}")

            time.sleep(1)


class Runner(object):
    """
    The Runner is able to spawn a subprocess with controled
    command line and environment (among others things).

    """

    TAGS = []
    ICON = None

    @classmethod
    def runner_name(cls):
        """
        Returns the name of the Runner.
        This value does not need to be unic among your runners:
        tags are also used to differenciate them. (but you'll
        probably need to ensure (name,tags) are unique.)
        """

        return cls.__name__

    @classmethod
    def runner_tags(cls):
        """
        Returns a list of tags for this runner.
        Tags are used to group and sort runner in GUIs, and
        to uniquify runners.

        Only the first tag is used to group runners in UIs.

        Default is to return the `TAGS` class attribute.
        """
        return cls.TAGS

    @classmethod
    def has_tags(cls, tags):
        """
        Returns True if all given tags are in `runner_tags()`
        """
        return set(tags).issubset(set(cls.runner_tags()))

    @classmethod
    def runner_icon(cls):
        """
        This value depends on how you entend to use it...
        Default is to return the `ICON` class attribute.
        """
        return cls.ICON

    @classmethod
    def can_edit(cls, filename):
        """
        Must be implemented to return True if the filename
        looks like something supported by this process.

        Default is to return False
        """
        return False

    @classmethod
    def supported_versions(cls):
        """
        Return a list of supported version names.
        A version name of `None` represents the default version.

        Default is to return [None]
        """
        return [None]

    @classmethod
    def runner_handlers(cls):
        """
        Return a list of runner handlers
        
        An runner handler is represented by a dict with keys:
            handler_type, description, pattern, whence

        Handler types:
            ERROR
            WARNING
            INFO
            SUCCESS

        They are used to catch specific messages in the log such as errors, status, success etc.

        Default is to return a empty list
        """
        return []

    def __init__(self, version=None, label=None, extra_argv=[], extra_env={}, extra_handlers=[]):
        super(Runner, self).__init__()
        self.version = version
        self.label = label or self.runner_name()
        self.extra_argv = extra_argv
        self.extra_env = extra_env
        self.extra_handlers = extra_handlers
        self.handlers_catch = []

        self._popen = None
        self._log_path = None
        self._last_run_time = None
        self._last_cmd = None
        self._running_delay = 0

    def show_terminal(self):
        return True

    def keep_terminal(self):
        return True

    def executable(self):
        """
        Must return the path of the executable to run
        depending on self.version
        """
        raise NotImplementedError()

    def argv(self):
        """
        Must return the list of arg values for the command to run
        including self.extra_argv.
        Default is to return extra_argv
        """
        return self.extra_argv

    def env(self):
        """
        Returns the env to use for the command to run.
        Default is a copy of os.environ and update with
        self.extra_env
        """
        env = os.environ.copy()
        env.update(self.extra_env)
        return env

    def run(self):
        cmd = [self.executable()]
        cmd.extend(self.argv())

        env = self.env()

        os_flags = {}

        # Disowning processes in linux/mac
        if hasattr(os, "setsid"):
            os_flags["preexec_fn"] = os.setsid

        # Disowning processes in windows
        if hasattr(subprocess, "STARTUPINFO"):
            # Detach the process
            os_flags["creationflags"] = subprocess.CREATE_NEW_CONSOLE

            # Hide the process console
            startupinfo = subprocess.STARTUPINFO()
            if self.show_terminal():
                flag = "/C"
                if self.keep_terminal():
                    flag = "/K"
                cmd = ["cmd", flag] + cmd
            else:
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            os_flags["startupinfo"] = startupinfo

        logger.debug("Running Subprocess: %r", cmd)
        
        if not os.path.exists(self._get_log_dir()):
            os.mkdir(self._get_log_dir())
        
        # Store run time used to compute log paths
        self._last_run_time = time.time()
        cmd = [str(arg) for arg in cmd]
        self._last_cmd = ' '.join(cmd)

        self.create_log_path()
        self.handle_extra_handlers()
        with open(self._log_path, 'w+') as log_fd:
            self._popen = subprocess.Popen(
                cmd,
                env=env,
                stdout=log_fd,
                stderr=log_fd,
                bufsize=0, # unbuffered mode to avoid missing lines
                **os_flags,
            )
        
        # Start handlers check thread
        thread = RunnerHandler(self)
        thread.start()

    def _get_log_dir(self):
        if os.environ.get("KABARET_SUBPROCESS_LOG_PATH"):
            log_dir = os.environ["KABARET_SUBPROCESS_LOG_PATH"]
            if os.path.isdir(log_dir):
                return os.environ["KABARET_SUBPROCESS_LOG_PATH"]
        
        return os.path.normpath(os.path.join(
            pathlib.Path.home(),
            ".kabaret",
            "runners"
        ))

    def create_log_path(self):
        dt = datetime.fromtimestamp(self._last_run_time)
        dt = dt.astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")
        
        path = os.path.join(
            self._get_log_dir(),
            '%s_%s.log' % (self.runner_name(), dt),
        )
        # Specify a different file name if a log already exists for that date and time
        if os.path.exists(path):
            path = os.path.join(
                self._get_log_dir(),
                '%s_%s.log' % (self.runner_name(), f'{dt}_1'),
            )
        self._log_path = path

    def handle_extra_handlers(self):
        if self.extra_handlers is not None:
            extra_handlers = self.extra_handlers
            base_handlers = self.runner_handlers()

            # No need to modify list if no base handlers to check
            if base_handlers is None:
                return

            for i, handler in enumerate(self.extra_handlers):
                # The extra handler is an override of the runner's base handler
                base_check = [i for i, base in enumerate(base_handlers) if base['description'] == handler['description']]

                if base_check is not None:
                    # Remove handler if there is an enabled key and it's defined as False
                    if 'enabled' in handler:
                        if handler['enabled'] is False:
                            del base_handlers[base_check[0]]
                            del extra_handlers[i]
                    # Remove base handler to use the override handler
                    else:
                        del base_handlers[base_check[0]]
            
            # Set up the new list of extra handlers with defaults, extras and overrides
            self.extra_handlers = base_handlers + extra_handlers

    def get_log_path(self):
        return self._log_path

    def has_run(self):
        return self._last_run_time is not None
    
    def cmd(self):
        return self._last_cmd
    
    def pid(self):
        return self._popen.pid
    
    def last_run_time(self):
        return self._last_run_time
    
    def terminate(self):
        self._popen.terminate()
    
    def kill(self):
        self._popen.kill()

    def is_running(self):
        if self._popen.poll() is None: # Is running
            return True
        elif self._running_delay == 2: # To avoid handler capture issues, the false return is used two seconds later.
            return False
        else: # Increase delay value
            self._running_delay += 1
            return True


class Factory(object):
    """
    A Factory is able to find and instanciate registered Runners.
    You manage a collection of Factory with the Factories class.
    """

    def __init__(self, name):
        super(Factory, self).__init__()
        """
        The `name` only purpose is logging info.
        """
        self.name = name
        self._runner_types = []

    def ensure_runner_type(self, RunnerType):
        if RunnerType in self._runner_types:
            return
        self._runner_types.append(RunnerType)

    def list_runner_types(self):
        return list(self._runner_types)

    def list_runner_handlers(self):
        runner_handlers = {}
        for RunnerType in self._runner_types:
            handlers = RunnerType.runner_handlers()
            if handlers:
                runner_handlers[RunnerType.runner_name()] = handlers

        return dict(sorted(runner_handlers.items()))

    def runner_tags(self):
        """
        Returns an ordered list of know tags.
        """
        tags = []  # dont use set to keep order
        for RunnerType in self._runner_types:
            for t in RunnerType.runner_tags():
                if t not in tags:
                    tags.append(t)
        return tags

    def find_runners(self, edited_filename=None, tags=[]):
        """
        Returns a list of (runner names, tags) supporting the given
        filename and having given tags.

        An `edited_filename` of `None` will match any RunnerType
        """
        names_and_tags = []
        for RunnerType in self._runner_types:
            if not RunnerType.has_tags(tags):
                continue
            if edited_filename is None or RunnerType.can_edit(edited_filename):
                names_and_tags.append(
                    (RunnerType.runner_name(), RunnerType.runner_tags(),)
                )
        return names_and_tags

    def get_runner_versions(self, runner_name, tags=[]):
        """
        Only the first matching runner is processed.
        If the runner is not found, None is returned.

        Using None as `tags` will match any RunnerType
        with `runner_name`
        """
        for RunnerType in self._runner_types:
            if tags is not None and not RunnerType.has_tags(tags):
                continue
            if RunnerType.runner_name() == runner_name:
                return RunnerType.supported_versions()
        return None

    def get_runner(
        self,
        runner_name,
        tags=[],
        version=None,
        label=None,
        extra_argv=[],
        extra_env={},
        extra_handlers=[]
    ):
        """
        Returns the first runner with the given runner_name and tags,
        configured with version, label, extra_arv and extra_env.
        """
        for RunnerType in self._runner_types:
            if RunnerType.runner_name() != runner_name:
                continue
            if not RunnerType.has_tags(tags):
                continue
            return RunnerType(
                version=version,
                label=label,
                extra_argv=extra_argv,
                extra_env=extra_env,
                extra_handlers=extra_handlers
            )
        return None


class Factories(object):

    # NB: I don't use the composition pattern here
    # because I don't want to support a tree of
    # factories.

    def __init__(self):
        super(Factories, self).__init__()
        self._factories = []

    def create_new_factory(self, factory_name):
        """
        Will return a new factory, but WILL NOT REGISTER it.
        """
        return Factory(factory_name)

    def ensure_factory(self, factory):
        if factory in self._factories:
            return
        self._factories.append(factory)

    def list_runner_types(self):
        """
        Returns an ordered list of:
            (factory, RunnerType)
        """
        RunnerTypes = []
        for factory in self._factories:
            for RunnerType in factory.list_runner_types():
                RunnerTypes.append((factory, RunnerType))
        return RunnerTypes

    def runner_tags(self):
        tags = []  # dont use set to keep order
        for factory in self._factories:
            for tag in factory.runner_tags():
                if tag not in tags:
                    tags.append(tag)
        return tags

    def find_runners(self, edited_filename, tags=[]):
        names_and_tags = []  # dont use set to keep order
        for factory in self._factories:
            for nat in factory.find_runners(edited_filename, tags):
                names_and_tags.append(nat)
        return names_and_tags

    def get_runner_versions(self, runner_name, tags=[]):
        """
        Only the first matching runner is processed.
        If the runner is not found, None is returned.
        """
        for factory in self._factories:
            versions = factory.get_runner_versions(runner_name, tags,)
            if versions is not None:
                return versions
        return None

    def get_runner(
        self,
        runner_name,
        tags=[],
        version=None,
        label=None,
        extra_argv=[],
        extra_env={},
        extra_handlers=[]
    ):
        """
        Only the first matching runner is processed.
        """
        for factory in self._factories:
            runner = factory.get_runner(
                runner_name, tags, version, label, extra_argv, extra_env, extra_handlers
            )
            if runner is not None:
                return runner
        return None


class SubprocessManager(object):
    """
    The SubprocessManager manages a list of Runner instances.
    """

    def __init__(self):
        super(SubprocessManager, self).__init__()
        self._runners = {}

    @staticmethod
    def _get_runner_info(runner, rid):
        return dict(
            id=rid,
            label=runner.label,
            name=runner.runner_name(),
            icon=runner.runner_icon(),
            version=runner.version,
            is_running=runner.is_running(),
            log_path=runner.get_log_path(),
            command=runner.cmd(),
            last_run_time=runner.last_run_time(),
            pid=runner.pid(),
            handlers=runner.extra_handlers,
            handlers_catch=runner.handlers_catch
        )

    @staticmethod
    def _get_unknown_runner_info(rid):
        return dict(
            id=rid,
            label='!!!',
            name='!!!',
            icon=('icons.libreflow', 'exclamation-sign-colored'),
            version='!!!',
            is_running=False,
            log_path='!!!',
            command='!!!',
            last_run_time=-1,
            pid=-1,
            handlers=[],
            handlers_catch=[]
        )

    def get_runner_infos(self):
        """
        Return a list of dict with keys:
            label, name, icon, version, is_running, log_path
        """
        infos = []
        for id, runner in self._runners.items():
            if runner.has_run():
                infos.append(
                    self._get_runner_info(runner, id)
                )
        
        return infos

    def get_runner_info(self, rid):
        """
        Returns data of the runner indexed with
        the given id `rid`, as a dict with keys:
            id, label, name, icon, version, is_running, log_path, pid
        """
        try:
            runner = self._runners[rid]
        except KeyError:
            return self._get_unknown_runner_info(rid)
        else:
            return self._get_runner_info(runner, rid)

    def get_runner(self, rid):
        return self._runners.get(rid, None)
    
    def delete_runner(self, rid):
        try:
            self._runners.pop(rid)
        except KeyError:
            return False
        else:
            return True

    def run(self, runner):
        if runner.executable() is not None :
            if not os.path.exists(runner.executable()):
                raise Exception('[RUNNER] Executable path not found')

        rid = self._add_runner(runner)
        runner.run()
        return rid

    def _add_runner(self, runner):
        rid = str(uuid.uuid4())
        max_tries = 10
        i = 0
        while rid in self._runners and i < max_tries:
            rid = str(uuid.uuid4())
            i += 1
        if i == max_tries:
            raise Exception('Could not create a new runner...')

        self._runners[rid] = runner
        return rid


def test():
    class MyRunner1(Runner):
        TAGS = ["A", "B", "C", "D"]

    class MyRunner2(Runner):
        TAGS = ["C", "D", "E", "F"]

    factory_1 = Factory("F1")
    factory_1.ensure_runner_type(MyRunner1)

    factory_2 = Factory("F2")
    factory_2.ensure_runner_type(MyRunner2)

    factories = Factories()
    factories.ensure_factory(factory_1)
    factories.ensure_factory(factory_2)

    tags = factories.runner_tags()
    print("TAGS:", tags)
    assert tags == ["A", "B", "C", "D", "E", "F"]

    runners = factories.find_runners(None, ["D", "C"])
    print("Runners:", runners)
    assert runners == [
        ("MyRunner1", ["A", "B", "C", "D"]),
        ("MyRunner2", ["C", "D", "E", "F"]),
    ]


if __name__ == "__main__":
    test()
