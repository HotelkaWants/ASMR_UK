import psycopg2
from psycopg2.extras import RealDictCursor
import config
from data_classes import Analytic, Indicator, AnalyticType, ValueIndicator, _parse_date, User, DZO
import pandas as pd

class DatabaseError(Exception):
    """Кастомное исключение для ошибок базы данных"""
    pass

class Database:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(**config.DB_CONFIG)
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False
        
    def execute_query(self, query: str, params: tuple = None):
        """Универсальный метод выполнения SELECT запросов"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                return []
        except Exception as e:
            raise DatabaseError(f"Ошибка выполнения запроса: {e}\nЗапрос: {query}")
    
    def execute_command(self, query: str, params: tuple = None) -> bool:
        """Универсальный метод выполнения INSERT/UPDATE/DELETE"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"Ошибка выполнения команды: {e}\nКоманда: {query}")
      
    def load_from_csv(self, filepath, table_name):
        """Загрузить данные из CSV файла"""
        try:
            df = pd.read_csv(filepath)
            return self._insert_dataframe(df, table_name)
        except Exception as e:
            print(f"Ошибка загрузки CSV: {e}")
            raise e
    
     # ========== CRUD ДЛЯ Analytic ==========
        
    def create_analytic(self, analytic: Analytic):
        """Создать новую аналитику"""
        try:
            existing = self.get_analytic_by_id(analytic.id_analytic_type, analytic.id)
            if existing:
                raise DatabaseError(f"Аналитика с ID '{analytic.id}' для типа '{analytic.id_analytic_type}' уже существует")
            
            parent_type = self.get_analytic_type_by_id(analytic.id_analytic_type)
            if not parent_type:
                raise DatabaseError(f"Родительский тип аналитики '{analytic.id_analytic_type}' не найден")
            
            return self.execute_command(
                'INSERT INTO public."Аналитики" ("Код вида аналитики", "Код аналитики", "Аналитика") VALUES (%s, %s, %s)',
                (analytic.id_analytic_type, analytic.id, analytic.analytic_name)
            )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка создания аналитики: {e}")
    
    def get_analytic_by_id(self, analytic_type_id: str, analytic_id: str):
        """Получить аналитику по ID"""
        try:
            result = self.execute_query(
                'SELECT * FROM public."Аналитики" WHERE "Код вида аналитики" = %s AND "Код аналитики" = %s',
                (analytic_type_id, analytic_id)
            )
            return Analytic(result[0]) if result else None
        except Exception as e:
            raise DatabaseError(f"Ошибка получения аналитики по ID: {e}")
    
    def get_all_analytics(self):
        """Получить все аналитики"""
        query = """
        SELECT * FROM public."Аналитики"
        ORDER BY "Код вида аналитики" ASC, "Код аналитики" ASC
        """
        try:
            result = self.execute_query(query)
            return [Analytic(row) for row in result]
        except Exception as e:
            raise DatabaseError(f"Ошибка получения всех аналитик: {e}")
    
    def get_analytics_by_type(self, analytic_type_id: str):
        """Получить аналитики по виду аналитики"""
        try:
            result = self.execute_query(
                'SELECT * FROM public."Аналитики" WHERE "Код вида аналитики" = %s',
                (analytic_type_id,)
            )
            return [Analytic(row) for row in result]
        except Exception as e:
            raise DatabaseError(f"Ошибка получения аналитик по типу: {e}")
    
    def update_analytic(self, analytic_type_id: str, analytic_id: str, new_name: str) -> bool:
        """Обновить аналитику"""
        try:
            existing = self.get_analytic_by_id(analytic_type_id, analytic_id)
            if existing:
                raise DatabaseError(f"Аналитика с ID '{analytic_id}' для типа '{analytic_type_id}' уже существует")
            
            parent_type = self.get_analytic_type_by_id(analytic_type_id)
            if not parent_type:
                raise DatabaseError(f"Родительский тип аналитики '{analytic_type_id}' не найден")
            print(parent_type)
            return self.execute_command(
                'UPDATE public."Аналитики" SET "Аналитика" = %s WHERE "Код вида аналитики" = %s AND "Код аналитики" = %s',
             (new_name, analytic_type_id, analytic_id)
            )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка обновления аналитики: {e}")
    
    def delete_analytic(self, analytic_type_id: str, analytic_id: str):
        """Удалить аналитику"""
        try:
            existing = self.get_analytic_by_id(analytic_type_id, analytic_id)
            if not existing:
                raise DatabaseError(f"Аналитика с ID '{analytic_id}' для типа '{analytic_type_id}' не найдена")
            
            return self.execute_command(
                'DELETE FROM public."Аналитики" WHERE "Код вида аналитики" = %s AND "Код аналитики" = %s',
                (analytic_type_id, analytic_id)
            )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка удаления аналитики: {e}")
    
    
    
    # ========== CRUD ДЛЯ Indicator ==========
    
    def create_indicator(self, indicator: Indicator) -> bool:
        """Создать новый показатель"""
        try:
            existing = self.get_indicator_by_id(indicator.id)
            if existing:
                raise DatabaseError(f"Показатель с ID '{indicator.id}' уже существует")
            
            if indicator.id_analytic_type_1:
                parent1 = self.get_analytic_type_by_id(indicator.id_analytic_type_1)
                if not parent1:
                    raise DatabaseError(f"Тип аналитики 1 '{indicator.id_analytic_type_1}' не найден")
            
            if indicator.id_analytic_type_2:
                parent2 = self.get_analytic_type_by_id(indicator.id_analytic_type_2)
                if not parent2:
                    raise DatabaseError(f"Тип аналитики 2 '{indicator.id_analytic_type_2}' не найден")
            
            if indicator.id_analytic_type_3:
                parent3 = self.get_analytic_type_by_id(indicator.id_analytic_type_3)
                if not parent3:
                    raise DatabaseError(f"Тип аналитики 3 '{indicator.id_analytic_type_3}' не найден")
            
            return self.execute_command(
                'INSERT INTO public."Показатели" ("Код показателя", "Показатель", "Код вида аналитики 1", "Код вида аналитики 2", "Код вида аналитики 3") VALUES (%s, %s, %s, %s, %s)',
                (indicator.id, indicator.indicator_name, indicator.id_analytic_type_1, indicator.id_analytic_type_2, indicator.id_analytic_type_3)
            )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка создания показателя: {e}")
    
    def get_indicator_by_id(self, indicator_id: str):
        """Получить показатель по ID"""
        try:
            result = self.execute_query(
                'SELECT * FROM public."Показатели" WHERE "Код показателя" = %s',
                (indicator_id,)
            )
            return Indicator(result[0]) if result else None
        except Exception as e:
            raise DatabaseError(f"Ошибка получения показателя по ID: {e}")
    
    def get_all_indicators(self):
        """Получить все показатели"""
        try:
            result = self.execute_query(
                """SELECT * FROM public."Показатели" ORDER BY "Код показателя" ASC """
            )
            return [Indicator(row) for row in result]
        except Exception as e:
            raise DatabaseError(f"Ошибка получения всех показателей: {e}")
    
    def update_indicator(self, indicator_id: str, indicator_name: str, id_analytic_type_1: str, id_analytic_type_2: str, id_analytic_type_3: str):
        """Обновить показатель"""
        try:
            if id_analytic_type_1 != '':
                parent1 = self.get_analytic_type_by_id(id_analytic_type_1)
                if not parent1:
                    raise DatabaseError(f"Тип аналитики 1 '{id_analytic_type_1}' не найден")
            if id_analytic_type_2 != '':
                parent2 = self.get_analytic_type_by_id(id_analytic_type_2)
                if not parent2:
                    raise DatabaseError(f"Тип аналитики 2 '{id_analytic_type_2}' не найден")
            if id_analytic_type_3 != '':
                parent3 = self.get_analytic_type_by_id(id_analytic_type_3)
                if not parent3:
                    raise DatabaseError(f"Тип аналитики 3 '{id_analytic_type_3}' не найден")
            query = """
            UPDATE public."Показатели"
            SET "Код показателя" = %s,
                "Показатель" = %s,
                "Код вида аналитики 1" = %s,
                "Код вида аналитики 2" = %s,
                "Код вида аналитики 3" = %s
            WHERE "Код показателя" = %s
            """
            return self.execute_command(
                query,
                (indicator_id, indicator_name, id_analytic_type_1, id_analytic_type_2, id_analytic_type_3, indicator_id)
            )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка обновления показателя: {e}")
    
    def delete_indicator(self, indicator_id: str) -> bool:
        """Удалить показатель"""
        try:
            # Проверяем, существует ли запись
            existing = self.get_indicator_by_id(indicator_id)
            if not existing:
                raise DatabaseError(f"Показатель с ID '{indicator_id}' не найден")
            
            return self.execute_command(
                'DELETE FROM public."Показатели" WHERE "Код показателя" = %s',
                (indicator_id,)
            )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка удаления показателя: {e}")
        


    # ========== CRUD ДЛЯ AnalyticType ==========
    def create_analytic_type(self, analytic_type: AnalyticType) -> bool:
        """Создать новый вид аналитики"""
        try:
            existing = self.get_analytic_type_by_id(analytic_type.id)
            if existing:
                raise DatabaseError(f"Вид аналитики с ID '{analytic_type.id}' уже существует")
            
            return self.execute_command(
                'INSERT INTO public."Виды аналитики" ("Код вида аналитики", "Вид аналитики") VALUES (%s, %s)',
                (analytic_type.id, analytic_type.analytic_type_name)
            )
        except DatabaseError:
            raise 
        except Exception as e:
            raise DatabaseError(f"Ошибка создания вида аналитики: {e}")
    
    def get_all_analytic_types(self):
        """Получить все виды аналитик"""
        try:
            result = self.execute_query(
                """
                SELECT * FROM public."Виды аналитики" ORDER BY "Код вида аналитики" ASC"""
            )
            return [AnalyticType(row) for row in result]
        except Exception as e:
            raise DatabaseError(f"Ошибка получения всех видов аналитик: {e}")
    
    def get_analytic_type_by_id(self, analytic_type_id: str):
        """Получить вид аналитики по ID"""
        try:
            result = self.execute_query(
                'SELECT * FROM public."Виды аналитики" WHERE "Код вида аналитики" = %s',
                (analytic_type_id,)
            )
            print(result)
            return AnalyticType(result[0]) if result else None
        except Exception as e:
            raise DatabaseError(f"Ошибка получения вида аналитики по ID: {e}")
            
    def update_analytic_type(self, analytic_type_id: str, new_name: str) -> bool:
        """Обновить вид аналитики"""
        try:
            existing = self.get_analytic_type_by_id(analytic_type_id)
            if not existing:
                raise DatabaseError(f"Вид аналитики с ID '{analytic_type_id}' не найден")
            
            return self.execute_command(
                'UPDATE public."Виды аналитики" SET "Вид аналитики" = %s WHERE "Код вида аналитики" = %s',
                (new_name, analytic_type_id)
            )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка обновления вида аналитики: {e}")
    
    def delete_analytic_type(self, analytic_type_id: str) -> bool:
        """Удалить вид аналитики"""
        try:
            existing = self.get_analytic_type_by_id(analytic_type_id)
            if not existing:
                raise DatabaseError(f"Вид аналитики с ID '{analytic_type_id}' не найден")
            
            count_result = self.execute_query(
                'SELECT COUNT(*) as count FROM public."Аналитики" WHERE "Код вида аналитики" = %s',
                (analytic_type_id,)
            )
            
            if count_result and count_result[0]['count'] > 0:
                raise DatabaseError("Нельзя удалить вид аналитики, так как есть связанные аналитики")
            
            return self.execute_command(
                'DELETE FROM public."Виды аналитики" WHERE "Код вида аналитики" = %s',
                (analytic_type_id,)
            )
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка удаления вида аналитики: {e}")
        

    # ========== CRUD ДЛЯ ValuesIndicator ==========
    def create_values_indicator(self, dzo: ValueIndicator) -> bool:
        """Создать новое значение показателя"""
        try:
            existing = self.get_values_indicator_by_id(dzo.id_indicator, dzo.date_period_start, dzo.date_period_end, dzo.analytic_1, dzo.analytic_2, dzo.analytic_3)
            if existing:
                raise DatabaseError(f"Значение показателя с указанными параметрами уже существует")
            
            return self.execute_command(
                'INSERT INTO public."Значения показателей ДЗО" ("Дата начала периода", "Дата окончания периода", "Код показателя", "Код аналитики 1", "Код аналитики 2", "Код аналитики 3", "Сумма", "ДЗО") VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (dzo.date_period_start, dzo.date_period_end, dzo.id_indicator, dzo.analytic_1, dzo.analytic_2, dzo.analytic_3, dzo.sum_value, dzo.dzo)
            )
        except DatabaseError:
            raise 
        except Exception as e:
            raise DatabaseError(f"Ошибка создания значения показателя: {e}")
    
    def get_values_indicator_by_id(self, indicator_id: str, date_start: str, date_end: str, analytic_1: str, analytic_2: str, analytic_3: str):
        """Получить значение показателя по ID"""
        try:
            query = 'SELECT * FROM public."Значения показателей ДЗО" WHERE "Код показателя" = %s AND "Дата начала периода" = %s AND "Дата окончания периода" = %s'
            params = [indicator_id, _parse_date(date_start), _parse_date(date_end)]

            query += ' AND "Код аналитики 1" = %s'
            params.append(analytic_1)

            if analytic_2 is None or analytic_2 == '':
                query += ' AND "Код аналитики 2" IS NULL'
            else:
                query += ' AND "Код аналитики 2" = %s'
                params.append(analytic_2)

            if analytic_3 is None or analytic_3 == '':
                query += ' AND "Код аналитики 3" IS NULL'
            else:
                query += ' AND "Код аналитики 3" = %s'
                params.append(analytic_3)

            result = self.execute_query(query, tuple(params))
            return ValueIndicator(result[0]) if result else None
        except Exception as e:
            raise DatabaseError(f"Ошибка получения значения показателя по ID: {e}")
   
    def get_values_indicators(self):
        """Получить все значения показателей"""
        try:
            result = self.execute_query(
                """SELECT * FROM public."Значения показателей ДЗО" ORDER BY "Дата начала периода" ASC, "Дата окончания периода" ASC, "Код показателя" ASC"""
            )
            return [ValueIndicator(row) for row in result]
        except Exception as e:
            raise DatabaseError(f"Ошибка получения всех значений показателей: {e}")
    def add_values_indicator(self, value_indicator: ValueIndicator) -> bool:
        """Добавить значение показателя"""
        try:
            return self.execute_command(
                'INSERT INTO public."Значения показателей ДЗО" ("Дата начала периода", "Дата окончания периода", "Код показателя", "Код аналитики 1", "Код аналитики 2", "Код аналитики 3", "Сумма") VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (value_indicator.date_period_start, value_indicator.date_period_end, value_indicator.id_indicator, value_indicator.analytic_1, value_indicator.analytic_2, value_indicator.analytic_3, value_indicator.sum_value)
            )
        except Exception as e:
            raise DatabaseError(f"Ошибка добавления значения показателя: {e}")
    
    def delete_values_indicator(self, indicator_id: str, date_start: str, date_end: str, analytic_1: str, analytic_2: str, analytic_3: str) -> bool:
        """Удалить значение показателя"""
        try:
            existing = self.get_values_indicator_by_id(indicator_id, date_start, date_end, analytic_1, analytic_2, analytic_3)
            if not existing:
                raise DatabaseError(f"Значение показателя с указанными параметрами не найдено")
            
            query = '''
                DELETE FROM public."Значения показателей ДЗО"
                WHERE "Код показателя" = %s
                AND "Дата начала периода" = %s
                AND "Дата окончания периода" = %s
                AND "Код аналитики 1" = %s
            '''
            params = [indicator_id, date_start, date_end, analytic_1]

            # analytic_2
            if analytic_2 is None or analytic_2 == '':
                query += ' AND "Код аналитики 2" IS NULL'
            else:
                query += ' AND "Код аналитики 2" = %s'
                params.append(analytic_2)

            # analytic_3
            if analytic_3 is None or analytic_3 == '':
                query += ' AND "Код аналитики 3" IS NULL'
            else:
                query += ' AND "Код аналитики 3" = %s'
                params.append(analytic_3)

            return self.execute_command(query, tuple(params))
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка удаления значения показателя: {e}")
        
    def update_values_indicator(self, old_value: ValueIndicator, new_value: ValueIndicator) -> bool:
        """Обновить значение показателя"""
        try:
            existing = self.get_values_indicator_by_id(
                old_value.id_indicator,
                old_value.date_period_start,
                old_value.date_period_end,
                old_value.analytic_1,
                old_value.analytic_2,
                old_value.analytic_3
            )
            if not existing:
                raise DatabaseError(f"Значение показателя с указанными параметрами не найдено")

            dzo_existing = self.get_dzo_by_id(new_value.dzo)
            if not dzo_existing:
                raise DatabaseError(f"ДЗО с ID '{new_value.dzo}' не найдено")
            
            where_clause = '''
                "Код показателя" = %s AND
                "Дата начала периода" = %s AND
                "Дата окончания периода" = %s AND
                "Код аналитики 1" = %s
            '''
            params = [
                new_value.date_period_start,
                new_value.date_period_end,
                new_value.id_indicator,
                new_value.analytic_1,
                new_value.analytic_2,
                new_value.analytic_3,
                new_value.sum_value,
                new_value.dzo,
                old_value.id_indicator,
                old_value.date_period_start,
                old_value.date_period_end,
                old_value.analytic_1,
                
            ]

            if old_value.analytic_2 is None or old_value.analytic_2 == '':
                where_clause += ' AND "Код аналитики 2" IS NULL'
            else:
                where_clause += ' AND "Код аналитики 2" = %s'
                params.append(old_value.analytic_2)

            if old_value.analytic_3 is None or old_value.analytic_3 == '':
                where_clause += ' AND "Код аналитики 3" IS NULL'
            else:
                where_clause += ' AND "Код аналитики 3" = %s'
                params.append(old_value.analytic_3)

            query = f'''
                UPDATE public."Значения показателей ДЗО"
                SET "Дата начала периода" = %s,
                    "Дата окончания периода" = %s,
                    "Код показателя" = %s,
                    "Код аналитики 1" = %s,
                    "Код аналитики 2" = %s,
                    "Код аналитики 3" = %s,
                    "Сумма" = %s,
                    "ДЗО" = %s
                WHERE {where_clause}
            '''

            return self.execute_command(query, tuple(params))
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Ошибка обновления значения показателя: {e}")
    
    # ========== CRUD ДЛЯ DZO ==========

    def create_dzo(self, name, address) -> bool:
        """Создать новое ДЗО"""
        try:
            return self.execute_command(
                'INSERT INTO public."ДЗО" ("Наименование", "Адрес") VALUES (%s, %s)',
                (name, address)
            )
        except Exception as e:
            raise DatabaseError(f"Ошибка создания ДЗО: {e}")

    def get_dzo_by_id(self, dzo_id: str):
        """Получить ДЗО по ID"""
        try:
            result = self.execute_query(
                'SELECT * FROM public."ДЗО" WHERE "Идентификатор ДЗО" = %s',
                (dzo_id,)
            )
            return DZO(result[0]) if result else None
        except Exception as e:
            raise DatabaseError(f"Ошибка получения ДЗО по ID: {e}")
        
    def get_all_dzos(self):
        """Получить все ДЗО"""
        try:
            result = self.execute_query(
                '''SELECT * FROM public."ДЗО" ORDER BY "Идентификатор ДЗО" ASC'''
            )
            return [DZO(row) for row in result]
        except Exception as e:
            raise DatabaseError(f"Ошибка получения всех ДЗО: {e}")
        
    def update_dzo(self, dzo_id: str, name: str, address: str) -> bool:
        """Обновить ДЗО"""
        try:
            return self.execute_command(
                '''
                UPDATE public."ДЗО"
                SET "Наименование" = %s,
                    "Адрес" = %s
                WHERE "Идентификатор ДЗО" = %s
                ''',
                (name, address, dzo_id)
            )
        except Exception as e:
            raise DatabaseError(f"Ошибка обновления ДЗО: {e}")
    
    def delete_dzo(self, dzo_id: str) -> bool:
        """Удалить ДЗО"""
        try:
            return self.execute_command(
                'DELETE FROM public."ДЗО" WHERE "Идентификатор ДЗО" = %s',
                (dzo_id,)
            )
        except Exception as e:
            raise DatabaseError(f"Ошибка удаления ДЗО: {e}")
    
    # ========== CRUD ДЛЯ USER ==========

    def create_user(self, user: User) -> bool:
        """Создать нового пользователя"""
        try:
            dzo_available = self.execute_query(
                'SELECT * FROM public."ДЗО" WHERE "Идентификатор ДЗО" = %s',
                (user.dzo,)
            )
            if not dzo_available:
                raise DatabaseError(f"ДЗО с ID '{user.dzo}' не найдено")
            return self.execute_command(
                '''
                INSERT INTO public."Пользователи"("ФИО", "Роль", "Логин", "Пароль", "ДЗО")
                VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')), %s)
                ''',
                (user.full_name, user.role, user.login, user.password, user.dzo)
            )
        except Exception as e:
            raise DatabaseError(f"Ошибка создания пользователя: {e}")
    
    def get_user_by_credentials(self, login: str, password: str):
        """Получить пользователя по логину и паролю"""
        try:
            result = self.execute_query(
                '''
                SELECT * FROM public."Пользователи"
                WHERE "Логин" = %s AND "Пароль" = crypt(%s, "Пароль")
                ''',
                (login, password)
            )
            return User(result[0]) if result else None
        except Exception as e:
            raise DatabaseError(f"Ошибка получения пользователя по учетным данным: {e}")
        
    def get_all_users(self):
        """Получить всех пользователей"""
        try:
            result = self.execute_query(
                '''SELECT * FROM public."Пользователи" ORDER BY "Идентификационный номер" ASC'''
            )
            return [User(row) for row in result]
        except Exception as e:
            raise DatabaseError(f"Ошибка получения всех пользователей: {e}")
        
    def update_user(self, user_id: str, full_name: str, role: str, login: str, password: str, dzo: str) -> bool:
        """Обновить пользователя"""
        try:
            dzo_available = self.execute_query(
                'SELECT * FROM public."ДЗО" WHERE "Идентификатор ДЗО" = %s',
                (dzo,)
            )
            if not dzo_available:
                raise DatabaseError(f"ДЗО с ID '{dzo}' не найдено")
            
            return self.execute_command(
                '''
                UPDATE public."Пользователи"
                SET "ФИО" = %s,
                    "Роль" = %s,
                    "Логин" = %s,
                    "Пароль" = crypt(%s, gen_salt('bf')),
                    "ДЗО" = %s
                WHERE "Идентификационный номер" = %s
                ''',
                (full_name, role, login, password, dzo, user_id)
            )
        except Exception as e:
            raise DatabaseError(f"Ошибка обновления пользователя: {e}")
        
    def delete_user(self, user_id: str) -> bool:
        """Удалить пользователя"""
        try:
            return self.execute_command(
                'DELETE FROM public."Пользователи" WHERE "Идентификационный номер" = %s',
                (user_id,)
            )
        except Exception as e:
            raise DatabaseError(f"Ошибка удаления пользователя: {e}")
    

# db = Database()
# if db.connect():
#     result = db.get_values_indicators()
#     for i in result:
#         print(i.to_dict())   