from mpf.core.case_insensitive_dict import CaseInsensitiveDict
from mpf.core.utility_functions import Util
from mpfmc.core.config_collection import ConfigCollection
from mpfmc.uix.slide_frame import SlideFrame
from mpfmc.widgets.image import ImageWidget
from mpfmc.widgets.text import Text
from mpfmc.widgets.video import VideoWidget
from mpfmc.widgets.line import Line
from mpfmc.widgets.triangle import Triangle
from mpfmc.widgets.quad import Quad
from mpfmc.widgets.rectangle import Rectangle
from mpfmc.widgets.ellipse import Ellipse
from mpfmc.widgets.bezier import Bezier
from mpfmc.widgets.point import Point
from mpfmc.widgets.dmd import Dmd, ColorDmd
from mpfmc.widgets.character_picker import CharacterPicker
from mpfmc.widgets.entered_chars import EnteredChars


class Widget(ConfigCollection):

    config_section = 'widgets'
    collection = 'widgets'
    class_label = 'WidgetConfig'

    type_map = CaseInsensitiveDict(text=Text,
                                   image=ImageWidget,
                                   video=VideoWidget,
                                   slide_frame=SlideFrame,
                                   bezier=Bezier,
                                   # imageborder=Shape,
                                   ellipse=Ellipse,
                                   line=Line,
                                   point=Point,
                                   points=Point,
                                   quad=Quad,
                                   rectangle=Rectangle,
                                   triangle=Triangle,
                                   dmd=Dmd,
                                   color_dmd=ColorDmd,
                                   character_picker=CharacterPicker,
                                   entered_chars=EnteredChars)

    def process_config(self, config):
        # config is localized to a specific widget section
        if isinstance(config, dict):
            config = [config]

        config.reverse()

        widget_list = list()

        for widget in config:
            widget_list.append(self.process_widget(widget))

        return widget_list

    def process_widget(self, config, mode=None):
        # config is localized widget settings
        try:
            config['_widget_cls'] = Widget.type_map[config['type']]
        except KeyError:
            raise AssertionError('"{}" is not a valid MPF display widget type'
                                 .format(config['type']))

        config['_default_settings'] = set()

        for default_setting_name in config['_widget_cls'].merge_settings:
            if default_setting_name in config:
                config['_default_settings'].add(default_setting_name)

        self.mc.config_validator.validate_config('widgets:{}'.format(
            config['type']).lower(),
                             config, base_spec='widgets:common')

        if not mode:
            priority = 0
        else:
            priority = mode.priority

        try:
            config['priority'] += priority
        except (KeyError, TypeError):
            config['priority'] = priority

        if 'animations' in config:
            config['animations'] = self.process_animations(config['animations'])

        else:
            config['animations'] = None

        return config

    def process_animations(self, config):
        # config is localized to the slide's 'animations' section

        for event_name, event_settings in config.items():

            # str means it's a list of named animations
            if type(event_settings) is str:
                event_settings = Util.string_to_list(event_settings)

            # dict means it's a single set of settings for one animation step
            elif isinstance(event_settings, dict):
                event_settings = [event_settings]

            # ultimately we're producing a list of dicts, so build that list
            # as we iterate
            new_list = list()
            for settings in event_settings:
                new_list.append(self.mc.animations.process_animation(settings))

            config[event_name] = new_list

        return config



collection_cls = Widget