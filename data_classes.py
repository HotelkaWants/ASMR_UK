import datetime 

def _parse_date(value):
    if not value:
        return None

    if isinstance(value, datetime.date):
        return value

    if isinstance(value, datetime.datetime):
        return value.date()

    if isinstance(value, str):
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.datetime.strptime(value, fmt).date()
            except Exception:
                continue
    return None
class ValueIndicator:
    def __init__(self, data: dict):
        self.id_indicator = data.get('Код показателя')
        self.analytic_1 = data.get('Код аналитики 1')
        self.analytic_2 = data.get('Код аналитики 2')
        self.analytic_3 = data.get('Код аналитики 3')
        self.sum_value = data.get('Сумма')
        self.date_period_start = _parse_date(data.get('Дата начала периода'))
        self.date_period_end = _parse_date(data.get('Дата окончания периода'))
        self.dzo = data.get('ДЗО')
    def to_dict(self):
        return {
            'Код показателя': self.id_indicator,
            'Код аналитики 1': self.analytic_1,
            'Код аналитики 2': self.analytic_2,
            'Код аналитики 3': self.analytic_3,
            'Сумма': self.sum_value,
            'Дата начала периода': self.date_period_start,
            'Дата окончания периода': self.date_period_end,
            'ДЗО': self.dzo
        }
class Indicator:
    def __init__(self, data: dict ):
        self.id = data.get('Код показателя')
        self.indicator_name = data.get('Показатель')
        self.id_analytic_type_1 = data.get('Код вида аналитики 1')
        self.id_analytic_type_2 = data.get('Код вида аналитики 2')
        self.id_analytic_type_3 = data.get('Код вида аналитики 3')
        self.date_period_start = _parse_date(data.get('Дата начала периода'))
        self.date_period_end = _parse_date(data.get('Дата конца периода'))
    def to_dict(self):
        return {
            'Код показателя': self.id,
            'Показатель': self.indicator_name,
            'Код вида аналитики 1': self.id_analytic_type_1,
            'Код вида аналитики 2': self.id_analytic_type_2,
            'Код вида аналитики 3': self.id_analytic_type_3,
            'Дата начала периода': self.date_period_start,
            'Дата конца периода': self.date_period_end
        }
class AnalyticType:
    def __init__(self, data: dict):
        self.id = data.get('Код вида аналитики')
        self.analytic_type_name = data.get('Вид аналитики')
    
    def to_dict(self):
        return {
            'Код вида аналитики': self.id,
            'Вид аналитики': self.analytic_type_name
        }
        
class Analytic:
    def __init__(self, data: dict):
        self.id = data.get('Код аналитики')
        self.id_analytic_type = data.get('Код вида аналитики')
        self.analytic_name = data.get('Аналитика')
        self.date_period_start = _parse_date(data.get('Дата начала периода'))
        self.date_period_end = _parse_date(data.get('Дата конца периода'))
    def to_dict(self):
        return {
            'Код аналитики': self.id,
            'Код вида аналитики': self.id_analytic_type,
            'Аналитика': self.analytic_name,
            'Дата начала периода': self.date_period_start,
            'Дата конца периода': self.date_period_end
        }

class DZO:
    def __init__(self, data: dict):
        self.id = data.get('Идентификатор ДЗО')
        self.name = data.get('Наименование')
        self.address = data.get('Адрес')
        
    def to_dict(self):
        return {
            'Идентификатор ДЗО': self.id,
            'Наименование': self.name,
            'Адрес': self.address
        }
    
class User:
    def __init__(self, data: dict):
        self.id = data.get('Идентификационный номер')
        self.full_name = data.get('ФИО')
        self.login = data.get('Логин')
        self.password = data.get('Пароль')
        self.role = data.get('Роль')
        self.dzo = data.get('ДЗО')

    
    def to_dict(self):
        return {
            'Идентификационный номер': self.id,
            'ФИО': self.full_name,
            'Логин': self.login,
            'Пароль': self.password,
            'Роль': self.role,
            'ДЗО': self.dzo
        }