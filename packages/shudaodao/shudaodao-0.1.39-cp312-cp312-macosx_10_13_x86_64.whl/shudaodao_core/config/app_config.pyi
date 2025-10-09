from .loader import ConfigLoader as ConfigLoader
from .schemas.app_config import AppConfigSetting as AppConfigSetting
from _typeshed import Incomplete

class AppConfigLoader:
    @classmethod
    def load_config(cls) -> AppConfigSetting: ...

AppConfig: Incomplete
