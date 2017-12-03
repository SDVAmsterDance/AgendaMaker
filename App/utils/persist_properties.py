import json
import os
from os.path import expanduser


class PersistProperties:
    def __init__(self):
        home = expanduser("~")

        properties_dir = os.path.join(home, ".agendamaker")
        self.properties_fname = os.path.join(properties_dir, "agendamaker.properties")

        if not os.path.isdir(properties_dir):
            os.mkdir(properties_dir)

        if not os.path.exists(self.properties_fname):
            with open(self.properties_fname, 'w') as f:
                json.dump({}, f)

        with open(self.properties_fname) as f:
            try:
                self.props = json.load(f)
            except Exception as e:
                print(e)
                self.props = {}
                json.dump({}, f)

    def __getitem__(self, item):
        if item in self.props:
            return self.props[item]
        else:
            raise KeyError("{} is not a know property".format(item))

    def __setitem__(self, key, value):
        self.props[key] = value
        with open(self.properties_fname, "w") as f:
            json.dump(self.props, f)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return ""

    def set_property(self, key, value):
        self[key] = value