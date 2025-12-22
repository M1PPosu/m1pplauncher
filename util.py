import os, sys
import json
from PySide6.QtCore import QObject

def get_app_path():
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
        return os.path.dirname(exe_path)
    else:
        exe_path = os.path.abspath(__file__)
        return os.path.dirname(exe_path)

def get_configdata():
    return json.loads(open(os.path.join(get_app_path(), 'installdata.json'), 'r').read())

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def config_setup():
    targetfile = os.path.join(get_app_path(), 'launchersettings.json')
    if not os.path.isfile(targetfile):
        open(targetfile, 'w').write('{"id0": 1,"id1": 1,"id10": 0,"id11": 1,"id111": 0}')

    data = json.loads(open(targetfile, 'r').read())
    for key in ["id0", "id1", "id10", "id11", "id111"]:
        value = data.get(key)
        if value not in [0, 1]:
            open(targetfile, 'w').write('{"id0": 1,"id1": 1,"id10": 0,"id11": 1,"id111": 0}')
        data[key] = int(value)
    
    return json.loads(open(targetfile, 'r').read()), data["id0"], data["id1"], data["id11"], data["id111"]
    
def config_set_value(key, value):
    f = json.loads(open(os.path.join(get_app_path(), 'launchersettings.json'), 'r').read())
    f[key] = value
    open(os.path.join(get_app_path(), 'launchersettings.json'), 'w').write(json.dumps(f))

def config_read_value(key):
    f = json.loads(open(os.path.join(get_app_path(), 'launchersettings.json'), 'r').read())
    return f[key]