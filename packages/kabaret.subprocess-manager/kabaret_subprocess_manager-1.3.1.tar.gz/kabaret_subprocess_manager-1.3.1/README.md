# kabaret.subprocess_manager

Subprocess Manager for Kabaret.

Provides an Actor, Views and Flow Objects to manage collections of  environment + command-lines, as well as running & controling them.


# Synopsis 

### Runners

You implement your `Runners` by subclassing `kabaret.subprocess_manager.runner_factory.Runner`. *Runners* have a name, some tags, a liste of supported versions, an icon, etc...

At runtime, you add your *Runners* to a `Factory`. A *Factory* has a name, can lookup *Runners* based on name and tags, etc...
You will probably have several factories.

### SubprocessManager Actor

In order to use them, you will *Add* them to the `SubprocessManager` Actor. There is 2 places where you may want to do it:

- In your Session, when creating the Action. This is nice for generic stuff (explorer, shell, text editors, ...) 
- In your Flow, when a project is instaciated. This is nice for production specific tools where the environment and the version are precisely defined (scene editing, baking, render, ...)
 
### LaunchToolBar and SubprocessView

If you add the LaunchToolBar to your *Session*, you will be able to run your Runner by clicking on the toolbar buttons.

Those run take no parameters.

If you add the SubprocessView, you will see a list of process you ran, with their outputs, and you will have opportinities to remove/kill/rerun...

### Flow RunAction 

A big majority of your Runner will be ran from your flows though. 

The `kabaret.subprocess_manager.flow.RunAction` Action will let the user trigger your Runners with the usual `flow.Action` fonctionnalities.

By using the *RunAction*, you will be able to access your flow to configure your *Runners* runs. For example using project settings to get the project resolution and frame rate...

### Logs

Each runner's log is stored in the user's temporary folder and in a subfolder called `.kabaret`. If you want to change the path, you can set it with the `KABARET_SUBPROCESS_LOG_PATH` environment variable.

# Usage:

## Define your process Runners:
```
from kabaret.subprocess_manager.runner_factory import Runner

class MyStuffToRun(Runner):

    ICON = ('icons.gui', 'team-lead')
    TAGS = ['Team', 'Lead', 'Blah']

    def supported_versions(self):
        return ['v1', 'v2]

    def executable(self):
        return '/path/to/{}/executable'.format(self.version)

    def argv(self):
        index = 'https://blah.blu.tv'
        if self.version == 'v2':
            index = 'https://blah2022.blu.tv'

        argv = ['--user', current_user, '--index', index]

        # To allow configured run, you must
        # use self.extra_argv:
        return argv+self.extra_argv

    def env(self):
        env = os.environ.copy()
        env['MY_STUFF_CONFIGVAR] = 'my_stuff_config_value'

        # To allow configured run, you must
        # use self.extra_argv:
        env.update(self.extra_env)

        return env

```
There are more tunning options, like terminal hidding etc... 

Everything is procedural (method call, no static/declarative thingy) so you're in full control ;)

If you want the Runner icon or tags to depend on the date or the current user your can override the classmethods `runner_icon()` and `runner_tags()`


## Configure your Session:

In your session class, add the `SubprocessView` and the `LaunchToolBar` to
the registered view types.

```
class MySession(gui.KabaretStandaloneGUISession):

    def register_view_types(self):
        super(MySession, self).register_view_types()

        type_name = self.register_view_type(SubprocessView)
        self.add_view(type_name, hidden=True)

        type_name = self.register_view_type(LauncherToolBar)
        self.add_view(
            type_name, hidden=False, 
            area=QtCore.Qt.RightToolBarArea
        )
```

In the `_create_actors()` method, you will create the `SubprocessManager` Actor and configure it with your generic runners:

```
    def _create_actors(self):
        # Add the Actor to the session:
        subprocess_manager = SubprocessManager(self)

        # Create your factory:
        site_factory = factories.create_new_factory('Studio Tools')

        # Ensure your Runners are known there:
        site_factory.ensure_runner_type(my_runners.Blender)
        site_factory.ensure_runner_type(my_runners.Godot)
        site_factory.ensure_runner_type(my_runners.Krita)

        # Register your factory to the Actor:
        subprocess_manager.ensure_factory(site_factory)

```

Now you have an awesome toolbar with buttons to launch each 
version of the runner you registered \o/
(They appear grouped by the first tag of each Runner)

## Configure your Project

Some *Runner*s will be specific to flow type.
For example, not all pipelines will supported USDView...

So you need to define Runners inside your flow and have them show up in the toolbar only if you entered a project using this flow.

One way to do so is to use your Project's `_fill_ui()` as a trigger for installation:

```
class MyProject(flow.Object):

    episodes = flow.Child(Episodes).ui(show_filter=True)
    admin = flow.Child(Admin)

    _RUNNERS_FACTORY = None

    def ensure_runners_loaded(self):
        session = self.root().session()
        subprocess_manager = session.get_actor('SubprocessManager')

        if self._RUNNERS_FACTORY is None:
            self._RUNNERS_FACTORY = subprocess_manager.create_new_factory(
                'Best Pipeline Eva'
            )
            self._RUNNERS_FACTORY.ensure_runner_type(
                my_runners.USDView,
                my_runners.USDBlast,
            )
        subprocess_manager.ensure_factory(self._RUNNERS_FACTORY)

    def _fill_ui(self, ui):
        # We can't setup runner in the constructor because
        # it needs access to self.session() which is set
        # *after* constructor :/
        # So we set them up the first time the project is displayed:
        if self._RUNNERS_FACTORY is None:
            self.ensure_runners_loaded()


``` 

## Run Subprocesses from the Flow

This is the most important since running stuff within 
a context is what we want 90% of time :p

In order to use your Runners from the flow and to have them use
some values from your flow (filename, env var, flag, etc...), you
will use the Action `kabaret.subprocess_manager.flow.RunAction`:

Here we define a RunAction that uses the parent's `filename` Param as a command line argument to a `TextEdit` runner:
```
class EditAction(RunAction):

    _scene = flow.Parent()

    def runner_name_and_tags(self):
        # Specifying None for tags means 'accept all'
        return 'TextEdit', None

    def needs_dialog(self):
        return False

    def extra_argv(self):
        # All strings returned here will be
        # appended to the runner command line:
        return [self._scene_.filename.get()]
``` 

You can also provide `extra_env`, let the user select the version
of the runner, etc... 

You can ask for more examples and support in the kabaret discord:
    https://www.kabaretstudio.com/support

Happy Running ! :)


