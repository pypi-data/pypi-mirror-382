import os
import logging
import subprocess
from collections import OrderedDict

from kabaret.flow import (
    values,
    Object, ThumbnailInfo, Map, Action, ConnectAction,
    ChoiceValueSetAction, ChoiceValueSelectAction,
    Child, Parent, Computed, Connection,
    Param, IntParam, BoolParam, HashParam
)

#-------------------------------- ACTIONS


class ExploreAction(Action):

    SHOW_IN_PARENT_INLINE = False
    ICON = 'explorer'


class TextEditActionOptions(Object):

    those = Param()
    are = Param()
    grouped = Param()
    action = Param()
    params = Param()


class TextEditAction(Action):

    ICON = 'notepad'

    options = Child(TextEditActionOptions)


class MayaEditAction(Action):

    ICON = 'maya'

    _parent = Parent()

    def get_context_oid(self):
        return self._parent.get_maya_context_oid()

    def needs_dialog(self):
        return False

    def run(self, button):
        maya = 'D:/Autodesk/Maya2015/bin/maya.exe'
        env = os.environ.copy()

        # The idea is to have the code configuring maya's embedded kabaret
        # somewhere inside you studio.
        # Here we have:
        #   dev_studio.flow.demo_project.maya_startup
        # It contains a ultra simple userSetup.py that calls something like
        #   dev_studio.flow.demo_project.maya_startup.install()
        # which in turn does all you want.

        # The best way to have you studio inside maya is
        # a shared install (It avoid installing it inside maya on
        # every workstation)
        # But beware of your .pyc files ! If your python is not the
        # same as Mayapy you should have a separated installation
        # for import made from inside maya.
        #
        # An easy way to deal with this is to set a studio env var like
        #   os.environ["MY_STUDIO_PYTHONDIR"] = "path/to/maya_pyton_libs"
        # And use this in maya's userSetup.py to extend sys.path and import
        # your studio.

        # For this demo, I assume the pyc are compatible (which is BAAAAA
        # AAAAAD !) and will use the current kabaret and dev_studio path:
        import kabaret
        env['KABARET_INSTALL'] = os.path.dirname(
            os.path.dirname(os.path.abspath(kabaret.__file__))
        )

        import dev_studio
        env['DEV_STUDIO_INSTALL'] = os.path.dirname(
            os.path.dirname(os.path.abspath(dev_studio.__file__))
        )

        # # In order to start a Kabaret Session for this project, maya code
        # # will need to know the cluster connection arguments.
        # # Most of the time, you'd better get them from a function in your
        # # studio. But for this demo we use command line args so I'll just
        # # use env to pass the info to maya:
        # host, port, cluster_name = self.root().session().cmds.Cluster.get_connection_info()
        # env['KABARET_HOST'] = host
        # env['KABARET_PORT'] = port
        # env['KABARET_CLUSTER_NAME'] = cluster_name

        # The Context view will load the oid defined in this env var:
        env['KABARET_CONTEXT_OID'] = str(self.get_context_oid())

        # Use PYTHONPATH to make maya exec our userSetup.py at startup:
        from . import maya_startup
        userSetup_dir = os.path.dirname(maya_startup.__file__)
        PYTHONPATH = os.environ.get('PYTHONPATH', '')
        env['PYTHONPATH'] = userSetup_dir + ';' + PYTHONPATH

        # Obviously the action should open a file :p
        # Adding a scene = Parent() relation would let you do something like:
        #   scene_filename = self.scene.get_filename()
        #   command_args = [maya, scene_filename]
        # But I dont deal with filename in this demo (not yet at least ^.^)
        # So:
        command_args = [maya]

        # Here you go !
        popen = subprocess.Popen(command_args, env=env)


class SetWAIT(ChoiceValueSetAction):
    ICON = ('icons.status', 'WAIT')
    VALUE_TO_SET = 'WAIT'


class SetWIP(ChoiceValueSetAction):
    ICON = ('icons.status', 'WIP')
    VALUE_TO_SET = 'WIP'


class SetRVW(ChoiceValueSetAction):
    ICON = ('icons.status', 'RVW')
    VALUE_TO_SET = 'RVW'


class SetRTK(ChoiceValueSetAction):
    ICON = ('icons.status', 'RTK')
    VALUE_TO_SET = 'RTK'


class SetDONE(ChoiceValueSetAction):
    ICON = ('icons.status', 'DONE')
    VALUE_TO_SET = 'DONE'


class StatusValue(values.ChoiceValue):

    STRICT_CHOICES = True
    CHOICES = ['NYS', 'WAIT', 'WIP', 'RVW', 'RTK', 'DONE', 'OOP']

    wait = Child(SetWAIT)
    wip = Child(SetWIP)
    rvw = Child(SetRVW)
    rtk = Child(SetRTK)
    done = Child(SetDONE)
    other = Child(ChoiceValueSelectAction)


class Status(Param):

    def __init__(self, default_value='NYS'):
        super(Status, self).__init__(default_value, StatusValue)


# ----------------------------------------- ASSET

class Asset(Object):

    ICON = 'asset'

    some_param = Param('some value...')


class CreateAssetAction(Action):

    _map = Parent()

    asset_preffix = Param('MyAsset')

    def get_buttons(self):
        return ['Create']

    def run(self, button):
        preffix = self.asset_preffix.get()
        asset_name = '%s_%03i' % (preffix, len(self._map),)
        self._map.add(asset_name)
        self._map.touch()


class Assets(Map):

    def mapped_type(cls):
        return Asset

    create_asset = Child(CreateAssetAction)

# ----------------------------------------- BANK


class Bank(Object):

    ICON = 'bank'

    assets = Child(Assets)


class CreateBankAction(Action):

    _map = Parent()

    bank_name = Param('Bank')

    def get_buttons(self):
        return ['Create']

    def run(self, button):
        self._map.add(self.bank_name.get())
        self._map.touch()


class Banks(Map):

    ICON = 'bank'

    # _items = HashParam(
    #     OrderedDict([
    #         ('Bank', ' my_studio.flow.test_project.Bank'),
    #     ])
    # )

    create_bank = Child(CreateBankAction)

    @classmethod
    def mapped_type(cls):
        return Bank

# --------------------------------------- SHOT


class Montage(Object):

    index = IntParam(0)
    first = IntParam(1).watched()
    fade_in = IntParam(0)
    last = IntParam(100).watched()
    fade_out = IntParam(0)
    nb_frames = Computed()

    def child_value_changed(self, child_value):
        if child_value in (self.first, self.last):
            self.nb_frames.touch()

    def compute_child_value(self, child_value):
        if child_value == self.nb_frames:
            self.nb_frames.set(
                self.last.get() - self.first.get() + 1
            )


class CastItem(Object):

    asset = Connection(Asset)
    index = IntParam(0)

    def asset_name(self):
        asset = self.asset.get()
        if asset is None:
            return None
        return asset.name()


class TestMultipleConnectActions(ConnectAction):

    casting = Parent()

    def accept_label(self, objects, urls):
        return "This does nothing"

    def run(self, objects, urls):
        logging.getLogger('kabaret.demo').info('Doing nothing with %r and %r' % (objects, urls))


class CastingAssetConnectAction(ConnectAction):

    casting = Parent()

    def accept_label(self, objects, urls):
        logging.getLogger('kabaret.demo').info("DROP!")
        if urls:
            return None
        for o in objects:
            if not isinstance(o, Asset):
                return None
        return "Add %i Assets to the Casting" % (len(objects,))

    def run(self, objects, urls):
        for asset in objects:
            ci = self.casting.add_asset(asset)
        self.casting.touch()


class Casting(Map):

    _drop_asset = Child(CastingAssetConnectAction)
    drop_something = Child(TestMultipleConnectActions)

    @classmethod
    def mapped_type(cls):
        return CastItem

    def add_asset(self, asset):
        used_indexes = set()
        for ci in self.mapped_items():
            c_asset = ci.asset.get()
            if c_asset is asset:
                used_indexes.add(ci.index.get())
        if not used_indexes:
            index = 1
        else:
            index = None
            for i in range(min(used_indexes), max(used_indexes)):
                if i not in used_indexes:
                    index = i
            if index is None:
                index = max(used_indexes) + 1
        name = asset.name() + ('_id%03i' % index)
        ci = self.add(name)
        ci.asset.set(asset)
        ci.index.set(index)

        return ci


class ShotObject(Object):

    def summary(self):
        return (
            '<font color=#440000><b>'
            '| File does not exists | Not Yet Reversionned |'
            '</b></font>'
        )


class AddToReversionAction(Action):
    SHOW_IN_PARENT_INLINE = False


class ProtectedAction(Action):
    SHOW_IN_PARENT_INLINE = False


class FileHistoryMap(Map):
    pass


class PublishAction(Action):
    ICON = ('icons.gui', 'share-option')


class InitAction(Action):
    pass


class DummyMayaAction(Action):

    pass


class MayaContextToolsGroup(Object):

    sub_tool01 = Child(DummyMayaAction)
    sub_tool02 = Child(DummyMayaAction)
    sub_tool03 = Child(DummyMayaAction)


class MayaContextTools(Object):

    group01 = Child(MayaContextToolsGroup)
    tool01 = Child(DummyMayaAction)
    tool02 = Child(DummyMayaAction)
    group02 = Child(MayaContextToolsGroup)
    tool03 = Child(DummyMayaAction)


class ShotTask(ShotObject):

    filename = Computed().ui(group='file')
    exists = Computed().ui(editor='bool').ui(group='file')
    explore = Child(ExploreAction).ui(group='file')

    is_versionned = BoolParam().ui(group='cvs')
    activate_versionning = Child(AddToReversionAction).ui(group='cvs')
    locked_by = Computed().ui(group='cvs')
    steal_work = Child(ProtectedAction).ui(group='cvs')
    trash_work = Child(ProtectedAction).ui(group='cvs')
    history = Child(FileHistoryMap).ui(group='cvs')

    publish = Child(PublishAction).ui(group='cvs')

    edit = Child(TextEditAction).ui(group='work')
    initialize = Child(InitAction).ui(group='work')

    open = Child(MayaEditAction).ui(group='work')
    _maya_context_tools = Child(MayaContextTools)

    @classmethod
    def get_source_display(self, oid):
        shot_oid, task = oid.rsplit('/', 1)
        return (
            Shot.get_source_display(shot_oid)
            +
            ' -> ' + task
        )

    def compute_child_value(self, child_value):
        child_value.set({
            self.filename: 'path/to/filename.ext',
            self.exists: False,
            self.is_versionned: False,
            self.locked_by: '-?-',
        }[child_value])

    def get_maya_context_oid(self):
        return self._maya_context_tools.oid()


class Anim(ShotObject):

    ICON = 'maya'


class Lighting(ShotObject):

    ICON = 'alembic'


class Comp(ShotObject):

    ICON = 'natron'


class SomeAction(Action):

    ICON = 'shot'

    def needs_dialog(self):
        return False

    def run(self, button):
        logging.getLogger('kabaret.demo').info('ACTION: ' + self.oid())


class DemoShotThumbnail(ThumbnailInfo):
    '''
    This class generates different thumbnail for demo purpose
    '''

    _RESOURCE = 'shot'
    _IMAGE = 'E:/tmp/Computer-Guy-Facepalm.jpg'

    _shot = Parent()

    def shot_num(self):
        return int(self._shot.name()[-1])

    def is_resource(self):
        return not self.shot_num() % 3

    def get_resource(self):
        return self._RESOURCE

    def is_image(self):
        return not (self.shot_num() - 1) % 3

    def is_sequence(self):
        return not (self.shot_num() - 2) % 3

    def get_label(self):
        return None

    def get_path(self):
        if self.is_sequence():
            p = 'E:/tmp/TEST_SEQ/HD_1420x594/M2_S2210_P0100-anim_blasts.%04i.jpg'
            p = 'E:/tmp/TEST_SEQ/LD_355x149/seq_ld.%04i.jpg'
            p = 'M:/KABARET_PROJECTS/MINUS/SYSTEM/RVS/REPO/films/M2/S2210/P0100/blast/LastBlast=M2_S2210_P0100-Animation-Blast/M2_S2210_P0100-anim_blasts.%04i.png'
            return p
        return self._IMAGE

    def get_default_height(self):
        return 200

    def get_first_last_fps(self):
        if self.is_sequence():
            return 1001, 1179, 24
        return None, None, None


class Shot(Object):

    ICON = 'shot'

    _thumbnail = Child(DemoShotThumbnail)

    status = Status().watched().ui(group='Prod')
    montage = Child(Montage).ui(group='Prod')

    film = Parent(2)

    casting = Child(Casting).ui(group='Prod')
    animatic = Child(ShotTask).ui(group='Tasks')
    sound = Child(ShotTask).ui(group='Tasks')
    anim = Child(ShotTask).ui(group='Tasks')
    lighting = Child(ShotTask).ui(group='Tasks')
    comp = Child(ShotTask).ui(group='Tasks')

    @classmethod
    def get_source_display(cls, oid):
        names = oid.split('/')
        return ' '.join(names[-3::2])

    def child_value_changed(self, child_value):
        if child_value is self.status:
            self.touch()

    def summary(self):
        return '%s (Anim, Lighting)' % (self.status.get(),)

    def get_thumbnail_object(self):
        '''
        Implementing this method let the GUI know how to
        display images for this object
        '''
        return self._thumbnail

# --------------------------------------- FILM


class Add10ShotsAction(Action):

    ICON = 'sequence'

    _shots = Parent()

    def run(self, button):
        start = len(self._shots) + 1
        for i in range(100):
            self._shots.add('P%03i' % (i + start))

        self._shots.touch()


class Shots(Map):

    ICON = 'shot'

    add_10_shots = Child(Add10ShotsAction)

    @classmethod
    def mapped_type(cls):
        return Shot

    def columns(self):
        return ['Name', 'Status']

    def _fill_row_cells(self, row, item):
        '''
        Subclasses must override this to fill value for each
        column returned by columns()
        '''
        row['Name'] = item.name()
        row['Status'] = item.status.get()

    def _fill_row_style(self, style, item, row):
        style['Status_icon'] = ('icons.status', row['Status'])


class Film(Object):

    shots = Child(Shots).ui(default_height=500)


class CreateFilmAction(Action):

    _map = Parent()

    film_name = Param('EP')

    def get_buttons(self):
        return ['Create']

    def run(self, button):
        i = len(self._map) + 1
        film = self._map.add('%s%03i' % (self.film_name.get(), i))
        self._map.touch()
        return self.get_result(goto=film.oid())


class Films(Map):

    create_film = Child(CreateFilmAction)

    @classmethod
    def mapped_type(cls):
        return Film

# ------------------------------------------------- PROJECT


class Launcher(Action):
    pass


class Launchers(Object):

    maya = Child(Launcher)
    max = Child(Launcher)
    guerilla = Child(Launcher)

    nuke = Child(Launcher)
    natron = Child(Launcher)


class ImageSettings(Object):

    frame_rate = Param(25)
    width = Param(2840)
    height = Param(1188)
    padding = Param(4)
    par = Param(1.0)


class MayaSettings(Object):

    project_path = Param('path/to/maya_project')
    user_away_path = Param('path/to/AWAY/Users/me')


class Settings(Object):

    project = Parent()

    image = Child(ImageSettings)
    Maya = Child(MayaSettings)


class CreateProjectFoldersAction(Action):

    def get_buttons(self):
        return ['Create']

    def run(self, button):
        pass


class ReversionAdmin(Object):

    repo_path = Param('path/to/cvs_repo')
    repo_exists = Param(True).ui(editor='bool')

    work_path = Param('path/to/work_dir')
    work_exists = Param(True).ui(editor='bool')

    mount_script = Param('\n\ntest...\n\n').ui(editor='textarea')


class ProjectMonkeyPatch(Object):

    filename = Param('path/to/project_monkey_patch.py')
    explore = Child(ExploreAction)
    edit = Child(TextEditAction)


class Admin(Object):

    project = Parent()

    create_folders = Child(CreateProjectFoldersAction)
    reversion = Child(ReversionAdmin)
    project_monkey_patch = Child(ProjectMonkeyPatch)


class DemoProject(Object):

    open = Child(Launchers)
    banks = Child(Banks)
    films = Child(Films)

    settings = Child(Settings)
    admin = Child(Admin)
