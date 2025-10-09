#coding: utf-8
'''
Хелперы для валидации значений
Created on 20.01.2010

@author: akvarats
'''
from __future__ import absolute_import
from django.db import models
import six

class Validator:
    '''
    Класс, обеспечивающий выполнение валидации объектов
    на корректность их состояния.
    '''
    def __init__(self):
        self.rules = []
    
#------------------------------------------------------------------------------ 
# методы добавления правил валидации
#------------------------------------------------------------------------------ 
    def addrule_notempty(self, value, fail_msg, on_success=None, on_fail=None):
        '''
        Добавляет правило валидации значения на непустоту
        ''' 
        rule = NotEmptyValidationRule()
        rule.value = value
        rule.fail_msg = fail_msg
        rule.callback_on_success = on_success
        rule.callback_on_fail = on_fail
        self.rules.append(rule)
        
    def addrule_failed(self, fail_msg, on_success=None, on_fail=None):
        rule = FailedValidationRule()
        rule.fail_msg = fail_msg
        rule.callback_on_success = on_success
        rule.callback_on_fail = on_fail
        self.rules.append(rule)
        
    def addrule_equal(self, value, fail_msg, on_success=None, on_fail=None):
        rule = NotEqualValidationRule()
        rule.value = value
        rule.fail_msg = fail_msg
        rule.callback_on_success = on_success
        rule.callback_on_fail = on_fail
        self.rules.append(rule)
        
    
    def addrule_unique(self, value, model, field_name,fail_msg, on_success=None, 
                       on_fail=None):
        '''
        Добавляет правило валидации на уникальность заданного поля
        '''
        rule = ModelUniqueField(value, model, field_name)
        rule.value = value
        rule.fail_msg = fail_msg
        rule.callback_on_success = on_success
        rule.callback_on_fail = on_fail
        self.rules.append(rule)
    
        
    #------------------------------------------------------------------------------
    # методы добавления правил валидации 
    #------------------------------------------------------------------------------ 
    def check(self, raise_exception=True):
        result = []
        for rule in self.rules:
            if not rule.check():
                result.append(rule.fail_msg)
                if rule.callback_on_fail:
                    rule.callback_on_fail()
            else:
                if rule.callback_on_success:
                    rule.callback_on_success()
        if result and raise_exception:
            e = ValidationFailed()
            for message in result:
                e.add_error_message(message)
            raise e
            
        return result
        
class BaseValidationRule(object):
    '''
    Базовое правило валидации значений.
    
    Ничего по сути не делает
    '''
    def __init__(self):
        self.value = ''
        self.fail_msg = '' 
        self.callback_on_success = None
        self.callback_on_fail = None
    def check(self):
        return True
        
class NotEmptyValidationRule(BaseValidationRule):
    '''
    Правило валидации значения на непустоту
    '''
    def check(self):
        return True if self.value else False
    
class NotEqualValidationRule(BaseValidationRule):
    '''
    Правило проверяет равны ли значения из списка value между собой.
    Например может пригодиться для сравнения пароля и подтверждения 
    '''
    def check(self):
        assert isinstance(self.value, (list, tuple))
        assert len(self.value) >= 2
        last_value = self.value[0]
        for value in self.value[1:]:
            if last_value != value:
                return False
            last_value = value
        return True

class ModelUniqueField(BaseValidationRule):
    '''
    Проверяет что value нет ни у одной записи в модели.
    Например у нас есть пользователь с мылом и мы хотим убедиться что такого же мыла 
    нет ни у кого больше. Причем проверяемая запись не исключается. 
    '''
    def __init__(self, value, model, field_name):
        super(ModelUniqueField, self).__init__()
        self.value = value
        self.model = model
        self.field_name = field_name
    
    def check(self):
        assert issubclass(self.model, models.Model)
        assert isinstance(self.field_name, str)
        query = self.model.objects.filter(**{self.field_name: self.value})
        if isinstance(self.value, models.Model):
            if self.value.id != None:
                query = query.exclude(id = self.value.id)
        return not query.exists()

class FailedValidationRule(BaseValidationRule):
    '''
    Правило валидации, которое заведомо является неправильным
    '''
    def check(self):
        return False # надо тупо записать текущее сообщение в список ошибок

#===============================================================================
# Исключительная ситуация 
#===============================================================================
class ValidationFailed(Exception):
    '''
    Исключение для ситуаций валидации пользовательских данных
    '''
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.error_messages = [six.text_type(arg) for arg in args] # список ошибок валидации
        
    def add_error_message(self, message):
        self.error_messages.append(message)

    def has_errors(self):
        return self.error_messages

    def __unicode__(self):
        return self.messages_as_string()

    def __str__(self):
        return six.text_type(self).encode("utf-8")

    def messages_as_string(self, line_preffix = '  - ', line_delimiter='\n'):
        '''
        Преобразует self.error_messages в одну строку для отдачи в html
        представление
        '''
        result = ''
        for message in self.error_messages:
            result += line_preffix + message + line_delimiter
        if result:
            result = result[0:len(result)-len(line_delimiter)]
        return result

    def messages_to_html(self):
        return self.messages_as_string(line_preffix = '&nbsp;&nbsp;-&nbsp;', line_delimiter='<br>')
