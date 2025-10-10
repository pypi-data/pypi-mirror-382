import re
import logging

from qtpy import QtWidgets

import kabaret.app.resources as resources


class Style(object):

    def __init__(self, name):
        super(Style, self).__init__()
        StylesManager.get().register_style(name, self)
        self._properties = {}

    def apply(self, widget=None):
        raise NotImplementedError()

    def apply_css(self, widget, css):
        """
        Set the css of the widget and load resources if referenced
        You can call a resource from the css with bracket and registered path of the resource
        Example:
        image: url({icons.gui.check});
        """
        regex = r'\{([\w\.\-_]+)\}'
        pattern = re.compile(regex)
        for match in pattern.finditer(css):
            path = match.group(1).split('.')
            try:
                css = css.replace(match.group(0), resources.get('.'.join(path[:-1]), path[-1])).replace('\\','/')
            except (resources.ResourcesError, resources.NotFoundError):
                logging.getLogger('kabaret.style').warning('Resource %r not found' % match.group(1))
                css = css.replace(match.group(0), 'none')
        widget.setStyleSheet(css)

    def set_property(self, name, value):
        self._properties[name] = value

    def get_property(self, name, default=None):
        return self._properties.get(name, default)


class StylesManager(object):

    _THE = None

    @classmethod
    def get(cls):
        return cls._THE

    def __init__(self):
        if self.__class__._THE is not None:
            raise Exception('The StylesManager is a singleton, you cant instantiate another one.')
        self.__class__._THE = self
        super(StylesManager, self).__init__()
        self._styles = {}
        self._default_style_name = None

    def register_style(self, name, style, set_default=True):
        self._styles[name] = style
        if set_default or self._default_style_name is None:
            self._default_style_name = name

    def get_style(self, name):
        return self._styles[name]

    def get_default_style(self):
        return self.get_style(self._default_style_name)

    def apply_default_style(self, widget=None):
        if self._default_style_name is None:
            raise Exception('No style registered !')
        self.apply_style(self._default_style_name, widget)

    def apply_style(self, style_name, widget=None):
        style = self.get_style(style_name)
        logging.getLogger('kabaret.style').debug(str(style))
        style.apply(
            widget or QtWidgets.QApplication.instance()
        )

StylesManager() # instanciate the singleton.


