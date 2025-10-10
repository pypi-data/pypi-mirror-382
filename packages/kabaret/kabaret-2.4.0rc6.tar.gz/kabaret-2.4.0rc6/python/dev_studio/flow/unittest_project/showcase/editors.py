import time

from kabaret.flow import (
    values,
    Object, Map, Action, ConnectAction,
    ChoiceValueSetAction, ChoiceValueSelectAction,
    Child, Parent, Computed, Connection,
    Param, IntParam, BoolParam, HashParam,
    Label,
)


class MyChoices(values.ChoiceValue):

    CHOICES = ['WIP', 'RVW', 'RTK', 'DONE']


class MyMultiChoices(values.ChoiceValue):

    CHOICES = ['WIP', 'RVW', 'RTK', 'DONE']
    STRICT_CHOICES = False


class EditorsGroup(Object):

    doc = Label(
        '<HR><H4>'
        'Every relation can have its GUI representation configured:'
        '</H4>'
        '<pre>\n'
        '\tclass MyObject(Object):\n'
        '\t  my_child = Param(MyChild).ui(hidden=True, label="The Child", group="Group Name")'
        '</pre>\n'
        'Base options are:'
        '<ul>'
        '   <li>editable (bool)\t\t- set the editor writable or read-only</li>'
        '   <li>tooltip (str)\t\t- define the tooltip content</li>'
        '   <li>label (str)\t\t- define the editor label</li>'
        '   <li>group (str)\t\t- define the editors group where the editor will be</li>'
        '   <li>hidden (bool)\t\t- if True, the editor will be hidden unless the "show hidden value" is activated</li>'
        '</ul>'
        '<H4>'
        'Additionnaly to the group, label and visibility, you can control<br>'
        'which "Editor" is used when the related Object is a Value.<br>'
        'Here are examples of the default available editors.'
        '</H4>'
    )

    text_doc = Label(
        '<HR><H4>'
        'By <u>default</u> it displays a text field'
        '</H4>'
        'Options are:'
        '<ul>'
        '   <li>placeholder (str)</li>'
        '</ul>'
    )
    text = Param("").ui(placeholder="Enter your value")

    bool_doc = Label(
        '<HR><H4>'
        'The <u>bool</u> displays a check box'
        '</H4>'
        'Options are:'
        '<ul>'
        '   <li>true_text (str)</li>'
        '   <li>false_text (str)</li>'
        '</ul>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\t  bool_value = Param(False).ui(editor="bool", true_text="This is True", false_text="This is False")'
        '</pre>\n'
    )
    bool_value = BoolParam(False)  # default editor is 'bool' for BoolValue
    bool_value_with_text = Param(False).ui(
        editor='bool',
        true_text='This is True', false_text='This is False'
    )  # you can use the 'bool' editor even if not BoolValue

    choice_doc = Label(
        '<HR><H4>'
        'The <u>choice</u> displays a choice menu'
        '</H4>'
        'Options are:'
        '<ul>'
        '   <li>sorted (bool)</li>'
        '   <li>choice_icons:   dict mapping each choice to an icon_ref<br>'
        '       example: choice_icons={"Work in Progress":("icons.status", "WIP")}'
        '</ul>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\tclass MyChoices(values.ChoiceValue):\n'
        '\t  CHOICES = ["WIP", "RVW", "RTK", "DONE"]\n'
        '\t(...)\n'
        '\t  # defaut editor is "choice" for ChoiceValue\n'
        '\t  choice_value = Param("WIP", MyChoices)'
        '</pre>\n'
    )
    # defaut editor id 'choice' for ChoiceValue
    choice_value = Param('WIP', MyChoices)

    choice_icon_doc = Label(
        'The choice editor tries to find a status icon matching the first word for each choice<br>'
        'You can also provide arbitrary icon for each choice with the "choice_icons" option:<br>'
        '<pre>\n'
        '\tstatus = Param("DONE", MyChoices).ui(\n'
        '\t    choice_icons={\n'
        '\t        "WIP":("icons.flow","asset"), \n'
        '\t        "RVW":("icons.flow","film"), \n'
        '\t        "RTK":("icons.flow","shot"), \n'
        '\t        "DONE":("icons.gui","kabaret_icon"), \n'
        '\t    }\n'
        '\t)\n'
        '</pre>\n'
    )
    iconed_choice_value = Param('DONE', MyChoices).ui(
        choice_icons={
            'WIP':('icons.flow', 'asset'),
            'RVW':('icons.flow', 'film'),
            'RTK':('icons.flow', 'shot'),
            'DONE':('icons.gui', 'kabaret_icon'),
        }
    )
    text_choice_doc = Label(
        '<H3>'
        'You can still use another editor if you prefer'
        '</H3>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\t  text_choice_value = Param("WIP", MyChoices).ui(editor="python")'
        '</pre>\n'
    )
    text_choice_value = Param('WIP', MyChoices).ui(editor='python')

    multichoice_doc = Label(
        '<HR><H4>'
        'The <u>multichoice</u> editor let you select more than one choice</H4>'
        'Options are:'
        '<ul>'
        '   <li>sorted (bool)</li>'
        '</ul>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\tclass MyMultiChoices(values.ChoiceValue):\n'
        '\t  CHOICES = ["WIP", "RVW", "RTK", "DONE"]\n'
        '\t  STRICT_CHOICES = False\n'
        '(...)\n'
        '\t  multichoice_value = Param(["WIP"], editor="multichoice",'
        ' tooltip="Select one or more item in this awesome list !")'
        '</pre>\n'
    )
    multichoice = Param(['WIP'], MyMultiChoices).ui(
        editor='multichoice', tooltip='Select one or more item in this awesome list !'
    )

    multichoice_default_height_doc = Label(
        'In some cases you will need to control the multichoice default height.'
        'This can be achived with the <b>default_height</b> option'
    )
    multichoice_small = Param(['WIP'], MyMultiChoices).ui(
        editor='multichoice', tooltip='Select one or more item in this awesome list !',
        default_height=10
    )
    multichoice_big = Param(['WIP'], MyMultiChoices).ui(
        editor='multichoice', tooltip='Select one or more item in this awesome list !',
        default_height=150
    )

    textarea_doc = Label(
        '<HR><H4>'
        'The <u>textarea</u> editor shows multiple lines of text, and can be resized '
        'with the middle button.<br>'
        'Once edited, you can Apply your modifications or Cancel them with the appropriate button '
        'or shortcut (Ctrl+Renter / Escape)'
        '</H4>'
        'Options are:'
        '<ul>'
        '   <li>html (bool)</li>'
        '   <li>buttons_side  top/bottom/left/right (defaults to right)</li>'
        '</ul>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\t  textarea = Param("This is a html Multiline'
        '&lt;br&gt;&lt;font color="red"&gt;NOT Editable !&lt;/font&gt;", editor="textarea",'
        '\n\t    tooltip="This text is not editable... (editable=False)"), editable=False, html=True)'
        '</pre>\n'
    )
    textarea = Param('This\nIs\nMultiline\nEditable').ui(
        editor='textarea',
        tooltip='This text is editable, hit "Apply" to save.'
    )
    read_only_textarea = Param('This is a html Multiline<br><font color="red">NOT Editable !</font>').ui(
        editor='textarea',
        editable=False,
        tooltip='This text is not editable... (editable=False)',
        html=True
    )
    textarea_buttons_side = Param(
        'This textarea buttons are on the bottom side (edit this text to show them)\n'
        'This is achieved using option "buttons_side" with a value of '
        'top/bottom/left/right'
    ).ui(
        editor='textarea', buttons_side='bottom',
        tooltip='Edit the text to show the buttons.'
    )

    password_doc = Label(
        '<HR><H4>'
        'The <u>password</u> editor shows a text field with password format (hidden characters)<br>'
        '</H4>'
        'Options are:'
        '<ul>'
        '   <li>placeholder (str)</li>'
        '</ul>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\t  password = Param("password").ui(editor="password")'
        '</pre>\n'
    )
    password = Param("password").ui(editor="password")

    date_doc = Label(
        '<HR><H4>'
        'The <u>datetime</u> editor shows a date with the given format </br>'
        'You can edit the date with a calendar </br>'
        'The value stored is in seconds since epoch'
        '</H4>'
        'Options are:'
        '<ul>'
        '   <li>format (str)</li>'
        '   <li>minimum (seconds since epoch)</li>'
        '   <li>maximum (seconds since epoch)</li>'
        '</ul>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\t  datetime = Param(time.time()).ui(editor="datetime", format="MM/yyyy HH:ss")'
        '</pre>\n'
    )
    datetime = Param(time.time()).ui(editor="datetime", format="MM/yyyy HH:ss")
    date = Param(time.time()).ui(editor="date")

    progress_doc = Label(
        '<HR><H4>'
        'The <u>percent</u> editor shows a progress bar<br>'
        '</H4>'
        'Options are:'
        '<ul>'
        '   <li>minimum (float)</li>'
        '   <li>maximum (float)</li>'
        '   <li>display_text (bool) - display also progression in text or not'
        '</ul>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\t  progress = Param(75).ui(editor="percent")'
        '</pre>\n'
    )
    progress = Param(75).ui(editor="percent")

    error_doc = Label(
        '<HR><H4>'
        'Error are handled mostly with the tooltip and the property error="true" which can be handled in stylesheet'
        '</H4>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\t  date_error = Param(object()).ui(editor="datetime")'
        '</pre>\n'
    )
    date_error = Param(object()).ui(editor="datetime")

    thumbnail_doc = Label(
        '<HR><H4>'
        'The <u>thumbnail</u> editor shows an image which can be modified by a snapshot<br>'
        'The editor will not work if no path is set'
        '</H4>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\t  thumbnail = Param(<path_to_image>).ui(editor="thumbnail")'
        '</pre>\n'
    )
    thumbnail = Param(None).ui(editor="thumbnail")

    path_doc = Label(
        '<HR><H4>'
        'The <u>path</u> editor shows a text field that can be defined with a path value or multiple paths in a list.<br>'
        'A button on the right lets you use the file explorer to find a file or directory.'
        '</H4>'
        'Options are:'
        '<ul>'
        '   <li>start_path (str) - Open file explorer from a specific path</li>'
        '   <li>filters (list of str) - Displays files that match the patterns<br>'
        '       example: filters=["Text files (*.txt)", "Any files (*)"]</li>'
        '   <li>max_count (int) - Limit the maximum number of paths</li>'
        '   <li>dirs_only (bool) - Can only select directories</li>'
        '   <li>files_only (bool) - Can only select files</li>'
        '   <li>path_format win32/linux - Force path format to a specific operating system</li>'
        '</ul>'
        'Note: Depending on the options used, the operating system\'s native file explorer will be used instead.'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\tpath = Param().ui(editor="path")'
        '</pre>\n'
    )
    path = Param().ui(editor="path")

    image_doc = Label(
        '<HR><H4>'
        'The <u>image</u> editor lets you define an image to be converted to a base64 value.<br>'
        'You can click to use the file explorer or drag and drop an image file.'
        '</ul>'
        '<H3>Example:</H3>'
        '<pre>\n'
        '\timage = Param().ui(editor="image")'
        '</pre>\n'
    )
    image = Param().ui(editor="image")

