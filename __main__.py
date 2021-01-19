import os

# checking environment variables (all of these must be set)
if not ("TG_API_ID" in os.environ and "TG_API_HASH" in os.environ and "ONLINE_INFORMER_BOT_TOKEN" in os.environ):
    raise IOError('Please set environmental variables TG_API_ID, TG_API_HASH and ONLINE_INFORMER_BOT_TOKEN '
                  'with proper values.')

import threading

from bot.bot import *

if "CREATE_TABLE" in os.environ:
    if os.environ["CREATE_TABLE"] == '1':
        User.create_table()

if __name__ == "__main__":
    # updater thread will run in background
    threading.Thread(target=updater).start()
    bot.polling(none_stop=True)
