"""
Хелперы для удобного чтения конфигурационного файла проекта
"""

from django.conf import (
    settings,
)
from django.utils.module_loading import (
    import_string,
)
import six


try:
    import configparser
except ImportError:
    import six.moves.configparser as configparser


class ProjectConfig:
    """
    Обертка над парсером параметров конфигурации
    """
    def __init__(self, filenames=[], defaults={}):
        self.parser = configparser.ConfigParser()
        if filenames:
            self.parser.read(filenames)
        self.defauls = defaults

    def read(self, filenames):
        """
        Загружает конфигурацию из файла(ов) filenames
        """
        self.parser = configparser.ConfigParser()
        self.parser.read(filenames)

    def set_defaults(self, defaults):
        """
        Устанавливает параметры проекта по умолчанию
        """
        self.defauls = defaults

    def update_defaults(self, update_values):
        """
        Обновляет параметры по умолчанию

        Возвращает итоговый словарь с умолчаниями

        :param dict update_values: словарь с обновляемыми значениями
        :return dict: итоговые параметры по умолчанию
        """
        self.defauls.update(update_values)

        return self.defauls

    def items(self, section):
        """
        Возвращает список кортежей (key, value) из указанной секции.
        В случае, если такой секции нет, то возвращается пустой список.
        """
        return self.parser.items(section) if self.parser.has_section(section) else []

    def get(self, section, option):
        """
        Безопасно возвращает значение конфигурационного параметра option
        из раздела section
        """
        try:
            value = self.parser.get(section, option).strip()
            if not value:
                return self.defauls[(section,option)]
            return value
        except:
            if (section,option) in self.defauls:
                return self.defauls[(section,option)]
        return ''

    def set(self, section, option, value):
        """
        Устанавливает значение конфигурационного параметра.

        :param str section: раздел
        :param str option: параметр
        :param str value: устанавливаемое значение
        """
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser.set(section, option, value)

    def get_bool(self, section, option):
        """
        Безопастно возвращает булево из конфига
        """
        value = self.get(section, option)
        if isinstance(value, six.string_types):
            value = value.upper() == 'TRUE'

        return bool(value)

    def get_int(self, section, option):
        """
        Безопасно возвращает целое число из конфига
        """
        value = self.get(section, option)
        if isinstance(value, str):
            try:
                value = int(value)
            except:
                value = 0
        return value

    def get_uint(self, section, option):
        """
        Безопасно возвращает положительное целое число из конфига
        """
        value = self.get_int(section, option)
        if value < 0:
            value = 0
        return value


def get_downloads_dir():
    """
    Функция получения директории для генерируемого контента.
    Геттер переопределяется в settings.py проекта
    """
    try:
        getter_path = settings.DOWNLOADS_DIR_GETTER
    except AttributeError:
        getter = lambda: settings.MEDIA_ROOT
    else:
        getter = import_string(getter_path)

    return getter()


def get_downloads_url():
    """
    Функция получения url для генерируемого контента.
    Геттер переопределяется в settings.py проекта
    """
    try:
        getter_path = settings.DOWNLOADS_URL_GETTER
    except AttributeError:
        getter = lambda: settings.MEDIA_URL
    else:
        getter = import_string(getter_path)

    return getter()
