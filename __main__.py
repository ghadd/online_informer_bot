import os

if not ("TG_API_ID" in os.environ and "TG_API_HASH" in os.environ and "ONLINE_INFORMER_BOT_TOKEN" in os.environ):
    raise IOError('Please create files `./settings/{.api_id, .api_hash, .bot_token}` and fill them with proper values.')

import threading
from pathlib import Path

from bot.bot import *

Path('~/.cache').mkdir(parents=True, exist_ok=True)
User.create_table()

if __name__ == "__main__":
    # threading.Thread(target=updater).start()
    bot.polling(none_stop=True)
