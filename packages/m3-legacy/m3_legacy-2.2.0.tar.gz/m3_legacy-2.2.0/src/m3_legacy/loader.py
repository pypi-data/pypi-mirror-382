# coding: utf-8
'''
Created on 14.04.2010

@author: airat
'''

from __future__ import absolute_import
import codecs
import datetime
import decimal
import re
import string
import time
import uuid
import xml.dom.minidom

from django.db import models
from django.utils.encoding import smart_str
from m3_django_compatibility import atomic
import six
from six.moves import range
from six.moves import zip


try:
    from dbfpy3.dbf import Dbf
except ImportError:
    # Заглушка на случай неустановленного dbfpy
    class Dbf(object):
        def __new__(cls, *args, **kwargs):
            raise RuntimeError(u'dbfpy is not installed!')


class DictNotEmptyException(Exception):
    '''
    Эксепшн, который выбрасывается в случае, если заполняемый справочник не пуст.
    '''
    def __init__(self, model, reason):
        # указывает на модель записи справочника, для которой определилось, что есть записи в базе данных
        self.model = model
        # текстовое описание причины исключения
        self.reason = reason

class DictLoadException(Exception):
    '''
    Эксепшн, который вызывается, если во время загрузки справочника из файла
    возникла какая-либо ошибка.
    '''
    def __init__(self, model, reason, orig_exc_info=None):
        # указывает на модель записи справочника, при загрузки которой возникла ошибка
        # в некоторых случаях(при считывании данных из файла) может быть == None
        self.model = model
        # текстовое описание причины исключения
        self.reason = reason
        #TODO нужно что-то еще сделать с исходным эксепшеном. хотя бы прокинуть дальше value и traceback

def read_simple_CSV_dict_file(filename, comma=','):
    '''
        Чтение данных из файла (формата CSV), где первая строка содержит перечисление
        имен атрибутов, а последующие строки содержат значения для заданных атрибутов для
        каждой записи в порядке, указанном в первой строке.
        Струткура возвращаемого значения аналогична той, что с методом @see read_simple_dict_file(filename)
    '''
    assert isinstance(filename, six.string_types), u"filename must be 'str'"

    attrs = []
    values = []

    try:
        with open(filename, "rb") as f:
            first_string = f.readline()
            first_string = strip_bom(first_string)


            attrs = [item.strip().lower() for item in smart_str(first_string).split(comma)]
            for num, line in enumerate(f, 1):
                row_values = [item.strip() for item in smart_str(line).split(comma)]
                if len(row_values) == len(attrs):
                    values.append(row_values)
                else:
                    raise DictLoadException(None, u'Количество полей не совпадает: строка %s' % num)
    except IOError:
        raise

    return (attrs, values,)

def read_simple_DBF_dict_file(filename, encoding='utf-8',
                              code_field="CODE", name_field="NAME"):
    ''' Чтение данных из файла формата "DBase" (.dbf) '''

    assert isinstance(filename, six.string_types), u"filename must be 'str'"

    attrs = []
    values = []

    try:
        records = Dbf(filename, readOnly=True, new=False)
        if records:
            for k,v in records[0].asDict().items(): # каждая запись - это ассоц. массив, ключи - имена атрибутов
                attrs.append(k)

            for record in records:
                vals_here = []
                for name in attrs:
                    vals_here.append(smart_str(record[name], encoding=encoding))

                values.append(vals_here)

        else:
            raise DictLoadException(None, u'Исходные данные отсутствуют. Пустой DBF-файл')
    except IOError:
        raise
    except TypeError:
        raise

    attrs_lowercase = []
    for attr in attrs:
        if attr not in [code_field, name_field, ]:
            attrs_lowercase.append(attr.strip().lower())
        else:
            if attr == code_field:
                attrs_lowercase.append("code")
            else:
                attrs_lowercase.append("name")

    attrs = attrs_lowercase

    return (attrs, values,)

def read_simple_xml_file(filename, fields={}):
    '''
    Чтение данных из файла формата xml.
    fields: ключ - атрибут в узле, соответствуюший полю в таблице
    значение - поле в таблице
    '''
    assert isinstance(filename, six.string_types), u"filename must be basestring type"

    values = []
    attrs = []
    doc = xml.dom.minidom.parse(filename)
    root_node = doc.childNodes
    if root_node[0]:
        for node in root_node[0].childNodes:
            values_list = []
            for attr in node.attributes._attrs:
                if attr in fields:
                    if not fields[attr] in attrs:
                        attrs.append(fields[attr])
                    values_list.append(smart_str(node.attributes._attrs[attr].nodeValue, encoding=doc.encoding))
            values.append(values_list)
    else:
        raise DictLoadException(None, u'Исходные данные отсутствуют. Пустой XML-файл')

    return (attrs, values,)

def read_simple_dict_file(filename):
    '''
    Выполняет чтение данных из формата простого линейного справочника
    и возвращает записи в виде кортежа со списком значений справочника.
    Пример возвращаемого значения,
    ( ['code', 'name'],
      [ ['Код1','Наименование 1'],
        ['Код2','Наименование 2'],
      ]
    )
    '''

    assert isinstance(filename, six.string_types), u"filename must be 'str'"

    attrs = []
    values = []
    try:
        with open(filename, "rb") as f:
            first_string = f.readline()
            first_string = strip_bom(first_string)
            if first_string.startswith('#'):
                first_string = first_string[1:].strip()
            else:
                raise DictLoadException(None, u'Первая строка скрипта загрузки линейного справочника должна содержать название аттрибутов и начинаться с символа #')

            attrs = [item.strip() for item in smart_str(first_string).split('\t')]
            for num, line in enumerate(f, 1):
                row_values = [item.strip() for item in line.split('\t')]
                if len(row_values) == len(attrs):
                    values.append(row_values)
                else:
                    raise DictLoadException(None, u'Количество полей не совпадает: строка %s' % num)
    except IOError:
        raise

    return (attrs, values,)

def read_tree_dict_file(filename):
    '''
    Выполняет чтение данных из формата иерархического справочнка.
    Пример возвращаемого значение:
    ( ['name'],
      ['code', 'name'],
      [.... описание пока не завершено ..... ]
    )
    '''

    assert isinstance(filename, six.string_types), u"filename must be 'str'"

    # паттерн для строки модели групп
    VALID_BRANCH = '\[\+\](\w| )+'
    tree_attrs = []
    dict_attrs = []

    class StringStruct():
        '''
        Парсит строку: определяет уровень вложенности, значения аттрибутов,
        является ли запись веткой или листом, генерит уникальный id'шник
        '''

        def __init__(self, row_string):
            if row_string == '':
                raise DictLoadException(None ,u'Пустая строка')

            s = row_string.split('\t')
            # Делаем для каждой записи уникальный id'шник
            self.uid = str(uuid.uuid4())[0:16]
            self.parent_uid = None
            self.level = 0
            self.is_leaf = True
            # значения аттрибутов
            self.attrs = None
            for item in s:
                if item == '':
                    self.level += 1
                else:
                    # знак '-' - это обозначение пустого значения, чтобы отличать начало строки от уровней вложенности ветки
                    # (может использоваться только для первого элемента в строке)
                    if item == '-':
                        s[self.level] = ''
                    break
            self.attrs = [ item.strip() for item in s[self.level:]]
            if self.attrs:
                self.is_leaf = not re.match(VALID_BRANCH, self.attrs[0])
                # убираем плюсик в скобках у веток
                if not self.is_leaf:
                    self.attrs[0] = self.attrs[0][3:].strip()
                    if self.attrs[0] == '-':
                        self.attrs[0] = ' '

            else:
                # листьям разрешено не иметь полей
                self.is_leaf = True

    try:
        with open(filename, 'rb') as f:
            lines = f.readlines()
            if len(lines) < 3:
                raise DictLoadException(None, u'В файле должно быть, как минимум, три строки')

            first_string = strip_bom(lines[0])
            if first_string.startswith('#'):
                first_string = first_string[1:].strip()
            else:
                raise DictLoadException(None, u'Первая строка скрипта загрузки иерархического справочника должна содержать название модели групп и начинаться с символа #')

            second_string = lines[1]
            if second_string.startswith('#'):
                second_string = second_string[1:].strip()
            else:
                raise DictLoadException(None, u'Вторая строка скрипта загрузки иерархического справочника должна содержать название аттрибутов модели линейного справочника и начинаться с символа #')

            tree_attrs = [item.strip() for item in smart_str(first_string).split('\t')]
            dict_attrs = [item.strip() for item in smart_str(second_string).split('\t')]
            dict_rows = {}
            tree_rows = {}
            parents = []
            cur_parent = -1
            level = 0
            for num, line in enumerate(lines[2:], 3):
                #пустые строки в файле пропускаются
                if line == '':
                    continue
                struct = StringStruct(line)
                if (struct.level == level) or (struct.level-1 == level):
                    # все нормально, тут ничего не делаем
                    pass
                elif struct.level < level:
                    d = level - struct.level
                    for i in range(d):
                        cur_parent = parents.pop()
                    level -= d
                else:
                    raise DictLoadException(None, u'Уровень вложенности задан неверно: строка %s' % num)

                struct.parent_uid = cur_parent
                if struct.is_leaf:
                    dict_rows[struct.uid] = struct
                else:
                    parents.append(cur_parent)
                    cur_parent = struct.uid
                    level += 1
                    tree_rows[struct.uid] = struct

    except IOError:
        raise

    return (tree_attrs, dict_attrs, tree_rows, dict_rows)


@atomic
def fill_simple_dict(model, data):
    '''
    Выполняет заполнение модели model (тип параметра - classobj) данными data,
    в формате, возвращаемом функцией read_simple_dict_file
    '''

    assert issubclass(model, models.Model), 'model must be subclass of django.db.models.Model'

    if model.objects.all().count() > 0:
        raise DictNotEmptyException(model.__name__, u'Таблица справочника %s не должна содержать записи' % model.__name__)

    fields = dict( (field.name, field,) for field in model._meta.fields)
    attrs = data[0]
    values = data[1]
    for value in values:
        obj = model()
        for attr, val in zip(attrs, value):
            if val != u'None':
                try:
                    if attr in fields:
                        converted = _convert_value(fields[attr], val)
                        setattr(obj, attr, converted)
                except Exception as e:
                    raise DictLoadException(model.__name__, u'Не удалось преобразовать значение: %s' % val)
        try:
            obj.save()
        except Exception as exc:
            raise DictLoadException(model.__name__, u'Не удалось сохранить запись справочника: %s' % string.join(value))


@atomic
def fill_tree_dict(group_model, list_model, group_link, list_link, data):

    assert issubclass(list_model, models.Model), 'model must be subclass of django.db.models.Model'
    assert issubclass(group_model, models.Model), 'model must be subclass of django.db.models.Model'

    if group_model.objects.all().count() > 0:
        raise DictNotEmptyException(group_model.__name__, u'Таблица справочника %s не должна содержать записи' % group_model.__name__)

    if list_model.objects.all().count() > 0:
        raise DictNotEmptyException(list_model.__name__, u'Таблица справочника %s не должна содержать записи' % list_model.__name__)

    tree_attrs = data[0]
    dict_attrs = data[1]
    tree_rows = data[2]
    dict_rows = data[3]
    tree_values = {}

    tree_fields = dict( (field.name, field,) for field in group_model._meta.fields)
    for k,v in tree_rows.items():
        obj = group_model()
        for i in range(len(tree_attrs)):
            try:
                val = _convert_value(tree_fields[str(tree_attrs[i])], v.attrs[i])
            except:
                raise DictLoadException(group_model.__name__, u'Не удалось преобразовать значение: %s' % v.attrs[i])
            setattr(obj, str(tree_attrs[i]), val)
        try:
            obj.save()
        except:
            raise DictLoadException(group_model.__name__, u'Не удалось сохранить запись справочника: %s' % string.join(v.attrs))
        tree_values[k] = (obj, v.parent_uid,)

    for k,v in tree_values.items():
        if v[1] != -1:
            setattr(v[0], group_link, tree_values[v[1]][0])
            try:
                v[0].save()
            except:
                raise DictLoadException(group_model.__name__, u'Не удалось сохранить запись справочника: %s' % string.join(v[0]))

    dict_fields = dict( (field.name, field,) for field in list_model._meta.fields)
    for k,v in dict_rows.items():
        obj = list_model()
        for i in range(len(dict_attrs)):
            if v.attrs[i] != u'None':
                try:
                    val = _convert_value(dict_fields[str(dict_attrs[i])], v.attrs[i])
                except:
                    raise DictLoadException(list_model.__name__, u'Не удалось преобразовать значение: %s' % v.attrs[i])
                setattr(obj, str(dict_attrs[i]), val)

        parent = None if v.parent_uid == -1 else tree_values[v.parent_uid][0]
        setattr(obj, list_link, parent)
        try:
            obj.save()
        except:
            raise DictLoadException(list_model.__name__, u'Не удалось сохранить запись справочника: %s' % string.join(v.attrs, ','))

def strip_bom(s):
    '''
    Убирает от начала строки все символы BOM
    '''
    boms = (codecs.BOM, codecs.BOM32_BE, codecs.BOM32_LE, codecs.BOM64_BE,
            codecs.BOM64_LE, codecs.BOM_BE, codecs.BOM_LE, codecs.BOM_UTF16,
            codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE, codecs.BOM_UTF32,
            codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE, codecs.BOM_UTF8,)
    return s.lstrip(''.join(boms))

def _convert_value(field, value):
    if not value:
        return None
    converted_value = value
    if isinstance(field, models.AutoField):
        pass
    elif isinstance(field, models.BooleanField):
        value = value.lower()
        if value == 'true' or value == '1':
            converted_value = True
        elif value == 'false' or value == '0':
            converted_value = False
        else:
            raise Exception()
    elif isinstance(field, models.CharField):
        pass
    elif isinstance(field, models.CommaSeparatedIntegerField):
        pass
    elif isinstance(field, models.DateTimeField):
        if '-' in value:
            ts = time.strptime(value, '%Y-%m-%d %H.%M.%S')
        else:
            ts = time.strptime(value, '%d.%m.%Y %H.%M.%S')
        converted_value = datetime.datetime(*(ts[0:6]))
    elif isinstance(field, models.DateField):
        if '-' in value:
            ts = time.strptime(value, '%Y-%m-%d')
        else:
            ts = time.strptime(value, '%d.%m.%Y')
        converted_value = datetime.date(*(ts[0:3]))
    elif isinstance(field, models.DecimalField):
        converted_value = decimal.Decimal(value)
    elif isinstance(field, models.EmailField):
        pass
    elif isinstance(field, models.FileField):
        pass
    elif isinstance(field, models.FilePathField):
        pass
    elif isinstance(field, models.FloatField):
        converted_value = float(value.replace(',', '.'))
    elif isinstance(field, models.ImageField):
        pass
    elif isinstance(field, models.IntegerField):
        converted_value = int(value)
    elif isinstance(field, models.IPAddressField):
        pass
    elif isinstance(field, models.NullBooleanField):
        value = value.lower()
        if value == 'true':
            converted_value = True
        elif value == 'false':
            converted_value = False
        elif value in ['null', 'none', '']:
            converted_value = None
    elif isinstance(field, models.PositiveIntegerField):
        converted_value = int(value)
    elif isinstance(field, models.PositiveSmallIntegerField):
        converted_value = int(value)
    elif isinstance(field, models.SlugField):
        pass
    elif isinstance(field, models.SmallIntegerField):
        converted_value = int(value)
    elif isinstance(field, models.TextField):
        pass
    elif isinstance(field, models.TimeField):
        ts = time.strptime(value, '%H.%M.%S')
        converted_value = datetime.time(*(ts[3:3]))
    elif isinstance(field, models.URLField):
        pass
    elif isinstance(field, models.XMLField):
        pass

    return converted_value
