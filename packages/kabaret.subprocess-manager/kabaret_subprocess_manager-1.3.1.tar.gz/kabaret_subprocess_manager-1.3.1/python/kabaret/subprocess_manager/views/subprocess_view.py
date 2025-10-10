import os
import re
import timeago
from datetime import datetime
from kabaret.app import resources
from kabaret.app.ui.gui.widgets.widget_view import DockedView, QtWidgets, QtGui, QtCore


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    '''Sort a string in a natural way
    https://stackoverflow.com/a/16090640'''
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]


def timeago_format(time):
    dt = datetime.fromtimestamp(time)
    dt = timeago.format(dt, datetime.now())
    return dt


def custom_format(time, format):
    dt = datetime.fromtimestamp(time)
    dt = dt.astimezone().strftime(format)
    return dt


class SubprocessHandlerItem(QtWidgets.QListWidgetItem):

    # Represents a runner handler captured in the process log.

    ICONS = {
        'ERROR': ('icons.libreflow', 'cross-mark-on-a-black-circle-background-colored'),
        'WARNING': ('icons.libreflow', 'exclamation-sign-colored'),
        'SUCCESS': ('icons.libreflow', 'checked-symbol-colored')
    }

    def __init__(self, tree, data):
        super(SubprocessHandlerItem, self).__init__(tree)
        self.tree = tree
        self._data = data
        
        self.refresh()
    
    def refresh(self):       
        self.setIcon(self.get_icon(self.ICONS.get(self._data['handler_type'])))
        self.setText(self._data['description'])

        font = QtGui.QFont()
        font.setBold(True)
        self.setFont(font)

    @staticmethod
    def get_icon(icon_ref):
        return QtGui.QIcon(resources.get_icon(icon_ref))


class SubprocessHandlersList(QtWidgets.QListWidget):

    # List of all runners' handlers catch in the process log

    def __init__(self, parent, view):
        super(SubprocessHandlersList, self).__init__(parent)
        self.view = view

        self.itemClicked.connect(self.on_item_select)

    def get_columns(self):
        return ['Description']
    
    def refresh(self):
        current_item = self.view.current_item()
        handlers_catch = current_item.handlers_catch()

        for handler in handlers_catch:
            # Don't append handler if it already exists and ignore INFO handler type (TODO: Make specific use case)
            if self.item_exists(handler) or handler['handler_type'] == 'INFO':
                continue
            item = SubprocessHandlerItem(self, handler)

    def item_exists(self, handler):
        for i in range(self.count()):
            item = self.item(i)
            if item._data['description'] == handler['description']:
                return True
        
        return False
    
    def on_item_select(self, item):
        # Move the cursor to the matching line of the selected handler
        output = self.view._subprocess_output._output

        cursor = QtGui.QTextCursor(output.document().findBlockByLineNumber(item._data['line']))
        output.moveCursor(QtGui.QTextCursor.End)
        output.setTextCursor(cursor)

    def paintEvent(self, event):
        # Display placeholder text when list is empty
        super().paintEvent(event)
        if self.count() == 0:
            painter = QtGui.QPainter(self.viewport())
            painter.save()
            col = self.palette().placeholderText().color()
            painter.setPen(col)
            fm = self.fontMetrics()
            elided_text = fm.elidedText(
                'No events', QtCore.Qt.ElideRight, self.viewport().width()
            )
            painter.drawText(self.viewport().rect(), QtCore.Qt.AlignCenter, elided_text)
            painter.restore()


class OutputHeader(QtWidgets.QWidget):

    def __init__(self, view, parent=None):
        super(OutputHeader, self).__init__(parent)
        self.view = view

        # Define widgets to display current runner data
        self._label_icon = QtWidgets.QLabel()
        self._label_index = QtWidgets.QLabel()
        self._label_name = QtWidgets.QLabel()
        self._label_description = QtWidgets.QLabel()
        self._label_update_time = QtWidgets.QLabel()
        self._label_pid = QtWidgets.QLabel()
        self._textedit_cmd = QtWidgets.QPlainTextEdit()
        self._button_copy_cmd = QtWidgets.QPushButton(
            resources.get_icon(('icons.gui', 'clipboard')), ''
        )

        # Labels styling
        self._label_icon.setFixedWidth(40)
        self._label_icon.setAlignment(QtCore.Qt.AlignCenter)
        font = self._label_index.font()
        font.setPointSize(12)
        font.setWeight(QtGui.QFont.Bold)
        self._label_name.setFont(font)
        font.setPointSize(10)
        font.setWeight(QtGui.QFont.Normal)
        self._label_description.setFont(font)
        font.setPointSize(8)
        font.setWeight(QtGui.QFont.Normal)
        self._label_update_time.setFont(font)
        self._label_update_time.setStyleSheet("QLabel { color : #aaa; }")
        self._label_index.setFont(font)
        self._label_index.setStyleSheet("QLabel { color : #aaa; }")
        self._label_index.setToolTip('Index/PID')
        self._label_pid.setFont(font)
        self._label_pid.setStyleSheet("QLabel { color : #aaa; }")
        self._textedit_cmd.setStyleSheet((
            "QPlainTextEdit { "
            "background-color: #3e4041; "
            "color: #717476; "
            "border-style: none; }"
        ))

        # Command text edit
        self._textedit_cmd.setReadOnly(True)
        self._textedit_cmd.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._textedit_cmd.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding
        )
        self._textedit_cmd.setFixedHeight(25)
        self._textedit_cmd.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Copy to clipboard button
        self._button_copy_cmd.setFixedSize(42, 28)
        self._button_copy_cmd.setToolTip('Copy command to clipboard')
        self._button_copy_cmd.setStyleSheet((
            "QPushButton { border-color: #666; }"
            "QPushButton:pressed { border-color: #999; }"
        ))

        self._button_copy_cmd.clicked.connect(self.copy_cmd_to_clipboard)

        # Setup layout
        main_lo = QtWidgets.QVBoxLayout(self)
        main_lo.setSpacing(1)
        main_lo.setContentsMargins(0, 0, 0, 0)

        # Runner data (Top part)
        runner_data_widget = QtWidgets.QWidget()
        runner_data_lo = QtWidgets.QHBoxLayout(runner_data_widget)
        runner_data_lo.setContentsMargins(0, 0, 9, 0)

        runner_data_lo.addWidget(self._label_icon)
        
        runner_name_lo = QtWidgets.QVBoxLayout()
        runner_name_lo.setSpacing(1)
        runner_name_lo.addWidget(self._label_name)
        runner_name_lo.addWidget(self._label_description)

        runner_update_lo = QtWidgets.QVBoxLayout()
        runner_update_lo.setSpacing(0)
        runner_update_lo.addWidget(self._label_pid, 0, alignment=QtCore.Qt.AlignRight)
        runner_update_lo.addWidget(self._label_update_time, 0, alignment=QtCore.Qt.AlignRight)
        
        runner_data_lo.addLayout(runner_name_lo)
        runner_data_lo.addLayout(runner_update_lo)

        main_lo.addWidget(runner_data_widget, 0)

        # Separator
        line = QtWidgets.QFrame()
        line.setGeometry(QtCore.QRect(320, 150, 118, 1))
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("QFrame { color: #555 }")

        main_lo.addWidget(line)
        
        # Runner command line (bottom part)
        runner_cmd_lo = QtWidgets.QHBoxLayout()
        runner_cmd_lo.setAlignment(QtCore.Qt.AlignHCenter)
        runner_cmd_lo.setContentsMargins(0, 0, 0, 0)
        runner_cmd_lo.setSpacing(0)
        runner_cmd_lo.addWidget(self._textedit_cmd, 0)
        runner_cmd_lo.addWidget(self._button_copy_cmd, 1)
        
        main_lo.addLayout(runner_cmd_lo)

        self.setFixedHeight(main_lo.sizeHint().height())

    def update(self):
        current_item = self.view.current_item()
        
        if current_item is None:
            self._label_update_time.clear()
        else:
            time = custom_format(
                os.path.getmtime(current_item.log_path()),
                '%d-%m-%Y, %H:%M:%S'
            )
            self._label_update_time.setText('Last update: ' + time)
            self.view._subprocess_handlers.refresh()

    def refresh(self):
        current_item = self.view.current_item()
        
        if current_item is None:
            self._label_icon.clear()
            self._label_name.clear()
            self._label_description.clear()
            self._label_update_time.clear()
            self._label_pid.clear()
            self._textedit_cmd.clear()
            self.view._subprocess_handlers.clear()
        else:
            icon = current_item.icon()
            if icon:
                item_icon = resources.get_pixmap(icon[0],icon[1])
                self._label_icon.setPixmap(item_icon.scaled(28, 28, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                self._label_icon.show()
            else:
                self._label_icon.hide()
            
            self._label_name.setText(current_item.name())
            self._label_description.setText(current_item.label())
            
            time = custom_format(
                os.path.getmtime(current_item.log_path()),
                '%d-%m-%Y, %H:%M:%S'
            )
            self._label_update_time.setText('Last modification: ' + time)
            
            self._label_pid.setText('PID: ' + str(current_item.pid()))
            self._textedit_cmd.setPlainText(current_item.command())
            
            self.view._subprocess_handlers.refresh()

    def copy_cmd_to_clipboard(self):
        cmd = self._textedit_cmd.toPlainText()
        app = QtWidgets.QApplication.instance()
        clip = app.clipboard()
        clip.setText(cmd)


class OutputHighlighter(QtGui.QSyntaxHighlighter):

    # Highlight runner handlers when detected in process log

    COLORS = {
        'ERROR': '#FF584D',
        'WARNING': '#EFDD5B',
        'INFO': '#4AA5AD',
        'SUCCESS': '#6DD86B'
    }

    def __init__(self, view, parent):
        super(OutputHighlighter, self).__init__(parent)
        self.view = view

    def highlightBlock(self, text):
        # Define text format
        text_format = QtGui.QTextCharFormat()
        text_format.setFontWeight(QtGui.QFont.Bold)

        if self.view.current_item():
            # Fetch all runner handlers
            self.patterns = [
                (QtCore.QRegularExpression(handler['pattern']), handler['handler_type'])
                for handler in self.view.current_item().handlers()
            ]

            for pattern, handler_type in self.patterns:
                # Set color according to handler type
                text_format.setForeground(QtGui.QBrush(QtGui.QColor(self.COLORS.get(handler_type)))) #TODO: use kabaret style
                # Find for matching pattern
                match = pattern.match(text)
                index = match.capturedStart()
                while index >= 0:
                    length = match.capturedLength()
                    self.setFormat(index, length, text_format)
                    match = pattern.match(text, index + length)
                    index = match.capturedStart()


class OutputTextEdit(QtWidgets.QPlainTextEdit):
    
    def __init__(self, view, parent=None):
        super(OutputTextEdit, self).__init__(parent)
        self.view = view
        self._log_mtime = 0
        
        self.setReadOnly(True)
    
    def _write(self, text):
        doc = self.document()
        cursor = QtGui.QTextCursor(doc)
        cursor.clearSelection()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ensureCursorVisible()
    
    def update(self):
        self.clear()
        
        current_item = self.view.current_item()
        if current_item is None:
            return
        
        log_path = current_item.log_path()
        if log_path is None:
            return
        
        with open(log_path, 'r') as log_file:
            log = log_file.read()
            self._write(log)
    
    def refresh(self):
        current_item = self.view.current_item()
        if current_item is None:
            return
        
        log_path = current_item.log_path()
        if log_path is None:
            return

        # Check if log file has been modified
        mtime = os.path.getmtime(log_path)
        
        if mtime > self._log_mtime:
            self.update()
            self._log_mtime = mtime


class SubprocessOutput(QtWidgets.QWidget):
    
    def __init__(self, parent, view):
        super(SubprocessOutput, self).__init__(parent)
        self.view = view
        
        self._header = OutputHeader(view)
        self._output = OutputTextEdit(view)
        self._highlighter = OutputHighlighter(view, self._output.document())
        
        self._output.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        
        vlo = QtWidgets.QVBoxLayout()
        vlo.addWidget(self._header)
        vlo.addWidget(self._output)
        vlo.setContentsMargins(0, 0, 0, 0)
        vlo.setSpacing(1)
        self.setLayout(vlo)
        
        # Set up timer to periodically update
        # running process output
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.setInterval(10)
    
    def update(self):
        self._header.refresh()
        self._output.update()
    
    def refresh(self):
        self._header.update()
        self._output.refresh()


class SubprocessListItem(QtWidgets.QTreeWidgetItem):
    
    def __init__(self, tree, process):
        super(SubprocessListItem, self).__init__(tree)
        self.tree = tree
        self.process = None
        # self.args = ()
        # self.kwargs = {}
        self._match_str = ''
        self.set_process(process)
    
    def set_process(self, process):
        self.process = process
        self._match_str = ''
        self._update()
    
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        if column == 3:
            mtime = os.path.getmtime(self.log_path())
            other_mtime = os.path.getmtime(other.log_path())
            return mtime < other_mtime
        elif column == 4:
            return self.last_run_time() < other.last_run_time()
        else:
            key1 = self.text(column)
            key2 = other.text(column)
            return natural_sort_key(key1) < natural_sort_key(key2)
    
    def _update(self):
        # Set default icon for running process
        if self.is_running():
            self.setIcon(0, resources.get_icon(('icons.libreflow', 'run')))

        # Set warning icon when an ERROR or WARNING handler is captured
        if any(handler['handler_type'] not in ['INFO', 'SUCCESS'] for handler in self.handlers_catch()):
            self.setIcon(
                0, resources.get_icon(('icons.libreflow', 'warning') if self.is_running()
                else ('icons.libreflow', 'stop'))
            )
        # Set valid icon when process is no longer running and no handlers have been captured
        elif self.is_running() is False:
            self.setIcon(0, resources.get_icon(('icons.libreflow', 'checked-symbol-colored')))
        
        self.setText(1, self.name())
        self.setText(2, self.label())

        # Last update time
        # mtime = os.path.getmtime(self.log_path())
        # self.setText(3, timeago_format(mtime))
        
        # Started time
        self.setText(3, timeago_format(self.last_run_time()))
        
        # self.setText(5, str(self.pid()))
        
        # Set foreground color according to process running status
        color = QtGui.QColor(185, 194, 200) if self.is_running() else QtGui.QColor(110, 110, 110)
        
        for i in range(self.treeWidget().columnCount()):
            self.setForeground(i, QtGui.QBrush(color))

    def id(self):
        return self.process['id']
    
    def name(self):
        return self.process['name']
    
    def version(self):
        return self.process['version']
    
    def label(self):
        return self.process['label']
    
    def icon(self):
        return self.process['icon']

    def pid(self):
        return self.process['pid']
    
    def is_running(self):
        return self.process['is_running']
    
    def log_path(self):
        return self.process['log_path']
    
    def command(self):
        return self.process['command']

    def last_run_time(self):
        return self.process['last_run_time']
    
    def handlers(self):
        return self.process['handlers']
    
    def handlers_catch(self):
        return self.process['handlers_catch']

    def matches(self, filter):
        return filter in self._match_str


class SubprocessList(QtWidgets.QTreeWidget):
    
    def __init__(self, parent, view, session):
        super(SubprocessList, self).__init__(parent)
        self.view = view
        self.session = session
        
        columns = (
            'Status', 'Application',
            'Description', #'Last update',# 'Version',
            'Started', #'PID',
        )
        self.setHeaderLabels(columns)
        
        self.itemSelectionChanged.connect(self.view.update_output)

        # Periodically update runner infos
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        
        self.setSortingEnabled(True)
        self.sortByColumn(4, QtCore.Qt.DescendingOrder)
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_popup_menu_request)

        self._popup_menu = QtWidgets.QMenu(self)

        self._filter = None
        self._rid_to_item = {}
        
        self.header().resizeSection(0, 60)
        self.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header().resizeSection(3, 100)
        self.header().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.header().setStretchLastSection(False)
    
    def set_show_running_only(self, b):
        self._show_running_only = b
        self.refresh()
    
    def refresh(self):
        #TODO: intelligent refresh: remove deleted runners, add created runners
        self.clear()
        self._rid_to_item.clear()
        for sp in self.session.cmds.SubprocessManager.list_runner_infos():
            item = SubprocessListItem(self, sp)
            self._rid_to_item[item.id()] = item
            # TODO: manage item filtering
            if self.view.show_running_only():
                item.setHidden(not item.is_running())

    def update(self):
        for sp in self.session.cmds.SubprocessManager.list_runner_infos():
            rid = sp['id']
            item = self._rid_to_item.get(rid, None)
            
            if item is None:
                # Create item for new runner instance
                item = SubprocessListItem(self, sp)
                self._rid_to_item[rid] = item
                # TODO: manage item filtering
                if self.view.show_running_only():
                    item.setHidden(not item.is_running())
            else:
                # Update info of existing runner instance
                item.set_process(sp)

    def update_runner(self, rid):
        item = self._rid_to_item[rid]
        if item is not None:
            process = self.session.cmds.SubprocessManager.get_runner_info(
                rid
            )
            item.set_process(process)
    
    def clear_completed_runners(self):
        # self.refresh()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            
            if not item.is_running():
                self.session.cmds.SubprocessManager.delete_runner_instance(
                    item.id()
                )
        
        self.refresh()
    
    def _on_popup_menu_request(self, pos):
        item = self.itemAt(pos)
        
        if item is None:
            m = self._popup_menu
            m.clear()
            m.addAction(
                QtGui.QIcon(resources.get_icon(('icons.gui', 'refresh'))),
                'Refresh',
                self.view.refresh
            )
            m.addAction(
                QtGui.QIcon(resources.get_icon(('icons.gui', 'clean'))),
                'Clean completed',
                self.view.clear_completed_runners
            )
        else:
            # item = item.job_item()
            m = self._popup_menu
            m.clear()
            if not item.is_running():
                m.addAction(
                    QtGui.QIcon(resources.get_icon(('icons.gui', 'run'))),
                    'Relaunch',
                    lambda item=item: self._launch(item)
                )
                m.addAction(
                    QtGui.QIcon(resources.get_icon(('icons.gui', 'delete'))),
                    'Delete',
                    lambda item=item: self._delete(item)
                )
            else:
                m.addAction(
                    QtGui.QIcon(resources.get_icon(('icons.gui', 'stop'))),
                    'Terminate',
                    lambda item=item: self._terminate(item)
                )

        self._popup_menu.popup(self.viewport().mapToGlobal(pos))
    
    def _launch(self, item):
        self.session.cmds.SubprocessManager.launch_runner_instance(
            item.id()
        )
        self.update_runner(item.id())
        self.view.update_output()
    
    def _terminate(self, item):
        self.session.cmds.SubprocessManager.terminate_runner_instance(
            item.id()
        )
        self.update_runner(item.id())

    def _kill(self, item):
        self.session.cmds.SubprocessManager.kill_runner_instance(
            item.id()
        )
        self.update_runner(item.id())
    
    def _delete(self, item):
        self.session.cmds.SubprocessManager.delete_runner_instance(
            item.id()
        )
        self.view.refresh()


class SubprocessView(DockedView):
    def __init__(self, *args, **kwargs):
        super(SubprocessView, self).__init__(*args, **kwargs)

    def _build(self, top_parent, top_layout, main_parent, header_parent, header_layout):
        self.splitter = QtWidgets.QSplitter(main_parent)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        
        self._subprocess_list = SubprocessList(self.splitter, self, self.session)
        self._subprocess_output = SubprocessOutput(self.splitter, self)
        self._subprocess_handlers = SubprocessHandlersList(self.splitter, self)

        self.installEventFilter(self)
        
        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        lo.addWidget(self.splitter)

        main_parent.setLayout(lo)
        
        self.view_menu.setTitle('Options')
        self.view_menu.addAction(
            QtGui.QIcon(resources.get_icon(('icons.gui', 'refresh'))),
            'Refresh',
            self.refresh
        )
        self.view_menu.addAction(
            QtGui.QIcon(resources.get_icon(('icons.gui', 'clean'))),
            'Clean completed',
            self.clear_completed_runners
        )
        self._show_running_action = self.view_menu.addAction(
            'Show running only',
            self.on_show_running_change
        )
        self._show_running_action.setCheckable(True)
        self._show_running_action.setChecked(False)
        
        self.set_view_title('Processes')

    def eventFilter(self, obj, event):
        # Set initial height for subprocess handlers
        if event.type() == QtCore.QEvent.Show:
            self.splitter.setSizes([
                self._subprocess_list.height(),
                self._subprocess_output.height(),
                50
            ])
        
        return super(SubprocessView, self).eventFilter(obj, event)

    def refresh(self):
        self.refresh_list()
        self._subprocess_output.update()

    def refresh_list(self):
        self._subprocess_list.refresh()
    
    def update_output(self):
        current_item = self.current_item()
        
        if current_item is None:
            # Clear output if no runner is selected
            self._subprocess_output.timer.stop()
            self._subprocess_output.refresh()
        else:
            # Update stopped runner only if its output
            # isn't already displayed
            self._subprocess_output.timer.stop()
            self._subprocess_handlers.clear()
            self._subprocess_output.update()
            
            if current_item.is_running():
                self._subprocess_output.timer.start()

    def current_item(self):
        selection = self._subprocess_list.selectedItems()
        if not selection:
            return None
        else:
            return selection[0]
    
    def clear_completed_runners(self):
        self._subprocess_list.clear_completed_runners()
        self._subprocess_output.update()
    
    def on_show(self):
        self.refresh_list()

    def show_running_only(self):
        return self._show_running_action.isChecked()

    def on_show_running_change(self):
        self._subprocess_list.set_show_running_only(
            self._show_running_action.isChecked()
        )

    def receive_event(self, event_type, data):
        # TODO: Manage events sent from actor
        # (e.g. when a runner is instanciated ?)
        if event_type == "focus_changed":
            # Update dock title bar background color depending on the active view status
            view_id = data["view_id"]
            self.dock_widget().setProperty(
                "current", True if view_id == self.view_id() else False
            )
            self.dock_widget().style().polish(self.dock_widget())
            self.dock_widget().update()