import datetime
import logging
import os
import win32api
from os.path import expanduser
from os.path import join, isdir

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform

from agenda.draw.draw_agenda import DrawAgenda
from agenda.draw.draw_flyer import DrawFlyer
from apis.google_calendar import get_calendars, remove_credentials
from apis.google_mail import create_message, send_message, create_draft
from birthday_email.email import Email

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


class CustomDropDown(DropDown):
    pass


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


class CalendarCheckBoxLabel(Label):
    def __init__(self, **kwargs):
        super(CalendarCheckBoxLabel, self).__init__(**kwargs)


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
        self.birthdays = set()
        self.calendar_dict = {}
        now = datetime.datetime.now()
        self.year = now.year
        self.month = now.month + 1

    def set_internal_activities(self, internal_activities):
        self.internal_activities = set([x.strip() for x in internal_activities.split(",")])

    def set_external_activities(self, external_activities):
        self.external_activities = set([x.strip() for x in external_activities.split(",")])

    def set_birthdays(self, birthdays):
        self.birthdays = set([x.strip() for x in birthdays.split(",")])

    def dismiss_popup(self):
        self._popup.dismiss()

    def make_calendar(self):
        self.persist.set_property("internal_activities", self.ids.internal_activities.text)
        self.persist.set_property("external_activities", self.ids.external_activities.text)
        self.persist.set_property("birthdays", self.ids.birthdays.text)
        self.persist.set_property("birthdays_template", self.ids.birthdays_template.text)
        self.set_internal_activities(self.ids.internal_activities.text)
        self.set_external_activities(self.ids.external_activities.text)
        self.set_birthdays(self.ids.birthdays.text)
        if self.ids.tabs.current_tab.text == "Maand":
            draw = DrawAgenda(self.month, self.year, internal_activities=self.internal_activities,
                              external_activities=self.external_activities)
            fname = draw.draw_agenda()
            self.ids.agenda_image.source = fname
            self.ids.agenda_image.reload()
            self.persist.set_property("agenda_image", fname)
        if self.ids.tabs.current_tab.text == "Flyer":
            draw = DrawFlyer(self.month, self.year, internal_activities=self.internal_activities,
                              external_activities=self.external_activities)
            fname = draw.draw_agenda()
            self.ids.flyer_image.source = fname
            self.ids.flyer_image.reload()
            self.persist.set_property("flyer_image", fname)
        elif self.ids.tabs.current_tab.text == "Verjaardagen":
            email = Email(birthdays=self.birthdays, internal_activities=self.internal_activities,
                              external_activities=self.external_activities, template=self.ids.birthdays_template.text)
            self.ids.birthdays_mail.text = email.make_email(month=self.month, year=self.year)

    def update_calendars(self):
        self.ids.connection_dropdown.select("Updating")
        self.calendar_dict = get_calendars()
        self.show_calendars()
        self.ids.connection_dropdown.select("Connection")

    def show_calendars(self):
        self.ids.checkbox_grid_internal_activities.clear_widgets()
        self.ids.checkbox_grid_external_activities.clear_widgets()
        for c in self.calendar_dict:
            # internal activities
            state = 'normal'
            if c in self.persist.internal_activities:
                state = 'down'
            self.ids.checkbox_grid_internal_activities.add_widget(CalendarCheckBoxLabel(text=self.calendar_dict[c]))
            checkbox = CalendarCheckBox(value=c, state=state)
            checkbox.bind(active=self.on_internal_checkbox_active)
            self.ids.checkbox_grid_internal_activities.add_widget(checkbox)

            # external activities
            state = 'normal'
            if c in self.persist.external_activities:
                state = 'down'
            self.ids.checkbox_grid_external_activities.add_widget(CalendarCheckBoxLabel(text=self.calendar_dict[c]))
            checkbox = CalendarCheckBox(value=c, state=state)
            checkbox.bind(active=self.on_external_checkbox_active)
            self.ids.checkbox_grid_external_activities.add_widget(checkbox)

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

    def check_focus(self, textinput, who=""):
        if not textinput.focus:
            if who == "internal":
                self.set_internal_activities(textinput.text)
            elif who == "external":
                self.set_external_activities(textinput.text)
            elif who == "birthdays":
                self.set_birthdays(textinput.text)

    def previous_month(self):
        if self.month == 1:
            self.year -= 1
        self.month -= 1
        self.month = (self.month % 12)
        if not self.month:
            self.month = 12
        self.ids.current_month.text = datetime.date(self.year, self.month, 1).strftime("%B %Y")
        self.make_calendar()

    def next_month(self):
        if self.month == 12:
            self.year += 1
        self.month += 1
        self.month = self.month % 12
        if not self.month:
            self.month = 12
        self.ids.current_month.text = datetime.date(self.year, self.month, 1).strftime("%B %Y")
        self.make_calendar()

    def logout(self):
        self.ids.connection_dropdown.select("Logging out")
        remove_credentials()
        self.ids.connection_dropdown.select("Connection")

    def export_email(self):
        if self.ids.tabs.current_tab.text == "Verjaardagen":
            self.ids.connection_dropdown.select("Exporting")
            message_text = self.ids.birthdays_mail.text
            message = create_message('Bestuur SDV AmsterDance <bestuur@sdvamsterdance.nl>', '',
                                     'Agenda AmsterDance ' + Maand(self.month).name, message_text=message_text)
            create_draft(user_id='me', message=message)
            self.ids.connection_dropdown.select("Connection")
        else:
            content = WarningPopup(message="Is de mail al gemaakt?", cancel=self.dismiss_popup)
            self._popup = MessagePopup(title="Error", content=content)
            self._popup.open()


    def export_facebook(self):
        if self.ids.tabs.current_tab.text == "Verjaardagen":
            self.ids.connection_dropdown.select("Exporting")
            message_text = "Hello World, This is my first post for today"

            ACCESS_TOKEN = "<your access token>"  # do not forget to add access token here
            graph = fb.GraphAPI(ACCESS_TOKEN)
            graph.put_object("me", "feed", message_text)
            self.ids.connection_dropdown.select("Connection")
        else:
            content = WarningPopup(message="Is de mail al gemaakt?", cancel=self.dismiss_popup)
            self._popup = MessagePopup(title="Error", content=content)
            self._popup.open()


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
        self.root.main_screen.ids.birthdays_template.text = self.persist.birthdays_template
        self.root.main_screen.internal_activities = set(
            [x.strip() for x in self.persist.internal_activities.split(",")])
        self.root.main_screen.external_activities = set(
            [x.strip() for x in self.persist.external_activities.split(",")])
        self.root.main_screen.birthdays = set(
            [x.strip() for x in self.persist.birthdays.split(",")])
        self.root.main_screen.ids.agenda_image.source = self.persist.agenda_image
        self.root.main_screen.ids.agenda_image.reload()
        self.root.main_screen.ids.flyer_image.source = self.persist.flyer_image
        self.root.main_screen.ids.flyer_image.reload()
        self.root.main_screen.update_calendars()


class Manager(ScreenManager):
    main_screen = ObjectProperty(None)


if __name__ == '__main__':
    AgendaMakerApp().run()
