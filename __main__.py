import os.path

if not (os.path.exists('./settings/.api_id') and
        os.path.exists('./settings/.api_hash') and
        os.path.exists('./settings/.bot_token')):
    raise IOError('Please create files `./settings/{.api_id, .api_hash, .bot_token}` and fill them with proper values.')

import threading
from pathlib import Path

from bot.bot import *

Path('./temp').mkdir(parents=True, exist_ok=True)
User.create_table()

threading.Thread(target=updater).start()
bot.polling(none_stop=True)
