from PySide6.QtCore import QTranslator, QLocale
from .config import RINUI_PATH
import os


class RinUITranslator(QTranslator):
    """
    RinUI i18n translator.
    :param locale: QLocale, optional, default is system locale
    """
    def __init__(self, locale: QLocale = QLocale.system().name(), parent=None):  # follow system
        super().__init__(parent)
        self.load(locale or QLocale())

    def load(self, locale: QLocale) -> bool:
        """
        Load translation file for the given locale.
        :param locale: QLocale, the locale to load (eg = QLocale(QLocale.Chinese, QLocale.China), QLocale("zh_CN"))
        :return: bool
        """
        print(f"🌏 Current locale: {locale.name()}")
        path = os.path.join(RINUI_PATH, "RinUI", "languages", f"{locale.name()}.qm")
        if not os.path.exists(path):
            print(f"Language file \"{path}\" not found. Fallback to default (en_US)")
            path = os.path.join(RINUI_PATH, "RinUI", "languages", "en_US.qm")
        return super().load(path)
