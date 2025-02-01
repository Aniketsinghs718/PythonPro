import os

import eel
eel.init('web')
os.system('start brave.exe --app="http://localhost:8000/index.html"')
eel.start('index.html',size=(800,800), mode = None,host='localhost',block=True)