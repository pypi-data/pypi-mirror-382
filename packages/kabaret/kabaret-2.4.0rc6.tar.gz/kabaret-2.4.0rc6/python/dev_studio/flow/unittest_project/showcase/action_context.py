

from kabaret import flow

USE_INGRID = True
try:
    from kabaret.ingrid.flow_objects import InGridConfig
except ImportError:
    USE_INGRID = False

class DOAction(flow.Action):

    def allow_context(self, context):
        return context and context.endswith('.details')

    def needs_dialog(self):
        return False

class DetailOnlyActions(flow.Object):

    label = flow.Label(
        'All actions here only show on this Object details. '
        '(there is no action menu next to the Object field name)'
    )
    action_1 = flow.Child(DOAction)
    action_2 = flow.Child(DOAction)
    action_3 = flow.Child(DOAction)


class IOAction(flow.Action):

    def allow_context(self, context):
        return context and context.endswith('.inline')

    def needs_dialog(self):
        return False

class InlineOnlyActions(flow.Object):

    label = flow.Label(
        'All actions here only show on this Object inline. '
        '(there is no action menu inside the Object)'
    )

    action_1 = flow.Child(IOAction)
    action_2 = flow.Child(IOAction)
    action_3 = flow.Child(IOAction)


class DAIAction(flow.Action):

    def allow_context(self, context):
        return True

    def needs_dialog(self):
        return False

class DetailAndInlineActions(flow.Object):

    label = flow.Label(
        'All actions here are visible inline and in details. '
    )

    action_1 = flow.Child(DAIAction)
    action_2 = flow.Child(DAIAction)
    action_3 = flow.Child(DAIAction)


if USE_INGRID:

    class InGridAction(flow.Action):

        def allow_context(self, context):
            return context and context.startswith('InGrid')

        def needs_dialog(self):
            return False

    class InGridRowAction(InGridAction):

        def allow_context(self, context):
            return context == 'InGrid.row'

    class InGridColumnAction(InGridAction):

        def allow_context(self, context):
            return context == 'InGrid.column'

    class InGridCellAction(InGridAction):

        def allow_context(self, context):
            return context == 'InGrid.cell'

    class TestInGridConfig(InGridConfig):

        _parent = flow.Parent()

        def get_oid_with_actions(self):
            return self._parent.oid()

        def get_rows(self):
            oid = self.get_oid_with_actions()
            return [
                dict(display=str(i), oid=oid)
                for i in range(20)
            ]

        def get_columns(self):
            oid = self.get_oid_with_actions()
            return [
                dict(display=c, oid=oid)
                for c in 'ABCDEFGHIJKLMNOPQ'
            ]

        def get_cell(self, row, column):
            oid = self.get_oid_with_actions()
            return dict(
                display='{}x{}'.format(row, column),
                oid=oid,
                bg=None,
                fg=None,
                icon=None,
                ui=None,
                align='center', # one of ['left', 'right', 'center']
            )

        # def get_actions(self, *row_column_pairs):
        #     '''
        #     Return a list of (label, action_oid) for the given list
        #     of (row, cols)
        #     '''
        #     return []

    class InGridOnlyActions(flow.Object):

        label = flow.Label(
            'Actions here are only visible inside a InGid view. '
            'You will need to have <i>kabaret.ingrid</i> extension installed to test this.<br>'
            '(Drop this group on a InGrid view to load it)<br>'
            'Some are only visible in grid headers, some in grid cells.'
        )
        row_only_action = flow.Child(InGridRowAction)
        column_only_action = flow.Child(InGridColumnAction)
        cell_action = flow.Child(InGridCellAction)
        ingrid_action = flow.Child(InGridAction)

        sep = flow.Separator()  # there's a layout bug, this is a workaround

        _ingrid_config = flow.Child(TestInGridConfig)

        def get_ingrid_config_oids(self):
            return [self._ingrid_config.oid()]

class ActionContextGroup(flow.Object):

    detail_only_actions = flow.Child(DetailOnlyActions)
    inline_only_actions = flow.Child(InlineOnlyActions)
    detail_and_inline_actions = flow.Child(DetailAndInlineActions)
    
    if USE_INGRID:
        ingrid_only_actions = flow.Child(InGridOnlyActions)


