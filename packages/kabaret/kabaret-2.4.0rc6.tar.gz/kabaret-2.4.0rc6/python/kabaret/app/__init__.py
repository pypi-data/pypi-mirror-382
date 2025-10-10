'''

    Lets do this:  <--- HAHAA ROFL !! THIS IS SOOOOO OOOOOLD !!! ^o^ (and almost 100% implemented ;) )
        FLOW
        - really granular queries for flow gui
        - hierarchical flow gui view (open a related page inside the page, with indentation)
        - find a way to have some relations on the same line (use relation ui_config infos)
        - file listener editor (for log files)
        - chat editor (for message maps)
        - Map gui should update mapped item infos when it receives a touch event for on of its mapped
        items (not refresh the whole map)
        - flow views should use current object.get_source_display() as view title ! :)
        - ICON in flow object should be able to point to alternative styles/resources repo
        
        PROCESS ACTOR
        - responsible for spawning typed subprocesses (editors)
        - defines env configs for each editor
        - logs outputs for all runs, has a view to show them
        - let the user kill subprocesses ?

        - One must be able to override/augment editor infos (exec_path, env vars,...) before spawining one.
            (the flow will need that)

        GUI:
        - get ride of the default scrolled content
        
'''

from .plugin_manager import plugin

from .session import KabaretSession

get_session = KabaretSession.get_session

del KabaretSession
