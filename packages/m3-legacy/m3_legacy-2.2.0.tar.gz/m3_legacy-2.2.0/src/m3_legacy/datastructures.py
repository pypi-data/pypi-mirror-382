#coding:utf-8
'''
Created on 29.03.2010

@author: prefer
'''
from __future__ import absolute_import
import copy
from six.moves import map

class TypedList(list):
    '''
        Вспомогательный класс, перекрывает три метода - добавление (append, insert, extend), изменение и расширение списка
        Атрибут должен быть типом, переданном в качестве параметра type, или соответствовать значению,
        переданному в *aprgs - иначе выводится assert
        Если значение входит в список исключений exceptions, то проверка не производится
    '''
    def __init__(self, type, exceptions=[], on_before_addition=None,
                 on_after_addition=None, on_before_deletion=None,
                 on_after_deletion=None):
        ''' 
        @param type: Тип значений, которые должны находится в списке
        '''
        super(TypedList, self).__init__()
        self._type = type
        self._exceptions = exceptions
        self.on_before_addition = on_before_addition
        self.on_after_addition = on_after_addition
        self.on_before_deletion = on_before_deletion
        self.on_after_deletion = on_after_deletion
        
    def __copy__(self):
        """ Правильное клонирование TypedList, которое copy не может сделать автоматически """
        result = TypedList(
            type = self._type, 
            exceptions = self._exceptions,
            on_before_addition = self.on_before_addition,
            on_after_addition = self.on_after_addition,
            on_before_deletion = self.on_before_deletion,
            on_after_deletion = self.on_after_deletion
        )
        result.extend(self[:])
        return result

    def __deepcopy__(self, memo):
        """ Глубокое клонирование TypedList, которое copy не может сделать автоматически """
        result = TypedList(
            type = self._type, 
            exceptions = self._exceptions,
            on_before_addition = self.on_before_addition,
            on_after_addition = self.on_after_addition,
            on_before_deletion = self.on_before_deletion,
            on_after_deletion = self.on_after_deletion
        )
        result.extend(copy.deepcopy(self[:]))
        return result

    def __setitem__(self, key, value):
        self.__check(value)
        super(TypedList, self).__setitem__(key, value)
 
    def append(self, value):
        self.__check(value)
        self.__do_before_addition(value)
        super(TypedList, self).append(value)
        self.__do_after_addition(value)

    def insert(self, num, value):
        self.__check(value)
        self.__do_before_addition(value)
        super(TypedList, self).insert(num, value)
        self.__do_after_addition(value)
        
    def extend(self, values):
        list(map(self.append, values))

    def remove(self, value):
        if value in self:
            self.__do_before_deletion(value)
        super(TypedList, self).remove(value)
        self.__do_after_deletion(success=True)

    def pop(self, index=-1):
        if 0 <= index < len(self) or -len(self) <= index <= -1:
            self.__do_before_deletion(self[index])
        super(TypedList, self).pop(index)
        self.__do_after_deletion(success=True)

    def clear(self):
        '''
        Очищает список
        '''
        while len(self) > 0:
            self.pop()
        
    def __check(self, value):
        '''
            Функция проверки типа и значения
            Сначало проверяется значение, то есть если значение "Разделитель" = "-" и тд, то дальнейшие проверки не осуществляются
            Иначе проверяется тип объекта.
        '''
        if value not in self._exceptions:
            assert isinstance(value, self._type), 'Type value "%s" isn\'t %s!' % (value, self._type.__name__)

    def __do_before_addition(self, *arg, **kwargs):
        if self.__on_before_addition is not None:
            self.__on_before_addition(*arg, **kwargs)

    def __do_after_addition(self, *arg, **kwargs):
        if self.__on_after_addition is not None:
            self.__on_after_addition(*arg, **kwargs)

    def __do_before_deletion(self, *arg, **kwargs):
        if self.__on_before_deletion is not None:
            self.__on_before_deletion(*arg, **kwargs)

    def __do_after_deletion(self, *arg, **kwargs):
        if self.__on_after_deletion is not None:
            self.__on_after_deletion(*arg, **kwargs)

    @property
    def on_before_addition(self):
        return self.__on_before_addition

    @on_before_addition.setter
    def on_before_addition(self, handler):
        self.__on_before_addition = handler

    @property
    def on_after_addition(self):
        return self.__on_after_addition

    @on_after_addition.setter
    def on_after_addition(self, handler):
        self.__on_after_addition = handler

    @property
    def on_before_deletion(self):
        return self.__on_before_deletion

    @on_before_deletion.setter
    def on_before_deletion(self, handler):
        self.__on_before_deletion = handler

    @property
    def on_after_deletion(self):
        return self.__on_after_deletion

    @on_after_deletion.setter
    def on_after_deletion(self, handler):
        self.__on_after_deletion = handler


class MutableList(list):
    '''
    Список с признаком измененности "changed"
    '''
    def __init__(self, mutable = True, *args, **kwargs):
        super(MutableList, self).__init__(*args, **kwargs)
        self._mutable = mutable
        self.changed = False
    
    def _assert_mutable(self):
        if not self._mutable:
            raise AttributeError("This MutableList instance is immutable")
        self.changed = True
    
    def __setitem__(self, key, value):
        self._assert_mutable()
        super(MutableList, self).__setitem__(key, value)
        
    def append(self, value):
        self._assert_mutable()
        super(MutableList, self).append(value)
    
    def extend(self, values):
        self._assert_mutable()
        super(MutableList, self).extend(values)
    
    def insert(self, num, value):
        self._assert_mutable()
        super(MutableList, self).append(num, value)
