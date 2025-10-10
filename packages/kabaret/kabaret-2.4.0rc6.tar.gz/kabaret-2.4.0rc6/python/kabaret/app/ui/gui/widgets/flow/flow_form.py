'''


'''
import os
import math

import six
from qtpy import QtWidgets, QtGui, QtCore

from kabaret.app import resources

from .. import event_filters
from ..form_tree import FormTree
from ..editors import editor_factory
from ..widget_view import DialogView

from .flow_field import FlowField, ObjectSummary, ObjectActionsMenu, ReferencesField
from .map_field import MapField


class ErrorField(FlowField):
    '''
    Use this field to display an error instead of a relation in a flow form.
    '''
    def activated(self, col):
        pass

    def build(self):
        self.setSizeHint(1, QtCore.QSize(32, 32))

        self.setFlags(
            QtCore.Qt.ItemIsEnabled
        )

        self.setText(0, self._label)
        icon = self._get_icon(
            'exclamation-sign', resource_folder='icons.gui'
        )
        self.setIcon(0, icon)

        tree = self.treeWidget()
        w = QtWidgets.QWidget(tree)
        lo = QtWidgets.QHBoxLayout()
        lo.setContentsMargins(2, 2, 2, 2)
        w.setLayout(lo)
        self.message_label = QtWidgets.QLabel()
        self.message_label.setProperty('error', True)
        w.layout().addWidget(self.message_label)
        w.layout().addStretch(100)
        self.setItemWidget(1, w)

    def set_message(self, message):
        self.message_label.setText(message)

    def update_content(self):
        pass

    def build_children(self):
        pass

class ObjectField(FlowField):

    def activated(self, col):
        if not super(ObjectField, self).activated(col):
            # It it did not open another window:
            if col == 0 or not self.ui_config.get("expandable", True):
                self.goto()
            else:
                if not self.isExpanded():
                    self.ensure_children_built()
                    self.setExpanded(True)
                else:
                    self.setExpanded(False)

    def goto(self):
        self.treeWidget().goto(self.oid)

    def build(self):
        # we may have 0 buttons, so ensure a default minimum size:
        self.setSizeHint(1, QtCore.QSize(32, 32))

        self.setFlags(
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsDragEnabled
        )
        tree = self.treeWidget()

        self.setText(0, self._label)
        self.setIcon(0, self._get_config_icon())

        w = QtWidgets.QWidget(tree)
        lo = QtWidgets.QHBoxLayout()
        lo.setContentsMargins(2, 2, 2, 2)
        w.setLayout(lo)

        actions_menu = ObjectActionsMenu(
            self.session, w, tree.show_action_dialog, 'Flow.inline'
        )
        actions_menu.set_with_submenus(
            self.ui_config.get('action_submenus', False)
        )
        w.layout().addWidget(actions_menu)
        actions_menu.load_actions(self.oid)
        self.setFirstColumnSpanned(False)

        self._summary = ObjectSummary(self.session, w)
        self._summary.load_summary(self.oid)
        w.layout().addWidget(self._summary)

        w.layout().addStretch(100)

        self.setItemWidget(1, w)

        self.show_may_have_children()

    def update_content(self):
        self._summary.load_summary(self.oid)


class ImageSequenceViewer(QtWidgets.QLabel):

    def __init__(self, parent):
        super(ImageSequenceViewer, self).__init__(parent)
        self.label = None
        self.path = None
        self.first = None
        self.last = None
        self.fps = None
        self._freq = None
        self._actual_fps = None
        self._freq_comp = 0
        self._played_frames = 0
        self._freq = None

        self.curr = None
        self.nb_frames = None
        self.aspect_ratio = None

        self._scrubbed_start_f = None
        self._scrubbed_start_x = None

        self._px_cache = {}
        self._px_height = None

        self._is_seq = False
        self._play = False

        self._last_time = QtCore.QTime()
        self._ave_time = QtCore.QTime()

        self.no_cache_brush = QtGui.QBrush(QtGui.QColor('#440000'))
        self.curr_frame_brush = QtGui.QBrush(QtGui.QColor('#00FFFF'))

        self.setFocusPolicy(QtCore.Qt.ClickFocus)

    def clear_cache(self):
        self._px_cache.clear()

    def set_sequence(self, label, path, first, last, fps):
        label = label or os.path.basename(path).split('.', 1)[0]

        self._is_seq = None not in (first, last)

        clear_cache = False
        if self.label != label:
            self.label = label
            clear_cache = True

        if self.path != path:
            self.path = path
            clear_cache = True

        if self.first != first:
            self.first = first
            clear_cache = True

        if self.last != last:
            self.last = last
            clear_cache = True

        if self.fps != fps:
            self.fps = fps
            if self.fps:
                self._freq = 1000.0 / self.fps
            clear_cache = True

        if clear_cache:
            self.clear_cache()
            if self._is_seq:
                self.nb_frames = (self.last - self.first)
                curr = self.first + self.nb_frames / 2
            else:
                self.nb_frames = 0
                curr = None
        else:
            curr = self.curr

        self.curr = None
        self.set_current_frame(curr)

    def set_current_frame(self, f):
        if not self.path:
            return
        if self._is_seq:
            f = min(self.last, max(self.first, f))
            if f == self.curr:
                return
            self.curr = f
        self._update_image()

    def _update_image(self):
        if self.path is None:
            raise ValueError('Sequence Path not set !')

        try:
            px = self._px_cache[self.curr]
        except KeyError:
            if not self._is_seq:
                p = self.path
            else:
                p = self.path % (self.curr,)
            px = QtGui.QPixmap(p)
            if px.isNull():
                h = self.height()
                w = h*(self.aspect_ratio or 1)
                px = QtGui.QPixmap(w, h)
                px.fill()
            else:
                h = self.height()
                # pxh = px.height()
                height = h  # min(h, pxh)
                px = px.scaledToHeight(height)
                self._last_width = px.width()
                self._px_cache[self.curr] = px
            
                if self.aspect_ratio is None:
                    self.aspect_ratio = px.width() / (px.height() * 1.0)
        self.setPixmap(px)

    def toggle_play(self):
        self._nb_avr_frames = 2
        self._actual_fps = None
        self._played_frames = 0
        if not self._play:
            self._last_time.start()
            self._ave_time.start()
            self._play = True
            self._play_step()
        else:
            self._play = False

    def _play_step(self):
        if not self._is_seq:
            self.set_current_frame(None)
            return

        elapsed = self._last_time.restart() * 1.0
        self._played_frames += 1
        if self._played_frames == self._nb_avr_frames:
            d = self._ave_time.restart() * 1.0
            self._actual_fps = 1.0 / ((d / self._nb_avr_frames) / 1000.0)
            self._played_frames = 0
            self._nb_avr_frames = min(self.fps, self._nb_avr_frames * 2)

        if self.curr == self.last:
            f = self.first
        else:
            f = self.curr + 1
        self.set_current_frame(f)
        if self._play:
            if elapsed / self._freq > 2:
                d = 0
                self._nb_avr_frames = 2
            else:
                late = elapsed - self._freq
                self._freq_comp += math.copysign(.5, late)
                d = max(0, self._freq - self._freq_comp)
            QtCore.QTimer.singleShot(max(0, d), self._play_step)

    def resizeEvent(self, e):
        self.clear_cache()
        f = self.curr
        if not self._is_seq or f is not None:
            self.curr = None
            self.set_current_frame(f)

    def keyPressEvent(self, e):
        k = e.key()
        if k == QtCore.Qt.Key_Left:
            self._play = False
            f = self.curr
            self.set_current_frame(f - 1)

        elif k == QtCore.Qt.Key_Right:
            self._play = False
            f = self.curr
            self.set_current_frame(f + 1)

        elif k == QtCore.Qt.Key_Space:
            self.toggle_play()

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self._scrubbed_start_f = None
            self._scrubbed_start_x = None
            e.accept()
        else:
            super(ImageSequenceViewer, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if e.buttons() & QtCore.Qt.LeftButton:
            if self._scrubbed_start_f is None:
                self._scrubbed_start_f = self.curr
                self._scrubbed_start_x = e.pos().x()
            else:
                self._play = False
                new_frame = self._scrubbed_start_f + (
                    e.pos().x() -
                    self._scrubbed_start_x
                ) / 1
                self.set_current_frame(new_frame)
            e.accept()
        else:
            super(ImageSequenceViewer, self).mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self._scrubbed_start_f = None
            self._scrubbed_start_x = None
            e.accept()
        else:
            super(ImageSequenceViewer, self).mouseReleaseEvent(e)

    def paintEvent(self, e):
        super(ImageSequenceViewer, self).paintEvent(e)

        curr = self.curr
        is_seq = self._is_seq

        p = QtGui.QPainter(self)

        p.setBrush(self.curr_frame_brush)
        p.setPen(QtCore.Qt.black)
        x = 20
        y = 30
        if is_seq:
            fps = ''
            if self._actual_fps:
                fps = ' (%i fps) ' % (self._actual_fps,)
                if abs(self._actual_fps - self.fps) > 1:
                    p.setPen(QtCore.Qt.red)
            t = '%04i/%04i/%04i - %s%s' % (
                self.first, curr, self.last, self.label, fps
            )
        else:
            t = self.label

        p.drawText(x, y, t)
        p.setPen(QtCore.Qt.white)
        p.drawText(x - 1, y - 1, t)

        if not is_seq:
            return

        nb = self.nb_frames
        cr = self.contentsRect()
        fw = cr.width() / (nb * 1.0)
        h = cr.height()

        p.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        p.setBrush(self.no_cache_brush)
        fr = QtCore.QRectF(0, h - 8, fw, 4)
        for i, f in enumerate(range(self.first, self.last + 1)):
            fr.moveLeft(i * fw)
            if f == curr:
                p.setBrush(self.curr_frame_brush)
                p.drawRect(fr)
                p.setBrush(self.no_cache_brush)
                continue

            try:
                self._px_cache[f]
            except KeyError:
                p.drawRect(fr)


class ObjectPreviewFied(FlowField):

    def activated(self, col):
        self.treeWidget().goto(self.oid)

    def build(self):
        self.setFlags(
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsDragEnabled
        )
        tree = self.treeWidget()

        self.setText(0, self._label)

        w = QtWidgets.QWidget(tree)

        lo = QtWidgets.QHBoxLayout()
        lo.setContentsMargins(2, 2, 2, 2)
        w.setLayout(lo)

        self._thumbnail = ImageSequenceViewer(w)
        self._resizer = event_filters.MouseResizer(
            self._thumbnail, self.update_height,
            aspect_ratio=None,  # will be set in update()
        )
        self._resizer.min_h = 50
        self._resizer.propagate_events = False
        self._thumbnail.installEventFilter(self._resizer)
        # ! This connection must not be done in the ImageSequenceViewer
        # or the slot is never called !
        self._thumbnail.destroyed.connect(self._on_thumbnail_destroyed)

        lo.addWidget(self._thumbnail, 100)

        self.actions_menu = ObjectActionsMenu(
            self.session, w, tree.show_action_dialog, 'Flow.inline'
        )
        self.actions_menu.set_with_submenus(
            self.ui_config.get('action_submenus', False)
        )
        w.layout().addWidget(self.actions_menu)

        self.summary = ObjectSummary(self.session, w, self._get_icon_for)
        w.layout().addWidget(self.summary)

        w.layout().addStretch()

        self.setItemWidget(1, w)

        self.update_content()

    def _on_thumbnail_destroyed(self):
        self._thumbnail.clear_cache()

    def update_content(self):
        info = self.session.cmds.Flow.get_thumbnail_info(self.oid)
        if info.get('is_sequence'):
            label = info.get('label')
            path = info.get('path')
            first = info.get('first')
            last = info.get('last')
            fps = info.get('fps')
            default_height = info.get('default_height', 100)

        elif info.get('is_image'):
            label = info.get('label')
            path = info.get('path')
            first, last, fps = None, None, None
            default_height = info.get('default_height', 100)

        else:
            label = info.get('label')
            folder = info.get('folder')
            name = info.get('name')
            path = resources.get(folder, name)
            if path is None:
                path = resources.get('icons.gui', 'remove-symbol')
            first, last, fps = None, None, None
            default_height = info.get('default_height', 100)

        self._thumbnail.set_sequence(label, path, first, last, fps)
        if self._resizer.aspect_ratio is None:
            self._resizer.aspect_ratio = self._thumbnail.aspect_ratio
            self._resizer.apply_resize(default_height, default_height, 0, 0)

        self.actions_menu.load_actions(self.oid)

        self.summary.load_summary(self.oid)


class ParentField(FlowField):

    def get_icon(self):
        # TODO: use a cmd to get the actual icon ?
        return self._get_icon('parent')

    def goto(self):
        self.treeWidget().goto(self.oid)

    def build(self):
        self.setFlags(QtCore.Qt.ItemIsEnabled)  # not selectable

        tree = self.treeWidget()

        w = QtWidgets.QWidget(tree)
        lo = QtWidgets.QHBoxLayout()
        lo.setContentsMargins(2, 2, 2, 2)
        w.setLayout(lo)

        b = QtWidgets.QPushButton('Go back to %s' % (self._label,), w)
        b.clicked.connect(self.goto)
        icon = self.get_icon()
        if icon is not None:
            b.setIcon(icon)
        w.layout().addWidget(b, 100)

        if 0:
            # this is too many action everywhere, let's light it up.
            actions_menu = ObjectActionsMenu(
                self.session, w, tree.show_action_dialog, 'Flow.inline'
            )
            actions_menu.set_with_submenus(
                self.ui_config.get('action_submenus', False)
            )
            w.layout().addWidget(actions_menu)
            actions_menu.load_actions(self.oid)

        if 0:
            # Until the summary gets touch reactive, let's not
            # show it too much :p
            summary = ObjectSummary(self.session, w)
            summary.load_summary(self.oid)
            w.layout().addWidget(summary)

        w.layout().addStretch(100)

        self.setItemWidget(1, w)


class ConnectionButton(QtWidgets.QPushButton):

    def __init__(self, session, oid, parent):
        super(ConnectionButton, self).__init__('???', parent)
        self.session = session
        self.oid = oid
        self._editable = True
        self.setAcceptDrops(True)

    def set_editable(self, b):
        self._editable = b

    def dragEnterEvent(self, event):
        if not self._editable:
            return 
        if self.session.cmds.Flow.can_handle_mime_formats(
            event.mimeData().formats()
        ):
            event.acceptProposedAction()
        else:
            return super(ConnectionButton, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if not self._editable:
            return 
        if self.session.cmds.Flow.can_handle_mime_formats(
            event.mimeData().formats()
        ):
            event.acceptProposedAction()
        else:
            return super(ConnectionButton, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if not self._editable:
            return 
        mime_data = event.mimeData()
        md = {}
        for format in mime_data.formats():
            md[format] = mime_data.data(format).data()
        oids, urls = self.session.cmds.Flow.from_mime_data(md)

        if not oids and not urls:
            return False    # let the event propagate up

        self.session.cmds.Flow.connect(self.oid, oids, urls)

class ConnectionField(ObjectField):

    def update_content(self):
        expanded = self.isExpanded()

        source_icon = None
        try:
            self.source_oid, source_display, source_icon = self.session.cmds.Flow.get_connection(
                self.oid
            )
        except Exception as err:
            source_display = 'ERROR: %s' % (err,)
        else:
            if source_display is None:
                source_display = '<Not Set>'
        source_icon = source_icon or 'ref'

        self.setIcon(0, self._get_icon(source_icon))
        self.b.setText(source_display)

        if expanded:
            self.delete_all_children()
            self.ensure_children_built()
            self.setExpanded(True)
        self._summary.load_summary(self.oid)

    def build(self):
        # we may have 0 buttons, so ensure a default minimum size:
        self.setSizeHint(1, QtCore.QSize(20, 20))

        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        tree = self.treeWidget()

        self.setText(0, self._label)

        w = QtWidgets.QWidget(tree)
        lo = QtWidgets.QHBoxLayout()
        lo.setContentsMargins(2, 2, 2, 2)
        w.setLayout(lo)

        #b = QtWidgets.QPushButton(source_display, w)
        self.b = ConnectionButton(self.session, self.oid, w)
        self.b.set_editable(self.ui_config.get('editable', True))
        self.b.clicked.connect(self.goto_ref)
        icon = self._get_icon('ref')
        if icon is not None:
            self.b.setIcon(icon)
        w.layout().addWidget(self.b)

        actions_menu = ObjectActionsMenu(
            self.session, w, tree.show_action_dialog, 'Flow.inline'
        )
        actions_menu.set_with_submenus(
            self.ui_config.get('action_submenus', False)
        )
        w.layout().addWidget(actions_menu)
        actions_menu.load_actions(self.oid)

        self._summary = ObjectSummary(self.session, w)
        self._summary.load_summary(self.oid)
        w.layout().addWidget(self._summary)

        w.layout().addStretch(100)

        self.setItemWidget(1, w)

        self.update_content()

    def goto(self):
        self.goto_ref()

    def goto_ref(self):
        if self.source_oid is not None:
            self.treeWidget().goto(self.source_oid)

    def build_children(self):
        if self.source_oid is not None:
            tree = self.treeWidget()
            tree.build_children(self, self.source_oid)

class ActionField(FlowField):

    def show_action_dialog(self):
        self.treeWidget().show_action_dialog(self.oid)

    def build(self):
        self.setFlags(QtCore.Qt.ItemIsEnabled)  # not selectable

        tree = self.treeWidget()

        # self.setText(0, '   ')
        # self.setIcon(0, self._get_config_icon())

        w = QtWidgets.QWidget(tree)
        lo = QtWidgets.QHBoxLayout()
        lo.setContentsMargins(2, 2, 2, 2)
        w.setLayout(lo)

        b = QtWidgets.QPushButton('%s' % (self._label,), w)
        b.clicked.connect(self.show_action_dialog)
        icon = self._get_config_icon()
        if icon is not None:
            b.setIcon(icon)
        w.layout().addWidget(b, 100)

        actions_menu = ObjectActionsMenu(
            self.session, w, tree.show_action_dialog, 'Flow.inline'
        )
        actions_menu.set_with_submenus(
            self.ui_config.get('action_submenus', False)
        )
        w.layout().addWidget(actions_menu)
        actions_menu.load_actions(self.oid)

        summary = ObjectSummary(self.session, w)
        summary.load_summary(self.oid)
        w.layout().addWidget(summary)

        w.layout().addStretch(100)

        self.setItemWidget(1, w)

    def build_children(self):
        # no child browsing on actions.
        return


class ParamField(FlowField):

    def __init__(self, parent, session, oid, ui_config=None):
        self._editor = None
        super(ParamField, self).__init__(parent, session, oid, ui_config)

    def _get_value_and_choices(self):
        value = self._get_value()
        choices = self.session.cmds.Flow.get_value_choices(self.oid)
        return value, choices

    def _get_value(self):
        return self.session.cmds.Flow.get_value(self.oid)

    def _set_value(self, new_value):
        self.session.cmds.Flow.set_value(
            self.oid, new_value
        )
        self.update_height(self._editor)

    def set_read_only(self):
        self._editor.configure(self._get_value, None)

    def build(self):
        self.setFlags(QtCore.Qt.ItemIsEnabled)  # not selectable

        tree = self.treeWidget()

        w = QtWidgets.QWidget(tree)
        resizer = event_filters.MouseResizer(
            w, self.update_height, horizontal=False)
        w.installEventFilter(resizer)

        lo = QtWidgets.QHBoxLayout()
        w.setLayout(lo)

        editor_type = self.ui_config.get('editor_type', None)
        self._editor = editor_factory().create(
            w, editor_type, self.ui_config
        )

        getter = self._get_value
        if self._editor.needs_choices():
            getter = self._get_value_and_choices
        self._editor.configure(getter, self._set_value, self._get_icon_for)

        self._editor.set_editable(self.ui_config.get('editable', True))

        self._editor.setToolTip(self.ui_config.get('tooltip', None))

        w.layout().addWidget(self._editor, stretch=100)

        actions_menu = ObjectActionsMenu(
            self.session, w, tree.show_action_dialog, 'Flow.inline'
        )
        actions_menu.set_with_submenus(
            self.ui_config.get('action_submenus', False)
        )
        w.layout().addWidget(actions_menu)
        w.layout().addStretch()
        actions_menu.load_actions(self.oid)

        if self._label:
            lo.setContentsMargins(2, 4, 2, 4)
            self.setText(0, self._label)
            self.setIcon(0, self._get_config_icon())
            self.setItemWidget(1, w)
        else:
            self.setText(0, '')
            self.setIcon(0, QtGui.QIcon())
            self.setItemWidget(0, w)

        self._editor.update()

    def update_content(self):
        self._editor.update()
        self.update_height(self._editor)

    def apply_edit(self):
        if self._editor.is_edited():
            self._editor.apply()


class ActionButtonsField(FlowField):

    def build(self):
        self.setFlags(QtCore.Qt.ItemIsEnabled)  # not selectable

        tree = self.treeWidget()

        w = QtWidgets.QWidget(tree)
        lo = QtWidgets.QHBoxLayout()
        lo.setContentsMargins(2, 2, 2, 2)
        w.setLayout(lo)

        # build new buttons
        buttons = self.session.cmds.Flow.get_action_buttons(self.oid)
        for button in buttons:
            b = QtWidgets.QPushButton(button.title(), w)
            b.clicked.connect(
                lambda checked=None, b=button: self._on_button(b)
            )
            icon = self._get_icon_for(button)
            if icon is not None:
                b.setIcon(icon)
            lo.addWidget(b)

        # lo.addStretch(100)

        self.setItemWidget(1, w)

    def _on_button(self, button):
        self.treeWidget().run_action(self.oid, button)


class GroupField(FlowField):

    _DEFAULT_EXPANDED_STATE = False

    def __init__(self, parent, label):
        super(GroupField, self).__init__(
            parent, session=None, oid=label, ui_config={})

    def _pref_id(self):
        '''Overrides FromField._pref_id to omit hierachy (used by auto_expand())'''
        return 'Group:' + self._label

    def activated(self, col):
        if not self.isExpanded():
            self.setExpanded(True)
        else:
            self.setExpanded(False)

    def build_children(self):
        # we must not build children for Groups
        return

    def build(self):

        tree = self.treeWidget()

        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.setFirstColumnSpanned(True)

        label = QtWidgets.QLabel(tree)
        label.setText(self._label)
        label.setStyleSheet('border: 1px ; padding: 5px; ')
        self.setItemWidget(0, label)

    def _dispatch_touch_event(self, oid):
        for i in range(self.childCount()):
            c = self.child(i)
            handled = c.on_touch_event(oid)
            if handled:
                return True
        return False


class FlowForm(FormTree):

    def __init__(self, page, parent):
        super(FlowForm, self).__init__(parent)
        self.page = page
        self._config = dict(
            show_hidden_relations=False,
            show_protected_relations=False,
            show_reference_relations=False,
            group_relations=True,
        )

        self.setDragEnabled(True)
        self._builders = []
        self._build_timer = QtCore.QTimer()
        self._build_timer.setSingleShot(True)
        self._build_timer.timeout.connect(self._build_step)

    def configure(
        self,
        show_hidden_relations=None, show_protected_relations=None,
        show_references_relation=None, group_relations=None, **kwargs
    ):
        if show_hidden_relations is not None:
            self._config['show_hidden_relations'] = show_hidden_relations
        if show_protected_relations is not None:
            self._config['show_protected_relations'] = show_protected_relations
        if group_relations is not None:
            self._config['group_relations'] = group_relations
        if show_references_relation is not None:
            self._config['show_reference_relations'] = show_references_relation
        self._config.update(kwargs)
        self.page.refresh()

    def config(self):
        return self._config.copy()

    def build_children(self, parent_item, oid=None):
        oid = oid or parent_item.oid
        self._build(oid, parent_item)

    def build_roots(self, oid):
        self._build(oid, self)

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction

    def mimeData(self, items):
        mime_data = super(FormTree, self).mimeData(items)

        oids = [item.oid for item in items]
        md = self.page.session.cmds.Flow.to_mime_data(oids)
        for data_type, data in six.iteritems(md):
            mime_data.setData(data_type, data)

        return mime_data

    def _build_generator(self, oid, parent_item):
        session = self.page.session

        relations, mapped_names = session.cmds.Flow.ls(
            oid,
            show_hidden=self._config['show_hidden_relations'],
            show_protected=self._config['show_protected_relations'],
            context='Flow.details'
        )

        last_group = None
        group_items = {None: parent_item}
        create_groups = self._config.get('group_relations', False)

        # Process Parent first so that layout is built top to bottom
        if oid == self.page.current_oid():
            for (
                related_oid, relation_name, relation_type,
                is_action, is_map, ui_config,
            ) in relations:
                if relation_type == 'Parent':
                    related_oid = oid + '/' + relation_name
                    ParentField(parent_item, session, related_oid, ui_config)

        for (
            related_oid, relation_name, relation_type,
            is_action, is_map, ui_config,
        ) in relations:
            if create_groups:
                group = ui_config.get('group')
                if group != last_group:
                    last_group = group
                    try:
                        group_item = group_items[group]
                    except KeyError:
                        group_item = GroupField(group_items[None], label=group)
                        group_items[group] = group_item
                    parent_item = group_item

            if is_action:
                ActionField(parent_item, session, related_oid, ui_config)

            elif is_map:
                MapField(parent_item, session, related_oid, ui_config)

            elif relation_type in ('Param', 'Computed'):
                field = ParamField(parent_item, session,
                                   related_oid, ui_config)
                if relation_type == 'Computed':
                    field.set_read_only()
                field.update_content()

            elif relation_type == 'Child':
                ObjectField(parent_item, session, related_oid, ui_config)

            elif relation_type == 'Relative':
                # cmds.Flow.LS only lists Relative fields when the relation
                # could not be resolved. Let's show it as an error:
                field = ErrorField(parent_item, session, related_oid, ui_config)
                field.set_message(
                    'Invalid oid for Relative "{}": {}'.format(
                        relation_name,
                        related_oid
                    )
                )
                
            elif relation_type == 'Parent':
                pass

            elif relation_type == 'Connection':
                ConnectionField(parent_item, session, related_oid, ui_config)
            else:
                raise ValueError(
                    'Unsupported relation %r under %r' % (relation_type, oid)
                )

            # update gui at each child creation
            yield

        # Return to top level parent for further items:
        parent_item = group_items[None]

        is_action = session.cmds.Flow.is_action(oid)
        if is_action:
            ActionButtonsField(parent_item, session, oid)
            self.page.view.fitSize()

        if session.cmds.Flow.is_map(oid):
            # MappedItemsFied(parent_item, session, oid, {})
            mapped_oids = session.cmds.Flow.get_mapped_oids(oid)
            for mapped_oid in mapped_oids:
                ObjectPreviewFied(parent_item, session, mapped_oid, {})

        if self._config['show_reference_relations']:
            ReferencesField(parent_item, session.cmds.Flow.refs(
                oid), self.goto_connected, self.goto)

    def _build_step(self):
        if self._builders:
            try:
                next(self._builders[-1])
            except StopIteration:
                self._builders.pop(-1)
            self._build_timer.start(6)
            return
        
        # Move DialogView to center when build is complete
        if isinstance(self.page.parent(), DialogView):
            self.page.parent().moveToCenter()

    def _build(self, oid, parent_item):
        if self._build_timer.isActive():
            self._build_timer.stop()
        if parent_item is self:
            self._builders = []
        self._builders.append(self._build_generator(oid, parent_item))
        self._build_timer.start(3)

    def open(self, oid):
        self.page.open(oid)

    def goto(self, oid):
        self.page.goto(oid)

    def goto_connected(self, oid):
        self.page.goto_connected(oid)

    def show_action_dialog(self, action_oid):
        self.page.show_action_dialog(action_oid)

    def run_action(self, action_oid, button):
        self.apply_all_edits()
        self.page.run_action(action_oid, button)
    
    def content_size(self):
        height = 0
        width = 0

        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)
            width = width + self.columnWidth(i)
        for i in range(self.invisibleRootItem().childCount()):
            child = self.invisibleRootItem().child(i)
            widget = self.itemWidget(child, 0) or self.itemWidget(child, 1)
            if widget:
                widget.update()
                for j in range(child.childCount()):
                    height = height + self.visualItemRect(child.child(j)).height()
                height = height + widget.frameGeometry().height()
                width = max(width, widget.sizeHint().width())
        
        return (width * 1.1, height * 1.1)
