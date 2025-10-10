'''


    Maya User Setup File.

    The PYTHONPATH must be set to the dir of this file for maya to
    exec it at startup.

    BEWARE:
        MAYA WILL NOT REPORT ERRORS HERE. 
        YOU MUST CATCH AND REPORT EXCEPTIONS YOURSELF!

'''
import os, sys, traceback
import logging

if __name__ == '__main__':

    try:
        kabaret_home = os.environ['KABARET_INSTALL']
    except KeyError:
        logging.getLogger('kabaret.demo').warning('Could not find KABARET_HOME in env :(')
    else:
        try:
            dev_studio_home = os.environ['DEV_STUDIO_INSTALL']
        except KeyError:
            logging.getLogger('kabaret.demo').warning('Could not find DEV_STUDIO_HOME in env :(')
        else:
            logging.getLogger('kabaret.demo').info('Installing Kabaret from ' + kabaret_home)
            if kabaret_home not in sys.path:
                sys.path.append(kabaret_home)
            try:
                import kabaret
            except ImportError:
                traceback.print_exc()
                logging.getLogger('kabaret.demo').info('=========> !!! Could not import kabaret package !!!')
            else:
                logging.getLogger('kabaret.demo').info('   Ok.')

            logging.getLogger('kabaret.demo').info('Installing Dev Studio from ' + dev_studio_home)
            if dev_studio_home not in sys.path:
                sys.path.append(dev_studio_home)
            try:
                import dev_studio
            except ImportError:
                traceback.print_exc()
                logging.getLogger('kabaret.demo').info('=========> !!! Could not import dev_studio package !!!')
            else:
                logging.getLogger('kabaret.demo').info('   Ok.')

    # From now on, print will fall into the Script Editor:
    import maya.utils
    maya.utils.executeDeferred('import dev_studio.flow.demo_project.maya_startup as ms; ms.install_kabaret()')
