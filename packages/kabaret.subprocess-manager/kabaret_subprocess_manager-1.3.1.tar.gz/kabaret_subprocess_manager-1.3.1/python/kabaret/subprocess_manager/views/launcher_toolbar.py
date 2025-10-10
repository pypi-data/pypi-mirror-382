from kabaret.app import resources

import kabaret.app.ui.gui.widgets.widget_view
from kabaret.app.ui.gui.widgets.widget_view import ToolBarView, QtWidgets, QtGui, QtCore


class LauncherToolBar(ToolBarView):
    def __init__(self, *args, **kwargs):
        kwargs["area"] = QtCore.Qt.LeftToolBarArea
        super(LauncherToolBar, self).__init__(*args, **kwargs)

        self.refresh()

    def refresh(self):
        self.clear()
        self.load()

    def clear(self):
        actions = self.actions()
        for action in actions:
            self.removeAction(action)
            action.deleteLater()

    def load(self):
        runners_list = self.session.cmds.SubprocessManager.list_runners(reverse=True)
        last_factory_name = None
        last_group_name = None
        tb = None
        for entry in runners_list:
            factory_name = entry["factory_name"]
            group_name = entry["group_name"]
            if last_factory_name != factory_name:
                self.addSeparator()
                last_factory_name = factory_name
            if tb is None or group_name != last_group_name:
                tb = self._create_group(entry)
                last_group_name = group_name
            self._add_runner(entry, tb)
            # self.ensure_group(factory_name, group_name)

    def _create_group(self, entry):

        factory_name = entry["factory_name"]
        name = entry["group_name"]
        icon_ref = entry["group_icon"]

        tb = QtWidgets.QToolButton(self)
        self.addWidget(tb)

        tb.setProperty("hide_arrow", True)
        tb.setText(name)
        tb.setToolTip("{} ({})".format(name, factory_name))
        tb.setPopupMode(tb.ToolButtonPopupMode.InstantPopup)
        tb.setIcon(resources.get_icon(icon_ref))
        tb.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        return tb

    def _add_runner(self, entry, tb):
        name = entry["runner_name"]
        version = entry["version"]
        tags = entry["runner_tags"]
        icon = entry["runner_icon"]

        label = name
        if version is not None:
            label = "{} ({})".format(name, version)
        action = QtGui.QAction(tb)
        action.setText(label)
        action.setIcon(resources.get_icon(icon))
        action.triggered.connect(
            lambda checked, n=name, t=tags, v=version: self._run(n, t, v)
        )
        action = tb.addAction(action)

    def _run(self, name, tags, version):
        self.session.cmds.SubprocessManager.run(name, tags, version)

    def receive_event(self, event_type, data):
        # print('!??? LauncerToolBar event', event_type, data)
        if event_type == "subprocess_manager.factory_added":
            # TODO: we should sync instead of refresh all
            # But let's not optimize early ;)
            self.refresh()
