from sqlalchemy import URL

ADMINS = ()


# create u'r own url objects
local_url_object = URL.create()

global_url_object = URL.create()

TOKEN = ""


greeting_text = """
Приветствую, <b>выберите группу</b> для дальнейшего пользования ботом
"""

group_choosing_text = """
<b>Выберите группу</b> 👥 для продолжения работы в боте
"""

licence_text = """
Предлагаем прочитать лиц.соглашение(вы можете просто скипнуть его, 
однако в любом случае используя данное п.о вы его принимает:) ), 
в дальнейшем оно будет доступно в меню настроек"""
