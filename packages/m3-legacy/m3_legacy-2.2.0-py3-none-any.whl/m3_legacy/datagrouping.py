# coding:utf-8
'''
Created on 14.04.2011

@author: kirov
'''
from __future__ import (
    absolute_import,
)

import codecs
import csv
import os
import uuid
from functools import (
    cmp_to_key,
)

import six
from django.db.models import (
    Avg,
    Count,
    Max,
    Min,
    Q,
    Sum,
)
from six.moves import (
    range,
)

from m3_legacy import (
    compare,
)
from m3_legacy.config import (
    get_downloads_dir,
    get_downloads_url,
)


try:
    import xlwt
except ImportError:
    class FakeXlwt(object):
        def __getattr__(self, *args):
            raise RuntimeError(u'xlwt is not installed!')
    xlwt = FakeXlwt()


class UnicodeWriter:

    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = six.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([six.text_type(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class RecordProxy(object):

    '''
    Прокси объект записи отображающей группировку
    '''
    def __init__(self, *args, **kwargs):
        self.id = 0  # ID записи в базе
        self.index = 0  # индекс записи в раскрытом дереве (заполняется при выводе)
        self.lindex = 0  # индекс записи на уровене (заполняется при выводе)
        self.indent = 0  # уровень (заполняется при выводе)
        self.is_leaf = False  # признак конечной записи (больше не раскрывается) (заполняется при выводе)
        self.expanded = False  # признак что элемент развернут (заполняется при выводе)
        self.count = 0  # количество дочерних узлов, если они есть
        self.grouped = []
            # Список атрибутов, по которым происходит группировка
        self.init_component(*args, **kwargs)

    def init_component(self, *args, **kwargs):
        '''
        Заполняет атрибуты экземпляра значениями в kwargs,
        если они проинициализированы ранее
        '''
        for k, v in kwargs.items():
            assert k in dir(self) and not callable(getattr(self, k)), \
                'Instance attribute "%s" should be defined in class "%s"!' \
                % (k, self.__class__.__name__)
            self.__setattr__(k, v)

    def load(self, data):
        '''
        Загрузка записи в объект
        '''
        pass

    def calc(self):
        '''
        Пост-обработка записи, когда все реквизиты заполнены
        '''
        pass


class DictToRecordProxy(RecordProxy):
    """
    Прокси объект для данных, переданных в виде словаря
    """
    def load(self, data):
        """
        Копирует все записи словаря в атрибуты объекта
        """
        self.__dict__.update(data)


class GroupingRecordProvider(object):

    '''
    Базовый класс провайдера данных
    '''
    proxy_class = RecordProxy
    data_source = None
    count_totals = False
    aggregates = {}
    xls_style = {}

    def __init__(
            self, proxy=None, data=None, totals=None,
            aggregates=None, detail_attrs_map=None):
        if proxy:
            self.proxy_class = proxy
        if data is not None:
            self.data_source = data
        if totals is not None:
            self.count_totals = totals
        if aggregates is not None:
            self.aggregates = aggregates

        # Словарь, определяющий дополнительные поля,
        # которые добавляются в узловые записи,
        # создаваемые самим провайдером.
        # Они могут пригодиться для последующей обработки узлов.
        # Например, detail_attrs_map={'a_name': 'a_id', 'b_name': 'b_id'}
        # Если группировка будет по полям a_name и b_name,
        # то вместе с ними будет добавлены a_id и b_id.
        self.detail_attrs_map = detail_attrs_map or {}

    def get_data(self, *args, **kwargs):
        return self.data_source

    def getattr(self, obj, attr):
        """
        Получить атрибут объекта или элемент словаря
        """
        if isinstance(obj, dict):
            if attr in obj:
                return obj[attr]
            else:
                return None
        else:
            if hasattr(obj, attr):
                return getattr(obj, attr)
            else:
                return None

    def setattr(self, obj, attr, value):
        """
        Установить атрибут объекта или элемент словаря
        """
        if isinstance(obj, dict):
            obj[attr] = value
        else:
            setattr(obj, attr, value)

    def calc(self, obj):
        """
        Вычислить остальные атрибуты объекта или словаря
        """
        if isinstance(obj, dict):
            pass
        else:
            if hasattr(obj, 'calc') and callable(obj.calc):
                obj.calc()

    def load(self, destination, source):
        """
        Загрузка объекта destination из атрибутов объекта source
        """
        EXCLUDED = ('index', 'lindex', 'indent',
                    'is_leaf', 'expanded', 'count')
        if isinstance(destination, dict):
            for attr in destination:
                if not attr in EXCLUDED:
                    if isinstance(source, dict):
                        if attr in source:
                            destination[attr] = source[attr]
                    else:
                        if hasattr(source, attr):
                            destination[attr] = getattr(source, attr)
        else:
            if hasattr(destination, 'load') and callable(destination.load):
                destination.load(source)

    def create_record(self, *args, **kwargs):
        if isinstance(self.proxy_class, dict):
            rec = self.proxy_class.copy()
            rec['index'] = 0
            rec['lindex'] = 0
            rec['indent'] = 0
            rec['is_leaf'] = False
            rec['expanded'] = False
            rec['count'] = 0
            return rec
        else:
            return self.proxy_class(*args, **kwargs)

    def reader(self, grouped, offset, level_index, level_keys, begin, end, aggregates, sorting):
        pass

    def counter(self, grouped, level_index, level_keys, expandedItems):
        pass

    def indexer(self, grouped, level_index, level_keys, expandedItems, aggregates, sorting):
        pass

    def get_elements(self, begin, end, grouped, expanded, sorting):
        '''
        Основной метод получения данных
        '''
        return self.__get_elements(grouped, begin, 0, {'count': -1, 'id': -1, 'expandedItems': expanded}, begin, end, [], self.aggregates, sorting)

    def __get_elements(self, grouped, offset, level_index, level, begin, end, keys, aggregates, sorting):
        res = []
        all_out = False  # признак того, что все необходимые элементы выведены, идет подсчет общего количества открытых элементов
        # print 'get_elements(): grouped=%s, offset=%s, level_index=%s,
        # level=%s, begin=%s, end=%s, keys=%s' % (grouped, offset, level_index,
        # level, begin, end, keys)

        # необходимо узнавать индекс элемента с кодом exp['id'] в текущем уровне, при текущей сортировке и располагать элементы соответственно
        if 'items' not in level:
            level['items'] = self.indexer(grouped, level_index, keys + [level[
                                          'id']] if level['id'] != -1 else [], level['expandedItems'], aggregates, sorting)
            removeExpandedItems = []
            for exp in level['expandedItems']:
                if exp['id'] in level['items']:
                    exp['index'] = level['items'].index(exp['id'])
                else:
                    # развернутый элемент отсутствует в уровне (видимо фильтр сработал, или что-то еще) - что делать?!
                    removeExpandedItems.append(exp)

            for exp in removeExpandedItems:
                level['expandedItems'].remove(exp)

            # теперь выстроим в порядке индексов
            exp_sort = sorted(level['expandedItems'], key=lambda x: x['index'])
            level['expandedItems'] = exp_sort

        # пройдемся по развернутым элементам
        i = 0
        while i < len(level['expandedItems']):
            exp = level['expandedItems'][i]

            # на текущий момент необходимо вычислить количество дочерних элементов
            if exp['count'] == -1:
                exp['count'] = self.counter(grouped, level_index + 1, (keys + [level[
                                            'id']] if level['id'] != -1 else []) + [exp['id']], exp['expandedItems'])

            if all_out or not exp['count']:
                i = i + 1
                continue

            # 1) может диапазон уже пройден
            if end <= exp['index']:
                # выдать диапазон с begin по end
                # print '1) диапазон уже пройден'
                # print 'offset=%s, begin=%s, end=%s, exp=%s, keys=%s' %
                # (offset, begin, end, exp, keys)
                list = self.reader(grouped, offset + len(res) - begin, level_index, keys + [
                                   level['id']] if level['id'] != -1 else [], begin, end, aggregates, sorting)
                # если выдали раскрытый элемент, то установим у него признак раскрытости
                if end == exp['index']:
                    self.setattr(list[-1], 'expanded', True)
                res.extend(list)
                # переходим к след. развернутому элементу
                i = i + 1
                all_out = True
                continue

            # 2) может интервал переходит с предыдущего
            if begin <= exp['index'] and end > exp['index']:
                # print '2) интервал переходит с предыдущего'
                # print 'offset=%s, begin=%s, end=%s, exp=%s, keys=%s' % (offset, begin, end, exp, keys)
                # выдадим известный диапазон, а остальное продолжим искать
                list = self.reader(grouped, offset + len(res) - begin, level_index, keys + [level[
                                   'id']] if level['id'] != -1 else [], begin, exp['index'], aggregates, sorting)
                # если выдали раскрытый элемент, то установим у него признак раскрытости
                self.setattr(list[-1], 'expanded', True)
                res.extend(list)
                begin = exp['index'] + 1
                continue

            # 3) попадаем ли мы в раскрытый уровень
            if begin >= exp['index'] and end <= exp['index'] + exp['count']:
                # print '3) мы попадаем в раскрытый уровень'
                # print 'offset=%s, begin=%s, end=%s, exp=%s, keys=%s' % (offset, begin, end, exp, keys)
                # переходим искать на след. уровень
                list, total = self.__get_elements(grouped, offset + len(res), level_index + 1, exp, begin - exp[
                                                  'index'] - 1, end - exp['index'] - 1, keys + [level['id']] if level['id'] != -1 else [], aggregates, sorting)
                res.extend(list)
                # переходим к след. развернутому элементу
                i = i + 1
                all_out = True
                continue

            # 4) если частично попадаем в раскрытый
            if begin <= exp['index'] + exp['count'] and end > exp['index'] + exp['count']:
                # print '4) частично попадаем в раскрытый'
                # print 'offset=%s, begin=%s, end=%s, exp=%s, keys=%s' % (offset, begin, end, exp, keys)
                # часть переведем искать на след. уровень, остальное продолжим
                list, total = self.__get_elements(grouped, offset + len(res), level_index + 1, exp, begin - exp[
                                                  'index'] - 1, exp['count'] - 1, keys + [level['id']] if level['id'] != -1 else [], aggregates, sorting)
                res.extend(list)
                delta = end - begin - len(list)
                begin = exp[
                    'index'] + 1  # поднимем нижнюю границу до следующего после текущего элемента
                end = begin + \
                    delta  # end - len(list) # сократим верхнюю границу на количество выданных элементов
                i = i + 1
                continue

            # 6) если еще не дошли
            if begin > exp['index'] + exp['count']:
                # print '6) если еще не дошли'
                # print 'offset=%s, begin=%s, end=%s, exp=%s, keys=%s' %
                # (offset, begin, end, exp, keys)
                begin = begin - exp['count']
                end = end - exp['count']

            # переходим к след. развернутому элементу
            i = i + 1

        if level['count'] == -1:
            level['count'] = self.counter(
                grouped, level_index, keys, level['expandedItems'])

        # 5) выдадим из уровеня всё что осталось
        if not all_out and begin <= end and begin < level['count']:
            # print '5) выдадим из уровеня всё что осталось'
            # print 'begin=%s, end=%s, level[count]=%s, len(res)=%s, offset=%s,
            # keys=%s' % (begin,end,level['count'], len(res), offset, keys)
            if end > level['count'] - 1:
                end = level['count'] - 1
            list = self.reader(grouped, offset + len(res) - begin, level_index, keys + [
                               level['id']] if level['id'] != -1 else [], begin, end, aggregates, sorting)
            res.extend(list)

        # можно уже не считать total выше
        total_len = level['count']

        # print 'get_elements()= total=%s, res_count=%s' % (total_len,
        # len(res))

        # если это самый первый уровень и нужно считать общие итоги, то посчитаем выдадим
        if level_index == 0 and self.count_totals:
            totals = self.reader(grouped, 0, -1, [], 0, 1, aggregates, sorting)
            return (res, (total_len, totals))
        else:
            return (res, total_len)

    def get_export_group_text(self, item, grouped_col_name):
        '''
        Форматирование колонки группировки
        '''
        indent_str = "   " * self.getattr(item, 'indent')
        value = self.getattr(item, 'id')
        return "%s %s: %s (%s)" % (indent_str, grouped_col_name, value, self.getattr(item, 'count'))

    EXPORT_XLS = 'xls'
    EXPORT_CSV = 'csv'

    def export_to_file(self, title, columns, total, grouped, expanded, sorting, export_type=EXPORT_XLS):
        if export_type == self.EXPORT_XLS:
            return self.export_to_xls(title, columns, total, grouped, expanded, sorting)
        elif export_type == self.EXPORT_CSV:
            return self.export_to_csv(title, columns, total, grouped, expanded, sorting)
        else:
            return None

    def _tune_xls_worksheet(self, worksheet):
        """Здесь можно задать нужные параметры страницы."""
        return worksheet

    def export_to_xls(self, title, columns, total, grouped, expanded, sorting, params=None):
        """Выгрузка таблицы в xls-файл."""

        w = xlwt.Workbook()
        ws = w.add_sheet('grid')
        ws = self._tune_xls_worksheet(ws)

        title_style = xlwt.easyxf(
            self.xls_style.get('title') or
            "font: bold on, height 400;"
        )
        header_style = xlwt.easyxf(
            self.xls_style.get('header') or
            "font: bold on, color-index white;"
            "borders: left thick, right thick, top thick, bottom thick;"
            "pattern: pattern solid, fore_colour gray80;"
        )
        data_style = xlwt.easyxf(
            self.xls_style.get('data') or
            "borders: left thin, right thin, top thin, bottom thin;"
        )

        col_count = 0
        total_width = 0
        for column in columns:
            if not column.get("hidden"):
                col_count += 1
                total_width += column.get("width")

        page_width = 30000
        ws.write_merge(0, 0, 0, col_count - 1, title, title_style)
        ws.row(0).height = 500
        columns_cash = []
        columns_title = {}
        index = 0
        for column in columns:
            if not column.get("hidden"):
                ws.write(1, index, column.get('header'), header_style)
                ws.col(index).width = column.get(
                    "width") * page_width // total_width
                columns_title[column["data_index"]] = column.get('header')
                columns_cash.append(column["data_index"])
                index += 1
        # запросим все данные
        data, total = self.get_elements(0, total, grouped, expanded, sorting)
        # вывод данных
        for item in data:
            for idx, column in enumerate(columns_cash):
                # значит это группировочная колонка
                if column == "grouping":
                    if self.getattr(item, 'is_leaf'):
                        value = ""
                    else:
                        col = grouped[self.getattr(item, 'indent')]
                        col_name = columns_title[col]
                        value = self.get_export_group_text(item, col_name)
                    ws.write(self.getattr(item, 'index') + 2, idx, value, data_style)
                else:
                    value = self.getattr(item, column)
                    ws.write(self.getattr(item, 'index') + 2, idx, value, data_style)
        # вывод итогов
        if not isinstance(total, six.integer_types):
            total_row = total[1]
            for idx, column in enumerate(columns_cash):
                if column == "grouping":
                    value = ""
                else:
                    value = self.getattr(total_row, column)
                ws.write(total[0] + 2, idx, value, header_style)

        params = params or {}
        dst_file_name = params.get('dst_file_name', '')
        is_need_to_create_folder = params.get('is_need_to_create_folder', False)

        if not dst_file_name:
            base_name = str(uuid.uuid4())[0:16] + '.xls'
        else:
            base_name = dst_file_name

        if is_need_to_create_folder:
            uid = str(uuid.uuid4())[:8]
            os.mkdir(f'{get_downloads_dir()}/{uid}')
            base_name = f'{uid}/{base_name}'

        xls_file_abs = os.path.join(get_downloads_dir(), base_name)
        w.save(xls_file_abs)
        join = lambda pieces: '/'.join(s.strip('/') for s in pieces)
        url = join([get_downloads_url(), base_name])

        return url

    def export_to_csv(self, title, columns, total, grouped, expanded, sorting):
        '''
        выгрузка таблицы в csv-файл
        '''
        base_name = str(uuid.uuid4())[0:16] + '.csv'
        file_abs = os.path.join(get_downloads_dir(), base_name)
        # ws = UnicodeWriter(open(file_abs, 'wb'), delimiter='|',
        # quotechar='"', quoting=csv.QUOTE_MINIMAL)
        ws = UnicodeWriter(open(
            file_abs, 'wb'), delimiter=';', encoding="cp1251")
        col_count = 0
        for column in columns:
            if not column.get("hidden"):
                col_count += 1

        ws.writerow([title])
        columns_cash = []
        columns_title = {}
        index = 0
        row = []
        for column in columns:
            if not column.get("hidden"):
                row.append(column.get('header'))
                columns_title[column["data_index"]] = column.get('header')
                columns_cash.append(column["data_index"])
                index += 1
        ws.writerow(row)
        # запросим все данные
        data, total = self.get_elements(0, total, grouped, expanded, sorting)
        # вывод данных
        for item in data:
            row = []
            for idx, k in enumerate(columns_cash):
                # значит это группировочная колонка
                if k == "grouping":
                    if self.getattr(item, 'is_leaf'):
                        v = ""
                    else:
                        col = grouped[self.getattr(item, 'indent')]
                        col_name = columns_title[col]
                        v = self.get_export_group_text(item, col_name)
                    row.append(v if v else '')
                else:
                    v = self.getattr(item, k)
                    row.append(v if v else '')
            ws.writerow(row)
        # вывод итогов
        if not isinstance(total, six.integer_types):
            row = []
            total_row = total[1]
            for idx, k in enumerate(columns_cash):
                if k == "grouping":
                    v = ""
                else:
                    v = self.getattr(total_row, k)
                row.append(v if v else '')
            ws.writerow(row)

        join = lambda pieces: u'/'.join(s.strip('/') for s in pieces)
        url = join([get_downloads_url(), base_name])
        return url


class GroupingRecordModelProvider(GroupingRecordProvider):

    '''
    Провайдер для модели
    '''
    def reader(self, grouped, offset, level_index, level_keys, begin, end, aggregates, sorting):
        return self.__read_model(grouped, offset, level_index, level_keys, begin, end, aggregates, sorting)

    def __read_model(self, grouped, offset, level_index, level_keys, begin, end, aggregates, sorting):
        '''
        вывод элементов дерева группировок в зависимости от уровня, ключевых элементов и интервала в уровне
        '''
        # построим ключ кэша
        # cache_key = '%s__%s__%s__%s__%s__%s' % (','.join(grouped), offset, level_index, ','.join(level_keys), begin, end)
        # if cache_key in out_cache.keys():
        #    print 'cached data...........'
        #    return out_cache[cache_key]

        # специальный режим, когда считается общий итог по всем записям - не важна сортировка и группировка
        if level_index == -1:
            aggr = []
            # будем считать агрегаты
            for agg in aggregates.keys():
                agg_type = aggregates[agg]
                if agg_type == 'sum':
                    aggr.append(Sum(agg))
                elif agg_type == 'count':
                    aggr.append(Count(agg))
                elif agg_type == 'min':
                    aggr.append(Min(agg))
                elif agg_type == 'max':
                    aggr.append(Max(agg))
                elif agg_type == 'avg':
                    aggr.append(Avg(agg))
            i = self.get_data().aggregate(*aggr)
            item = self.create_record()
            item.is_leaf = False
            item.index = None
            item.id = None
            item.indent = None
            item.lindex = None
            for agg in aggregates.keys():
                agg_type = aggregates[agg]
                if agg_type == 'sum':
                    setattr(item, agg, i[agg + '__sum'])
                elif agg_type == 'count':
                    setattr(item, agg, i[agg + '__count'])
                elif agg_type == 'min':
                    setattr(item, agg, i[agg + '__min'])
                elif agg_type == 'max':
                    setattr(item, agg, i[agg + '__max'])
                elif agg_type == 'avg':
                    setattr(item, agg, i[agg + '__avg'])
            item.calc()
            return item

        # print 'read_model(): grouped=%s, offset=%s, level_index=%s,
        # level_keys=%s, begin=%s, end=%s' % (grouped, offset, level_index,
        # level_keys, begin, end)
        res = []
        if grouped:
            # для всех группировочных элементов будут использоваться ключи
            # если берется уровень больший, чем количество группировок, то выдаем просто записи
            if level_index >= len(grouped):
                field = None
            else:
                field = grouped[level_index]

            filter = None
            for lev in range(0, level_index):
                lev_field = grouped[lev]
                key = level_keys[lev]
                if filter:
                    filter = filter & Q(**{lev_field: key})
                else:
                    filter = Q(**{lev_field: key})
            aggr = []
            if field:
                # будем считать агрегаты
                for agg in aggregates.keys():
                    agg_type = aggregates[agg]
                    if agg_type == 'sum':
                        aggr.append(Sum(agg))
                    elif agg_type == 'count':
                        aggr.append(Count(agg))
                    elif agg_type == 'min':
                        aggr.append(Min(agg))
                    elif agg_type == 'max':
                        aggr.append(Max(agg))
                    elif agg_type == 'avg':
                        aggr.append(Avg(agg))
            if filter:
                if field:
                    if aggr:
                        query = self.get_data().filter(filter).values(
                            field).annotate(*aggr).annotate(count=Count("id"))
                    else:
                        query = self.get_data().filter(filter).values(
                            field).annotate(count=Count("id"))
                else:
                    query = self.get_data().filter(filter)
            else:
                if field:
                    if aggr:
                        query = self.get_data().values(field).annotate(
                            *aggr).annotate(count=Count("id"))
                    else:
                        query = self.get_data().values(
                            field).annotate(count=Count("id"))
                else:
                    query = self.get_data()

            # сортировка
            sort_fields = []
            # оставлено для совместимости
            if isinstance(sorting, dict) and list(sorting.keys()):
                for sort_field, sort_dir in six.iteritems(sorting):
                    #необходимо исключить из сортировки поля, которые не входят в aggr, иначе по ним будет сделана ненужная группировка
                    if sort_field in list(aggregates.keys()) or sort_field == field or not field:
                        if sort_field in list(aggregates.keys()) and field:
                            # необходимо добавить суффикс к полю, которое в аггрегатах, иначе сортировать будет не по тому что надо :)
                            sort_field = sort_field + '__' + aggregates[sort_field]
                        if sort_dir == 'DESC':
                            sort_fields.append('-' + sort_field)
                        else:
                            sort_fields.append(sort_field)
            # изначальная ошибка была передавать сортировку в dict - надо было сразу в list
            elif isinstance(sorting, list) and sorting:
                for sort_field, sort_dir in sorting:
                    #необходимо исключить из сортировки поля, которые не входят в aggr, иначе по ним будет сделана ненужная группировка
                    if sort_field in list(aggregates.keys()) or sort_field == field or not field:
                        if sort_field in list(aggregates.keys()) and field:
                            # необходимо добавить суффикс к полю, которое в аггрегатах, иначе сортировать будет не по тому что надо :)
                            sort_field = sort_field + '__' + aggregates[sort_field]
                        if sort_dir == 'DESC':
                            sort_fields.append('-' + sort_field)
                        else:
                            sort_fields.append(sort_field)
            else:
                # нет заданной сортировки, отсортируем по этому полю
                if field:
                    sort_fields.append(field)
            if sort_fields:
                query = query.order_by(*sort_fields)

            # теперь выведем запрошенные элементы уровня
            index = 0
            for i in query.all()[begin:end + 1]:
                if field:
                    item = self.create_record()
                    item.is_leaf = False
                    item.index = offset + index + begin
                    item.id = i[field]
                    item.indent = level_index
                    item.lindex = index + begin
                    item.count = i['count']
                    # установим все атрибуты из группировки
                    for lev in range(0, level_index):
                        lev_field = grouped[lev]
                        key = level_keys[lev]
                        setattr(item, lev_field, key)
                    setattr(item, field, i[field])

                    for agg in aggregates.keys():
                        agg_type = aggregates[agg]
                        if agg_type == 'sum':
                            setattr(item, agg, i[agg + '__sum'])
                        elif agg_type == 'count':
                            setattr(item, agg, i[agg + '__count'])
                        elif agg_type == 'min':
                            setattr(item, agg, i[agg + '__min'])
                        elif agg_type == 'max':
                            setattr(item, agg, i[agg + '__max'])
                        elif agg_type == 'avg':
                            setattr(item, agg, i[agg + '__avg'])
                    item.calc()
                else:
                    item = self.create_record()
                    item.is_leaf = True
                    item.index = offset + index + begin
                    item.indent = level_index
                    item.lindex = index + begin
                    item.load(i)
                    item.calc()
                res.append(item)
                index = index + 1
        else:
            # вывести без группировки
            index = 0
            query = self.get_data()
            # оставлено для совместимости
            if isinstance(sorting, dict) and list(sorting.keys()):
                order = []
                for sort_field, sort_dir in six.iteritems(sorting):
                    if sort_dir == 'DESC':
                        order.append('-' + sort_field)
                    else:
                        order.append(sort_field)
                query = query.order_by(*order)
            # изначальная ошибка была передавать сортировку в dict - надо было сразу в list
            elif isinstance(sorting, list) and sorting:
                order = []
                for sort_field, sort_dir in sorting:
                    if sort_dir == 'DESC':
                        order.append('-' + sort_field)
                    else:
                        order.append(sort_field)
                query = query.order_by(*order)
            for i in query.all()[begin:end + 1]:
                item = self.create_record()
                item.indent = 0
                item.is_leaf = True
                item.count = 0
                item.lindex = index + begin
                item.index = index + begin
                item.load(i)
                item.calc()
                res.append(item)
                index = index + 1
        # out_cache[cache_key] = (res,total_of_level)
        return res

    def counter(self, grouped, level_index, level_keys, expandedItems):
        return self.__count_model(grouped, level_index, level_keys, expandedItems)

    def __count_model(self, grouped, level_index, level_keys, expandedItems):
        '''
        подсчет количества строк в раскрытом уровне
        '''
        # построим ключ кэша
        # cache_key = '%s__%s__%s__%s' % (','.join(grouped), level_index, ','.join(level_keys), add_to_count_key(expandedItems))
        # if cache_key in count_cache.keys():
        #    print 'cached count...........'
        #    return count_cache[cache_key]

        # print 'count_model(): grouped=%s, level_index=%s, level_keys=%s,
        # expandedItems=%s' % (grouped, level_index, level_keys, expandedItems)
        total_of_level = 0
        if grouped:
            grouped_ranges = []
            # определим порядок группировки
            for i in grouped:
                grouped_ranges.append(i)

            query = self.get_data()
            filter = None
            for lev in range(0, level_index):
                lev_field = grouped_ranges[lev]
                key = level_keys[lev]
                if filter:
                    filter = filter & Q(**{lev_field: key})
                else:
                    filter = Q(**{lev_field: key})
            if filter:
                query = query.filter(filter)
            if level_index < len(grouped_ranges):
                field = grouped_ranges[level_index]
                query = query.values(field).distinct()
                # т.к. count(distinct не считает поля с null, то будем считать ВЛОБ!
                total_of_level = len(query)  # query.count()
            else:
                total_of_level = query.count()

        else:
            total_of_level = self.get_data().count()

        # добавим к количеству также сумму раскрытых элементов
        exp_count = 0
        for exp in expandedItems:
            if exp['count'] == -1:
                exp['count'] = self.counter(grouped, level_index + 1, level_keys + [
                                            exp['id']], exp['expandedItems'])
            exp_count = exp_count + exp['count']

        # count_cache[cache_key] = total_of_level+exp_count

        # print 'count_model() = %s, total=%s, exp_count=%s' % (total_of_level
        # + exp_count, total_of_level, exp_count)
        return total_of_level + exp_count

    def indexer(self, grouped, level_index, level_keys, expandedItems, aggregates, sorting):
        return self.__index_model(grouped, level_index, level_keys, expandedItems, aggregates, sorting)

    def __index_model(self, grouped, level_index, level_keys, expandedItems, aggregates, sorting):
        '''
        построение индексов элементов в раскрытом уровне, только для группировок и для тех, которые раскрыты
        '''
        res = []
        if grouped and len(expandedItems) > 0:
            # для всех группировочных элементов будут использоваться ключи
            # если берется уровень больший, чем количество группировок, то выдаем просто записи
            field = grouped[level_index]

            filter = None
            for lev in range(0, level_index):
                lev_field = grouped[lev]
                key = level_keys[lev]
                if filter:
                    filter = filter & Q(**{lev_field: key})
                else:
                    filter = Q(**{lev_field: key})
            aggr = []
            # будем считать агрегаты - по ним тоже сортируют иногда
            for agg in aggregates.keys():
                agg_type = aggregates[agg]
                if agg_type == 'sum':
                    aggr.append(Sum(agg))
                elif agg_type == 'count':
                    aggr.append(Count(agg))
                elif agg_type == 'min':
                    aggr.append(Min(agg))
                elif agg_type == 'max':
                    aggr.append(Max(agg))
                elif agg_type == 'avg':
                    aggr.append(Avg(agg))

            query = self.get_data().values(field)
            if filter:
                query = query.filter(filter)
            if aggr:
                query = query.annotate(*aggr).annotate(count=Count("id"))
            else:
                query = query.distinct()

            # сортировка
            sort_fields = []
            # оставлено для совместимости
            if sorting:
                if isinstance(sorting, dict):
                    pairs = six.iteritems(sorting)
                elif isinstance(sorting, list):
                    pairs = sorting
                else:
                    raise TypeError("Sorting must be dict or list!")
                for sort_field, sort_dir in pairs:
                    # необходимо исключить из сортировки поля,
                    # которые не входят в aggr,
                    # иначе по ним будет сделана ненужная группировка
                    if sort_field in list(aggregates.keys()) or sort_field == field:
                        if sort_field in list(aggregates.keys()):
                            # необходимо добавить суффикс к полю,
                            # которое в аггрегатах,
                            # иначе сортировать будет не по тому что надо :)
                            sort_field = sort_field + '__' + (
                                aggregates[sort_field]
                            )
                        if sort_dir == 'DESC':
                            sort_fields.append('-' + sort_field)
                        else:
                            sort_fields.append(sort_field)
            else:
                # нет заданной сортировки, отсортируем по этому полю
                sort_fields.append(field)
            if sort_fields:
                query = query.order_by(*sort_fields)
            # теперь выведем запрошенные элементы уровня
            for i in query:
                res.append(i[field])
        return res


class GroupingRecordDataProvider(GroupingRecordProvider):
    '''
    Провайдер для массива
    '''
    def update_aggregates(self, aggregates, aggr_rec, rec):

        sum_ = lambda val_aggr, val_curr: val_aggr + val_curr
        type_map = {
            'sum': sum_,
            'count': lambda val_aggr, val_curr: val_aggr + 1,
            'min': lambda val_aggr, val_curr: min(val_aggr, val_curr),
            'max': lambda val_aggr, val_curr: max(val_aggr, val_curr),
            'avg': sum_,  # Деление на количество реализуется в reader().
        }

        for agg in aggregates.keys():
            agg_type = aggregates[agg]

            val_aggregated = aggr_rec.get(agg, 0)
            val_current = self.getattr(rec, agg) or 0

            if callable(agg_type):
                func = agg_type
            else:
                func = type_map.get(agg_type)

            aggr_rec[agg] = func(val_aggregated, val_current)

    def reader(
        self, grouped, offset, level_index, level_keys,
        begin, end, aggregates, sorting
    ):
        '''
        вывод элементов дерева группировок в зависимости от уровня,
        ключевых элементов и интервала в уровне
        '''
        # специальный режим, когда считается общий итог по всем записям
        # - не важна сортировка и группировка
        if level_index == -1:
            aggr_rec = {}
            count = 0
            for rec in self.get_data():
                # будем считать агрегаты
                self.update_aggregates(aggregates, aggr_rec, rec)
                count += self.get_record_aggregate_value(rec)
            item = self.create_record()
            self.setattr(item, 'id', None)
            self.setattr(item, 'indent', None)
            self.setattr(item, 'lindex', None)
            self.setattr(item, 'count', count)
            if aggr_rec:
                for agg, aggv in six.iteritems(aggregates):
                    # для средних - посчитаем среднее
                    if aggv == 'avg':
                        count = self.getattr(item, 'count')
                        self.setattr(
                            item, agg,
                            0 if count == 0 else
                            round(aggr_rec[agg] * 1.0 / count, 2)
                        )
                    elif callable(aggv):
                        self.setattr(
                            item, agg,
                            aggv(aggr_rec[agg], None)
                        )
                    else:
                        self.setattr(item, agg, aggr_rec[agg])
            self.calc(item)
            return item

        # сортировать будем после группировки и фильтрации
        raw_data = self.get_data()
        res = []
        pre_res = []

        if grouped:
            # для всех группировочных элементов будут использоваться ключи
            level = {}
            aggregate_values = {}
            prepared = []

            # если берется уровень больший, чем количество группировок,
            # то выдаем просто записи
            if level_index >= len(grouped):
                field = None
            else:
                field = grouped[level_index]

            for rec in raw_data:
                found = True
                for lev in range(0, level_index):
                    lev_field = grouped[lev]
                    key = level_keys[lev]
                    key_value = self.getattr(rec, lev_field)
                    # подходит ли запись под группировку
                    if key != key_value:
                        found = False
                        break
                # если успешно проверили все поля, то значит это наша запись
                if found:
                    if field:
                        group_value = self.getattr(rec, field)
                        if not group_value in list(level.keys()):
                            level[group_value] = 1
                            aggr_rec = {}
                            aggregate_values[group_value] = aggr_rec
                            prepared.append((group_value, rec))
                        else:
                            level[group_value] += 1
                            aggr_rec = aggregate_values[group_value]
                        # будем считать агрегаты
                        self.update_aggregates(aggregates, aggr_rec, rec)
                    else:
                        prepared.append((rec, rec))
            # теперь выведем запрошенные элементы уровня
            # придется обработать все записи уровня,
            # т.к. требуется еще отсортировать их,
            # и лишь потом ограничить количество
            for i, rec in prepared:
                if field:
                    item = self.create_record(grouped=grouped)
                    self.setattr(item, field, i)
                    self.setattr(item, 'id', i)
                    self.setattr(item, 'indent', level_index)
                    self.setattr(item, 'count', level[i])
                    for agg, aggv in six.iteritems(aggregates):
                        # для средних - посчитаем среднее
                        if aggv == 'avg':
                            count = self.getattr(
                                item, self.get_record_aggregate())
                            self.setattr(
                                item, agg,
                                0 if count == 0 else
                                round(aggregate_values[i][agg] * 1.0 / count, 2)
                            )
                        elif callable(aggv):
                            self.setattr(
                                item, agg,
                                aggv(aggregate_values[i][agg], None)
                            )
                        else:
                            self.setattr(item, agg, aggregate_values[i][agg])

                    # Добавляем в прокси расшифровку для группируемого поля
                    detail_attr = self.detail_attrs_map.get(field)
                    if detail_attr:
                        self.setattr(item, detail_attr, self.getattr(
                            rec, detail_attr))

                    # проставим значения ключей уровня
                    for lev in range(0, level_index):
                        lev_field = grouped[lev]
                        key = level_keys[lev]
                        self.setattr(item, lev_field, key)

                        # Добавляем в прокси атрибуты для расшифровки
                        detail_attr = self.detail_attrs_map.get(lev_field)
                        if detail_attr:
                            self.setattr(item, detail_attr, self.getattr(
                                rec, detail_attr))

                    self.calc(item)
                else:
                    item = self.create_record(grouped=grouped)
                    self.setattr(item, 'is_leaf', True)
                    self.setattr(item, 'indent', level_index)
                    self.load(item, i)
                    self.calc(item)
                pre_res.append(item)

        else:
            # вывести все записи без группировки
            index = 0
            for i in raw_data:
                item = self.create_record()
                self.setattr(item, 'indent', 0)
                self.setattr(item, 'is_leaf', True)
                self.load(item, i)
                self.calc(item)
                pre_res.append(item)

        # а вот теперь сортируем и граничиваем
        # оставлено для совместимости
        if isinstance(sorting, dict) and list(sorting.keys()):
            order = []
            for sort_field, sort_dir in six.iteritems(sorting):
                if sort_dir == 'DESC':
                    order.append('-' + sort_field)
                else:
                    order.append(sort_field)
            sorted_data = self.multikeysort(pre_res, order)
        # изначальная ошибка была передавать сортировку в dict
        # - надо было сразу в list
        elif isinstance(sorting, list) and sorting:
            order = []
            for sort_field, sort_dir in sorting:
                if sort_dir == 'DESC':
                    order.append('-' + sort_field)
                else:
                    order.append(sort_field)
            sorted_data = self.multikeysort(pre_res, order)
        else:
            sorted_data = pre_res
        index = 0
        for item in sorted_data[begin:end + 1]:
            self.setattr(item, 'index', offset + index + begin)
            self.setattr(item, 'lindex', index + begin)
            res.append(item)
            index += 1

        return res

    __read_data = reader

    def counter(self, grouped, level_index, level_keys, expandedItems):
        '''
        подсчет количества строк в раскрытом уровне
        '''
        total_of_level = 0
        if grouped:
            if level_index == 0:
                # вывести элементы 1-го уровня группировки
                # (не нужно использовать ключи)
                level = []
                # переберем элементы и сформируем уровень
                field = grouped[level_index]
                for rec in self.get_data():
                    group_value = self.getattr(rec, field)
                    if not group_value in level:
                        level.append(group_value)
                total_of_level = len(level)
            else:
                # для всех остальных элементов будут использоваться ключи
                level = []
                # если берется уровень больший, чем количество группировок,
                # то выдаем просто записи
                if level_index >= len(grouped):
                    field = None
                else:
                    field = grouped[level_index]

                for rec in self.get_data():
                    for lev in range(0, level_index):
                        lev_field = grouped[lev]
                        key = level_keys[lev]
                        key_value = self.getattr(rec, lev_field)
                        # подходит ли запись под группировку
                        if key != key_value:
                            break
                        # если успешно проверили все поля,
                        # то значит это наша запись
                        elif lev == level_index - 1:
                            if field:
                                group_value = self.getattr(rec, field)
                                if not group_value in level:
                                    level.append(group_value)
                            else:
                                level.append(rec)
                total_of_level = len(level)
        else:
            total_of_level = len(self.get_data())

        # добавим к количеству также сумму раскрытых элементов
        exp_count = 0
        for exp in expandedItems:
            if exp['count'] == -1:
                exp['count'] = self.counter(
                    grouped,
                    level_index + 1,
                    level_keys + [exp['id']],
                    exp['expandedItems']
                )
            exp_count = exp_count + exp['count']

        # count_cache[cache_key] = total_of_level+exp_count
        # print 'count_exp_data() = %s, total=%s, exp_count=%s' %
        # (total_of_level+exp_count, total_of_level, exp_count)
        return total_of_level + exp_count

    __count_data = counter

    def indexer(
        self, grouped, level_index, level_keys,
        expandedItems, aggregates, sorting
    ):
        '''
        построение индексов элементов в раскрытом уровне,
        только для группировок и для тех, которые раскрыты
        '''
        res = []
        pre_res = []
        if grouped and len(expandedItems) > 0:
            raw_data = self.get_data()
            # для всех группировочных элементов будут использоваться ключи
            level = {}
            aggregate_values = {}
            prepared = []
            field = grouped[level_index]

            for rec in raw_data:
                finded = True
                for lev in range(0, level_index):
                    lev_field = grouped[lev]
                    key = level_keys[lev]
                    key_value = self.getattr(rec, lev_field)
                    # подходит ли запись под группировку
                    if key != key_value:
                        finded = False
                        break
                # если успешно проверили все поля, то значит это наша запись
                if finded:
                    group_value = self.getattr(rec, field)
                    if not group_value in list(level.keys()):
                        level[group_value] = 1
                        aggr_rec = {}
                        aggregate_values[group_value] = aggr_rec
                        prepared.append((group_value, rec))
                    else:
                        level[group_value] = level[group_value] + 1
                        aggr_rec = aggregate_values[group_value]
                    # будем считать агрегаты
                    self.update_aggregates(aggregates, aggr_rec, rec)

            # придется обработать все записи уровня,
            # т.к. требуется еще отсортировать их
            # и лишь потом ограничить количество
            for i, rec in prepared:
                item = self.create_record()
                self.setattr(item, field, i)
                self.setattr(item, 'id', i)
                self.setattr(item, 'indent', level_index)
                self.setattr(item, 'count', level[i])
                for agg in aggregates.keys():
                    # для средних - посчитаем среднее
                    if aggregates[agg] == 'avg':
                        self.setattr(
                            item, agg, (
                                aggregate_values[i][agg] /
                                self.getattr(item, 'count')))
                    else:
                        self.setattr(item, agg, aggregate_values[i][agg])

                # Добавляем в прокси расшифровку для группируемого поля
                detail_attr = self.detail_attrs_map.get(field)
                if detail_attr:
                    self.setattr(
                        item, detail_attr, self.getattr(rec, detail_attr))

                # проставим значения ключей уровня
                for lev in range(0, level_index):
                    lev_field = grouped[lev]
                    key = level_keys[lev]
                    self.setattr(item, lev_field, key)

                    # Добавляем в прокси атрибуты для расшифровки
                    detail_attr = self.detail_attrs_map.get(lev_field)
                    if detail_attr:
                        self.setattr(
                            item, detail_attr, self.getattr(rec, detail_attr))

                self.calc(item)
                pre_res.append(item)

            # а вот теперь сортируем и граничиваем
            # оставлено для совместимости
            if isinstance(sorting, dict) and list(sorting.keys()):
                order = []
                for sort_field, sort_dir in six.iteritems(sorting):
                    if sort_dir == 'DESC':
                        order.append('-' + sort_field)
                    else:
                        order.append(sort_field)
                sorted_data = self.multikeysort(pre_res, order)
            # изначальная ошибка была передавать сортировку в dict
            # - надо было сразу в list
            elif isinstance(sorting, list) and sorting:
                order = []
                for sort_field, sort_dir in sorting:
                    if sort_dir == 'DESC':
                        order.append('-' + sort_field)
                    else:
                        order.append(sort_field)
                sorted_data = self.multikeysort(pre_res, order)
            else:
                sorted_data = pre_res

            for item in sorted_data:
                res.append(self.getattr(item, 'id'))
        return res

    __index_data = indexer

    def multikeysort(self, items, columns):
        comparers = [
            (
                (col[1:].strip(), -1)
                if col.startswith('-') else
                (col.strip(), 1)
            ) for col in columns
        ]

        def comparer(left, right):
            for attr, mult in comparers:
                result = compare(
                    self.getattr(left, attr),
                    self.getattr(right, attr)
                )
                if result:
                    return mult * result
            else:
                return 0
        return sorted(items, key=cmp_to_key(comparer))

    def get_record_aggregate_value(self, rec):
        """Используется при расчете количества записей

        По умолчанию считаются все записи,
        при переопределении в наследнике можно использовать
        self.getattr(rec, 'count')
        """
        return 1

    def get_record_aggregate(self):
        """Используется при расчете среднего значения

        По умолчанию делим сумму по записям на значение агрегата count
        """
        return 'count'
