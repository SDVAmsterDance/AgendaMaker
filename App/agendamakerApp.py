import datetime
import logging
import os
import win32api
from calendar import monthrange
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

from apis.google_calendar import get_calendars, remove_credentials, copy_events
from apis.google_mail import create_message, create_draft
from exports.agenda.draw.draw_agenda import DrawAgenda
from exports.agenda.draw.draw_flyer import DrawFlyer
from exports.birthday_email.email import Email
from exports.website.export import Website
from translatables.month import Maand

try:
    from App.utils.persist_properties import PersistProperties
except:
    from translatables.persist_properties import PersistProperties

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


class PasswordPopup(FloatLayout):
    cancel = ObjectProperty(None)
    submit = ObjectProperty(None)

    def __init__(self, message=None, **kwargs):
        super(PasswordPopup, self).__init__(**kwargs)
        self.ids.password_popup_text.text = message


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
        self.html_activities = {}
        self.website = None

    def set_internal_activities(self, internal_activities):
        self.internal_activities = set([x.strip() for x in internal_activities.split(",") if x.strip()])

    def set_external_activities(self, external_activities):
        self.external_activities = set([x.strip() for x in external_activities.split(",") if x.strip()])

    def set_birthdays(self, birthdays):
        self.birthdays = set([x.strip() for x in birthdays.split(",")])

    def dismiss_popup(self):
        self._popup.dismiss()

    def make_calendar(self, force_month=False, force_lang=None):
        self.persist.set_property("internal_activities", self.ids.internal_activities.text)
        self.persist.set_property("external_activities", self.ids.external_activities.text)
        self.persist.set_property("birthdays", self.ids.birthdays.text)
        self.persist.set_property("birthdays_template", self.ids.birthdays_template.text)
        self.set_birthdays(self.ids.birthdays.text)
        if not force_lang:
            lang = 'nl'
            if self.ids.language_switch.active:
                self.set_internal_activities(self.ids.translation_calendar_intern.text)
                self.set_external_activities(self.ids.translation_calendar_extern.text)
                lang = 'en'
            else:
                self.set_internal_activities(self.ids.internal_activities.text)
                self.set_external_activities(self.ids.external_activities.text)
        else:
            lang = force_lang

        if self.ids.tabs.current_tab.text == "Maand" or force_month:
            return self.make_agenda(lang)
        if self.ids.tabs.current_tab.text == "Flyer":
            return self.make_flyer(lang)
        elif self.ids.tabs.current_tab.text == "Email":
            self.make_email()

    def make_agenda(self, lang):
        draw = DrawAgenda(self.month, self.year, internal_activities=self.internal_activities,
                          external_activities=self.external_activities, language=lang)
        fname = draw.draw_agenda()
        self.html_activities[lang] = draw.html_activities
        self.ids.agenda_image.source = fname
        self.ids.agenda_image.reload()
        return fname

    def make_flyer(self, lang):
        draw = DrawFlyer(self.month, self.year, internal_activities=self.internal_activities,
                         external_activities=self.external_activities, language=lang)
        fname = draw.draw_agenda()
        self.ids.flyer_image.source = fname
        self.ids.flyer_image.reload()
        return fname

    def make_email(self):
        self.set_internal_activities(self.ids.internal_activities.text)
        self.set_external_activities(self.ids.external_activities.text)
        internal_activities = self.internal_activities
        external_activities = self.external_activities
        self.set_internal_activities(self.ids.translation_calendar_intern.text)
        self.set_external_activities(self.ids.translation_calendar_extern.text)
        internal_activities_en = self.internal_activities
        external_activities_en = self.external_activities
        email = Email(birthdays=self.birthdays, internal_activities=internal_activities,
                      external_activities=external_activities, internal_activities_en=internal_activities_en,
                      external_activities_en=external_activities_en, template=self.ids.birthdays_template.text)
        self.ids.birthdays_mail.text = email.make_email(month=self.month, year=self.year)

    def export_website(self):
        def submit():
            ftp_pass = self._popup.content.ids.password_password.text
            if not self.website:
                self.website = Website(server=self.ids.website_server.text, port=self.ids.website_port.text,
                                       path=self.ids.website_path.text, user=self.ids.website_username.text)

            resp = self.website.add_activities(self.month, str(self.year), self.html_activities,
                                               ftp_pass=ftp_pass,
                                               upload=self.ids.upload_switch.active,
                                               fname=self.ids.website_js_fname.text)
            if not resp:
                self._popup.dismiss()
                del ftp_pass
                self._popup.content.ids.password_password.text = ""
                if self.ids.language_switch.active:
                    self.ids.agenda_image.source = en_image
                    self.ids.agenda_image.reload()
                else:
                    self.ids.agenda_image.source = nl_image
                    self.ids.agenda_image.reload()
                self.ids.connection_dropdown.select("Menu")
            else:
                self._popup.content.ids.password_popup_text.text = resp
                self._popup.content.ids.password_popup_text.color = (1, 0, 0, 1)

        nl_image = self.make_calendar(force_month=True, force_lang='nl')
        en_image = self.make_calendar(force_month=True, force_lang='en')
        content = PasswordPopup(message="Wachtwoord voor de website", cancel=self.dismiss_popup, submit=submit)
        self._popup = MessagePopup(title="Login", content=content)
        self._popup.open()

    def update_calendars(self):
        self.ids.connection_dropdown.select("Updating")
        self.calendar_dict = get_calendars()
        self.show_calendars()
        self.ids.connection_dropdown.select("Menu")

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

    def translate_agenda(self):
        self.ids.connection_dropdown.select("Updating")
        self.persist.set_property("internal_activities", self.ids.internal_activities.text)
        self.persist.set_property("external_activities", self.ids.external_activities.text)
        self.set_internal_activities(self.ids.internal_activities.text)
        self.set_external_activities(self.ids.external_activities.text)
        start_date = datetime.date(self.year, self.month, 1)
        end_date = datetime.date(self.year, self.month, monthrange(self.year, self.month)[1]) + datetime.timedelta(
            days=1)

        for calendar_id in self.internal_activities:
            copy_events(calendar_id, self.ids.translation_calendar_intern.text, start_date, end_date)

        for calendar_id in self.external_activities:
            copy_events(calendar_id, self.ids.translation_calendar_extern.text, start_date, end_date)

        self.ids.connection_dropdown.select("Menu")

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
        self.ids.connection_dropdown.select("Menu")

    def export_email(self):
        if self.ids.tabs.current_tab.text == "Email":
            self.ids.connection_dropdown.select("Exporting")
            message_text = self.ids.birthdays_mail.text
            message = create_message('Bestuur SDV AmsterDance <bestuur@sdvamsterdance.nl>', '',
                                     'Agenda AmsterDance ' + Maand(self.month).name, message_text=message_text)
            create_draft(user_id='me', message=message)
            self.ids.connection_dropdown.select("Menu")
        else:
            content = PasswordPopup(message="Is de mail al gemaakt?", cancel=self.dismiss_popup)
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

        # Birthdays and calendars
        self.root.main_screen.ids.internal_activities.text = self.persist.internal_activities
        self.root.main_screen.ids.external_activities.text = self.persist.external_activities
        self.root.main_screen.ids.translation_calendar_intern.text = self.persist.internal_activities_en
        self.root.main_screen.ids.translation_calendar_extern.text = self.persist.external_activities_en
        self.root.main_screen.ids.birthdays.text = self.persist.birthdays
        self.root.main_screen.ids.birthdays_template.text = self.persist.birthdays_template
        self.root.main_screen.internal_activities = set(
            [x.strip() for x in self.persist.internal_activities.split(",")])
        self.root.main_screen.external_activities = set(
            [x.strip() for x in self.persist.external_activities.split(",")])
        self.root.main_screen.birthdays = set(
            [x.strip() for x in self.persist.birthdays.split(",")])

        # images
        m_name = Maand(self.root.main_screen.month).name + str(self.root.main_screen.year) + ".gif"
        self.root.main_screen.ids.agenda_image.source = m_name
        self.root.main_screen.ids.agenda_image.reload()
        self.root.main_screen.ids.flyer_image.source = "flyer-" + m_name
        self.root.main_screen.ids.flyer_image.reload()

        # make sure the calendars are up to date
        self.root.main_screen.update_calendars()

        # display the current month
        self.root.main_screen.ids.current_month.text = datetime.date(self.root.main_screen.year,
                                                                     self.root.main_screen.month, 1).strftime("%B %Y")


class Manager(ScreenManager):
    main_screen = ObjectProperty(None)


if __name__ == '__main__':
    AgendaMakerApp().run()
