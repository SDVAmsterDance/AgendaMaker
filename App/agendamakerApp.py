import logging
import os
import win32api
from os.path import expanduser
from os.path import join, isdir

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform

from agenda.draw_agenda import DrawAgenda
from apis.google_calendar import get_calendars, remove_credentials

try:
    from App.utils.persist_properties import PersistProperties
except:
    from utils.persist_properties import PersistProperties

from kivy.config import Config

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '720')

MAX_TIME = 1 / 60

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('agendamakerapp')
logger.setLevel(logging.DEBUG)


def get_drives():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    return drives


class MessagePopup(Popup):
    pass


class WarningPopup(FloatLayout):
    cancel = ObjectProperty(None)

    def __init__(self, message=None, **kwargs):
        super(WarningPopup, self).__init__(**kwargs)
        self.ids.warning_popup_text.text = message


class CalendarCheckBox(CheckBox):
    value = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CalendarCheckBox, self).__init__(**kwargs)


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def __init__(self, path=None, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        self.drives_list.adapter.bind(on_selection_change=self.drive_selection_changed)
        if path and isdir(path):
            self.filechooser.path = path
        else:
            home = expanduser("~")
            drives = self.get_win_drives()
            if drives:
                self.filechooser.path = home

    def show_item(self, directory, filename):
        result = (self.is_dir(directory, filename) and not self.is_hidden_folder(directory, filename)) or (
            os.path.isfile(filename) and filename.split(".")[-1] == "gnucash")
        return result

    @staticmethod
    def is_dir(directory, filename):
        return isdir(join(directory, filename))

    @staticmethod
    def is_hidden_folder(directory, filename):
        first_of_last = join(directory, filename).split(os.sep)[-1][0]
        if first_of_last is ".":
            return True
        return False

    def get_quick_links(self):
        links = []
        home = expanduser("~")
        links.append(home)
        links += self.get_win_drives()
        return links

    @staticmethod
    def get_win_drives():
        if platform == 'win':
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
            return drives
        else:
            return []

    def drive_selection_changed(self, *args):
        selected_item = args[0].selection[0].text
        self.filechooser.path = selected_item

    def go_to_directory(self, path):
        if isdir(path):
            self.filechooser.path = path


class CalendarDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CalendarDialog, self).__init__(**kwargs)
        self.calendar_dict = get_calendars()
        self.add_checkboxes()

    def add_checkboxes(self):
        for c in self.calendar_dict:
            self.ids.checkbox_grid.add_widget(Label(text=self.calendar_dict[c]))
            self.ids.checkbox_grid.add_widget(CalendarCheckBox(value=c))

    def get_keys(self):
        if self.calendar_dict is None:
            self.calendar_dict = get_calendars()
        return [k for k in self.calendar_dict.keys()]


class MainScreen(Screen):
    loadfile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process_running = False
        self.internal_activities = set()
        self.external_activities = set()
        self.calendar_dict = {}

    def set_internal_activities(self, internal_activities):
        self.internal_activities = set([x.strip() for x in internal_activities.split(",")])

    def set_external_activities(self, external_activities):
        self.external_activities = set([x.strip() for x in external_activities.split(",")])

    def dismiss_popup(self):
        self._popup.dismiss()

    def make_calendar(self):
        self.persist.set_property("internal_activities", self.ids.internal_activities.text)
        self.persist.set_property("external_activities", self.ids.external_activities.text)
        self.persist.set_property("birthdays", self.ids.birthdays.text)
        self.set_internal_activities(self.ids.internal_activities.text)
        self.set_external_activities(self.ids.external_activities.text)
        draw = DrawAgenda(internal_activities=self.internal_activities, external_activities=self.external_activities)
        draw.draw_agenda()
        self.ids.agenda_image.reload()

    def update_calendars(self):
        self.calendar_dict = get_calendars()
        self.show_calendars()

    def show_calendars(self):
        self.ids.checkbox_grid_internal_activities.clear_widgets()
        self.ids.checkbox_grid_external_activities.clear_widgets()
        self.ids.checkbox_grid_birthdays.clear_widgets()
        for c in self.calendar_dict:
            # internal activities
            state = 'normal'
            if c in self.persist.internal_activities:
                state = 'down'
            self.ids.checkbox_grid_internal_activities.add_widget(Label(text=self.calendar_dict[c]))
            checkbox = CalendarCheckBox(value=c, state=state)
            checkbox.bind(active=self.on_internal_checkbox_active)
            self.ids.checkbox_grid_internal_activities.add_widget(checkbox)

            # external activities
            state = 'normal'
            if c in self.persist.external_activities:
                state = 'down'
            self.ids.checkbox_grid_external_activities.add_widget(Label(text=self.calendar_dict[c]))
            checkbox = CalendarCheckBox(value=c, state=state)
            checkbox.bind(active=self.on_external_checkbox_active)
            self.ids.checkbox_grid_external_activities.add_widget(checkbox)

            # birthdays
            state = 'normal'
            if c in self.persist.birthdays:
                state = 'down'
            self.ids.checkbox_grid_birthdays.add_widget(Label(text=self.calendar_dict[c]))
            checkbox = CalendarCheckBox(value=c, state=state)
            checkbox.bind(active=self.on_external_checkbox_active)
            self.ids.checkbox_grid_birthdays.add_widget(checkbox)

    def on_internal_checkbox_active(self, checkbox, value):
        if value:
            self.internal_activities.add(checkbox.value)
        else:
            self.internal_activities.remove(checkbox.value)
        self.ids.internal_activities.text = ",".join(self.internal_activities)

    def on_external_checkbox_active(self, checkbox, value):
        if value:
            self.external_activities.add(checkbox.value)
        else:
            self.external_activities.remove(checkbox.value)
        self.ids.external_activities.text = ",".join(self.external_activities)

    # def on_birthday_checkbox_active(self, checkbox, value):
    #     if value:
    #         self.birthdays.add(checkbox.value)
    #     else:
    #         self.internal_activities.remove(checkbox.value)
    #     self.ids.internal_activities.text = ",".join(self.internal_activities)

    def check_focus(self, textinput, who=""):
        if not textinput.focus:
            if who == "internal":
                self.set_internal_activities(textinput.text)
            elif who == "external":
                self.set_external_activities(textinput.text)

    @staticmethod
    def logout():
        remove_credentials()


class AgendaMakerApp(App):
    current_action = ""
    rv_data = []
    printed = False

    def build(self):
        return Manager()

    def on_start(self, **kwargs):
        self.persist = PersistProperties()
        self.root.main_screen.persist = self.persist
        self.root.main_screen.ids.internal_activities.text = self.persist.internal_activities
        self.root.main_screen.ids.external_activities.text = self.persist.external_activities
        self.root.main_screen.ids.birthdays.text = self.persist.birthdays
        self.root.main_screen.internal_activities = set(
            [x.strip() for x in self.persist.internal_activities.split(",")])
        self.root.main_screen.external_activities = set(
            [x.strip() for x in self.persist.external_activities.split(",")])
        self.root.main_screen.update_calendars()


class Manager(ScreenManager):
    main_screen = ObjectProperty(None)


if __name__ == '__main__':
    AgendaMakerApp().run()
