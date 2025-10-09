#coding:utf-8
"""
Created on 16.01.2011

@author: akvarats
"""
from __future__ import absolute_import
import datetime

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

from django.conf import settings
from django.contrib import auth

try:
    from django.utils.log import logger
except ImportError:
    from logging import getLogger
    logger = getLogger('django')

from m3_django_compatibility import is_authenticated
from m3_django_compatibility.middleware import MiddlewareMixin


#==============================================================================
# M3 Common Middleware
#==============================================================================

class ThreadData(object):
    """
    Класс-враппер для набора данных, которые храняться в
    thread-locals
    """

    DEFAULT_USER_ID = 0
    DEFAULT_USER_LOGIN = 'console-user'
    DEFAULT_USER_NAME = u'Пользователь системной консоли'

    DEFAULT_SESSION_KEY = 'console-session'

    DEFAULT_CLIENT_HOST = 'server'

    ANONYMOUS_USER_ID = 0
    ANONYMOUS_USER_LOGIN = 'anonymous-user'
    ANONYMOUS_USER_NAME = u'Анонимный пользователь'

    def __init__(self):
        self.clear()

    def clear(self):
        """
        Приводит данные объекта в начальное состояние
        """
        # user data
        self.user_id = None  # идентификатор пользователя
        self.user_login = ''  # Логин пользователя
        self.user_name = ''  # ФИО пользователя
        self._user_is_authenticated = False

        # session data
        self.session_key = ''  # идентификатор пользовательской сессии

        # client host data
        self.client_host = ''

    def apply_defaults(self):
        """
        Метод применяет дефолтные значения атрибутов
        """
        self._apply_user_defaults()
        self._apply_session_defaults()
        self._apply_client_host_defaults()

    def _apply_user_defaults(self):
        self.user_id = self.user_id or ThreadData.DEFAULT_USER_ID
        self.user_login = self.user_id or ThreadData.DEFAULT_USER_LOGIN
        self.user_name = self.user_id or ThreadData.DEFAULT_USER_NAME

    def _apply_session_defaults(self):
        self.session_key = self.user_id or ThreadData.DEFAULT_SESSION_KEY

    def _apply_client_host_defaults(self):
        self.client_host = self.client_host or ThreadData.DEFAULT_CLIENT_HOST

    def _apply_anonymous_user(self):
        """
        Проставляет значения, специфичные для анонимного пользователя системы
        """
        self.user_id = ThreadData.ANONYMOUS_USER_ID
        self.user_login = ThreadData.ANONYMOUS_USER_LOGIN
        self.user_name = ThreadData.ANONYMOUS_USER_NAME
        self._user_is_authenticated = False

    def read(self, request=None):
        """
        Читает данные из объекта request
        """
        self.clear()

        if request:
            # читаем данные пользователя
            assert hasattr(request, 'user'), (
                "Для M3CommonMiddleware необходимо, "
                "чтобы был установлен AuthenticationMiddleware Django. "
                "Добавьте в ваш MIDDLEWARE{} настройку "
                "'django.contrib.auth.middleware.AuthenticationMiddleware' "
                "перед 'm3_legacy.middleware.M3CommonMiddleware'"
            ).format("_CLASSES" if settings.MIDDLEWARE is None else "")
            user = request.user
            if user:
                self.user_is_authenticated = is_authenticated(user)
                if self.user_is_authenticated:
                    self.user_id = user.id
                    self.user_login = user.username
                    self.user_name = ('%s %s' % (user.first_name,
                                                 user.last_name)).strip()
                else:
                    self._apply_anonymous_user()
            else:
                self._apply_user_defaults()

            # читаем данные сессии
            if hasattr(request, 'session') and request.session:
                self.session_key = request.session.session_key
            else:
                self._apply_session_defaults()

            if hasattr(request, 'META') and request.META:
                self.client_host = request.META.get('HTTP_X_FORWARDED_FOR', '')
            else:
                self._apply_client_host_defaults()

        return self

    def dump(self):
        """
        Выводит состояние объекта в строку для получения отладочной информации
        """
        str = (
            '''session_key: %s
user_id: %s
user_login: %s
user_name: %s
client_host: %s'''
        ) % (
            self.session_key,
            self.user_id,
            self.user_login,
            self.user_name,
            self.client_host
        )
        return str


def get_thread_data():
    """
    Метод возвращает объект типа ThreadData, который описывает
    текущие thread-local параметры обработки запроса.
    """
    if not hasattr(_thread_locals, 'm3_data'):
        default_data = ThreadData()
        default_data.apply_defaults()
        _thread_locals.m3_data = default_data

    return _thread_locals.m3_data


class M3CommonMiddleware(MiddlewareMixin):
    """
    Middleware общего назначения для проектов на M3.

    Данное middleware должно располагаться ниже
    SessionMiddleware и AuthenticationMiddleware
    """
    def process_request(self, request):
        """
        Обработчик, срабатывающий перед выполнением запроса в прикладном
        приложении. Записываем в thread-locals информацию о
        текущей сессии и пользователе.
        """
        _thread_locals.m3_data = ThreadData()
        _thread_locals.m3_data.read(request)

        _thread_locals.foo = 'foo'


    def _clear(self):
        """
        Очищает информацию в thread-locals о текущей сессии и пользователе
        """
        if hasattr(_thread_locals, 'm3_data'):
            del _thread_locals.m3_data

    def process_response(self, request, response):
        self._clear()
        return response

    def process_exception(self, request, exception):
        self._clear()


class M3SimpleProfileMiddleware(MiddlewareMixin):
    """
    Выводит в отладочный лог время отработки задного запроса
    вместе с полным адресом
    """
    def process_request(self, request):
        request.m3_simple_profile_start_time = datetime.datetime.now()

    def process_response(self, request, response):
        try:
            logger.debug(
                str(
                    datetime.datetime.now() -
                    request.m3_simple_profile_start_time
                ) + ' ' + request.get_full_path())
        except:
            pass

        return response


class AutoLogout(object):
    """
    Отслеживает активность пользователей в системе.
    Если с последнего действия пользователя прошло времени
    больше чем INACTIVE_SESSION_LIFETIME,
    то он выводит пользователя из системы
    """

    session_key = 'app_last_user_activity_time'

    def process_request(self, request):
        # Если проверка отключена
        if settings.INACTIVE_SESSION_LIFETIME == 0:
            return

        # У аутентифицированного пользователя проверяем таймаут,
        # а ананимусов сразу посылаем
        if is_authenticated(request.user):
            last_time = request.session.get(self.session_key, None)
            if last_time is not None:
                delta = datetime.datetime.now() - last_time
                if delta.seconds / 60 > settings.INACTIVE_SESSION_LIFETIME:
                    # После логаута сессия уже другая
                    # и присваивать время не нужно
                    auth.logout(request)
                    return

            # Записываем время последнего запроса
            request.session[self.session_key] = datetime.datetime.now()
