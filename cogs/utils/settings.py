# Bot Utilities
from types import prepare_class
from cogs.utils.my_errors import NoToken

import codecs
import json
from collections import namedtuple

from environs import Env, EnvError
from marshmallow.validate import URL


class Settings:
    def __init__(self, data_dir, log_level, log_to_file):

        env = Env()
        env.read_env()

        self.data_dir = env.str("PROGBOTT_DATA_DIR", data_dir)

        env.read_env(self.data_dir + "/.env")

        self.log_level = env.log_level("PROGBOTT_LOG_LEVEL") or log_level
        self.log_to_file = env.str("PROGBOTT_LOG_FILE") or log_to_file

        setting_path = self.data_dir + "/settings.json"

        extra = {"github": {}}
        try:
            with codecs.open(setting_path, "r", encoding="utf8") as f:
                fil = json.load(f)
                self.token = fil.get("token")
                self.prefix = fil.get("prefixes")

                extra = {**extra, **fil.get("extra")}
        except FileNotFoundError:
            pass

        try:
            with env.prefixed("PROGBOTT_"):
                self.token = env.str("TOKEN")
                self.prefix = env.list("PREFIXES")

                with env.prefixed("EXTRA_GITHUB_"):
                    extra["github"]["secret"] = env.str("SECRET")
                    extra["github"]["client_id"] = env.str("CLIENTID")
                    extra["github"]["callback_url"] = env.str("CALLBACKURL", validate=URL())

        except EnvError:
            pass

        if not self.prefix:
            self.prefix = "^"

        try:
            isinstance(self.token, str)
        except AttributeError:
            raise NoToken("No token found")

        try:
            self.extra = namedtuple("settings", extra.keys())(*extra.values())
        except KeyError:
            pass
