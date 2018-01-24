import logging
import os
import win32api
from io import StringIO
from os.path import expanduser
from os.path import join, isdir

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.image.img_pygame import ImageLoaderPygame
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.utils import platform

try:
    from utils.persist_properties import PersistProperties
except:
    from App.utils.persist_properties import PersistProperties

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


class MainScreen(Screen):
    loadfile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process_running = False

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_set_gnucash_file_path(self):
        path = None
        if self.ids.gnucash_file_path.text:
            if isdir(self.ids.gnucash_file_path.text):
                path = self.ids.gnucash_file_path.text
            else:
                path = os.path.dirname(self.ids.gnucash_file_path.text)
                print(path)

        content = LoadDialog(path=path, load=self.set_destination_path, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select GnuCash File", content=content)
        self._popup.open()

    def set_destination_path(self, path, filename):
        self.ids.gnucash_file_path.text = filename[0]
        self.dismiss_popup()

    def make_report(self):
        print("Pressed the button")

    def on_touch_down(self, touch):
        if self.ids.agenda_image.collide_point(*touch.pos):
            print(touch)
        else:
            super(MainScreen, self).on_touch_down(touch)

    def clicked_agenda(self):
        print("clicked")


class AgendaMakerApp(App):
    current_action = ""
    rv_data = []
    printed = False

    def build(self):
        return Manager()

    def on_start(self, **kwargs):
        self.persist = PersistProperties()
        print(self.persist)
        print(self.root.main_screen)
        self.root.main_screen.persist = self.persist


class Manager(ScreenManager):
    main_screen = ObjectProperty(None)


if __name__ == '__main__':
    AgendaMakerApp().run()
