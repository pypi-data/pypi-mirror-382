# coding: utf-8

from __future__ import absolute_import
import logging.handlers
import os
import sys
import traceback

from django.http import HttpResponseServerError, HttpRequest
from django.template.loader import render_to_string
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage
from django.utils.html import linebreaks
from django.utils.encoding import force_str
import six

__all__ = ['init_logging', 'catch_error_500',
           'info', 'error', 'debug', 'warning']


def init_logging(logs_path):
    '''
    Инициализация питоновского логирования. Срабатывает только один раз.
    Каждый error level записывается в свой лог.
    Нужно добавлять в settings.py или manage.py
    '''
    if hasattr(logging, "m3_set_up_done"):
        return

    if not os.path.exists(logs_path):
        os.mkdir(logs_path)

    loggers = [
        ('root', logging.NOTSET, 'root.log'),
        ('error_logger', logging.ERROR, 'error.log'),
        ('info_logger', logging.INFO, 'info.log'),
        ('debug_logger', logging.DEBUG, 'debug.log'),
        ('warning_logger', logging.DEBUG, 'warning.log')
    ]
    formatter = logging.Formatter("[%(asctime)s] %(message)s")
    formatter.datefmt = '%Y-%m-%d %H:%M:%S'
    for lname, level, fname in loggers:
        t = logging.getLogger(lname)
        t.setLevel(level)
        handler = logging.handlers.TimedRotatingFileHandler(
            os.path.join(logs_path, fname), when='D', encoding='utf-8')
        handler.setFormatter(formatter)
        t.addHandler(handler)

    logging.m3_set_up_done = True


def get_session_info(request):
    '''
    Возвращает строку для лога с информацией о запросе
    '''
    if (request is None) or (not isinstance(request, HttpRequest)):
        return ''
    # Адрес запроса
    result = 'URL: ' + request.get_full_path() + ' (' + request.method + ')'
    # Юзер
    if hasattr(request, 'user'):
        user = request.user
        if user and user.is_authenticated():
            result += ' - ' + user.email + ', ' + user.get_full_name()
    return result + '. '

#====================== ФУНКЦИИ АНАЛОГИЧНЫЕ LOGGING =====================
# Если передать именованный аргумент request = ... , то к сообщению будет
# добавлена информация о запросе
#========================================================================


def info(msg, *args, **kwargs):
    log = logging.getLogger('info_logger')
    msg = get_session_info(kwargs.get('request', None)) + msg
    log.info(msg)

    # Отправка на почту
    send_mail_log(msg, 'INFO')


def error(msg, *args, **kwargs):
    log = logging.getLogger('error_logger')
    msg = get_session_info(kwargs.get('request', None)) + msg
    log.error(msg)

    # Отправка на почту
    send_mail_log(msg, 'ERROR')


def debug(msg, *args, **kwargs):
    '''
    Выводит информацию в debug-log только в случае включенного режима отладки
    '''
    from django.conf import settings

    if settings.DEBUG:
        log = logging.getLogger('debug_logger')
        msg = get_session_info(kwargs.get('request', None)) + msg
        log.debug(msg)


def exception(msg='', *args, **kwargs):
    # Не желаемые ключи логирования
    black_list = [
        'win',  # Запрос браузера
        'request',  # Запрос в БД (sql)
        'query'
    ]

    log = logging.getLogger('error_logger')
    msg = get_session_info(kwargs.get(
        'request', None)) + 'Message: ' + msg + '\n'

    # FIXME: Отрефаторить нахер!!
    exception_info = sys.exc_info()
    try:
        e_type, e_value, e_traceback = exception_info
        e_vars = e_traceback.tb_frame.f_locals
        res = [u'Variables:\n']

        def append(key, val, rjust):
            res.append(
                u'%s: %s\n'.rjust(rjust) % (
                    key,
                    (force_unicode(val)
                        if isinstance(val, six.string_types) else val)))

        if e_traceback.tb_frame.f_code.co_name != '<module>':
            for key, val in e_vars.items():
                if key in black_list:
                    continue

                append(key, val, rjust=6)
                if hasattr(val, '__dict__'):
                    for obj_key, obj_val in val.__dict__.items():
                        if obj_key[0] != '_' and obj_key not in black_list:
                            append(obj_key, obj_val, rjust=12)
        else:
            res = []

        e_vars_str = ''.join(res)
        tb = traceback.format_exception(e_type, e_value, e_traceback)

        err_message = u'\n %s %s %s' % (
            force_unicode(msg),
            force_unicode(u''.join(tb)),
            force_unicode(e_vars_str)
        )
        log.error(err_message)

        # Отправка на почту
        send_mail_log(err_message, e_type.__name__)

    except:
        _old_good_exception(msg, exception_info, *args, **kwargs)


def _old_good_exception(msg, exception_info, *args, **kwargs):
    """
    Старый добрый способ вывода ошибки, без переменных, зато надежный.
      msg - гневное сообщение разработчикам
      exception_info - информация о оригинальной ошибке
    """
    log = logging.getLogger('error_logger')
    try:
        tb = traceback.format_exception(*exception_info)
        log.error(
            force_unicode(get_session_info(kwargs.get('request')) + msg) +
            '\n' + u''.join(tb)
        )
    except:
        try:
            log.error(force_unicode(msg) + '\n')
        except:
            log.error(u'Некорректная работа логгера')


def warning(msg, *args, **kwargs):
    log = logging.getLogger('warning_logger')
    msg = get_session_info(kwargs.get('request', None)) + msg
    log.warning(msg)

    send_mail_log(msg, 'WARN')


def catch_error_500(request, *args, **kwargs):
    '''
    Функция для перехвата ошибок сервера в боевом режиме.
    Возвращает страницу 500 определенную пользователем.
    '''
    exception(get_session_info(request), exc_info=True)
    return HttpResponseServerError(render_to_string("500.html"))

#=========================================================================


def send_mail_log(msg, err_name='', level=''):
    '''
    Дополнительное письмо с логом на почту администратора
    '''
    from django.conf import settings

    emails_admin = getattr(settings, 'EMAIL_ERRORLOG_ADMIN', False)
    email_from = getattr(settings, 'EMAIL_ADDRESS_FROM', "")

    if emails_admin and email_from:
        try:
            if isinstance(emails_admin, list):
                email_list = [emails_admin, ]
            elif isinstance(emails_admin, six.string_types):
                email_list = emails_admin.split(',')

            conn = get_connection(
                auth_user=settings.EMAIL_HOST_USER,
                auth_password=settings.EMAIL_HOST_PASSWORD
            )

            # uname есть только по nix системами,
            # на остальных смотрим переменную
            # среды os.getenv('USERNAME')
            # 2-ой параметр - имя системы
            uname = os.uname()[1] if hasattr(os, 'uname') and callable(
                os.uname) else os.getenv('USERNAME')

            msg = linebreaks(msg)
            d = {'body': msg, 'from_email': email_from, 'to': email_list,
                 'subject': u'Логер - %s - %s %s' % (uname, level, err_name)}
            message = EmailMessage(**d)
            message.content_subtype = "html"
            # TODO: на этом моменте сильно тормозит,
            # если есть проблемы с доставкой письма
            # типа нет связи с почтовым сервером
            # или неверный логин и(или) пароль
            # с другой стороны, ускорение отработки доставки писем
            # (в отдельном потоке) приводит к отказу
            # на почтовом сервере
            # (слишком частые !неудачные! попытки соединения)
            # и он вообще все блочит!
            conn.send_messages([message, ])
        except:
            log = logging.getLogger('error_logger')
            msg = 'Error sending e-mail\n'
            log.error(msg)
