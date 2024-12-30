from playhouse.mysql_ext import JSONField
from peewee import __exception_wrapper__ as exc_wrapper, OperationalError, IntegrityError
from peewee import MySQLDatabase, Model, fn
from peewee import PrimaryKeyField, DateField
from config import CONFIG


class RetryOperationalError(object):
    ''' Автоматическое переподключение '''

    def execute_sql(self, sql, params=None, commit=True):
        ''' Переподключение '''
        try:
            cursor = super(RetryOperationalError, self).execute_sql(sql, params, commit)
        except OperationalError:
            if not self.is_closed():
                self.close()
            with exc_wrapper:
                cursor = self.cursor()
                cursor.execute(sql, params or ())
                if commit and not self.in_transaction():
                    self.commit()
        return cursor


class MyRetryDB(RetryOperationalError, MySQLDatabase):
    ''' Подключение к БД '''
    pass


db = MyRetryDB(CONFIG['mysql_base'], user=CONFIG['mysql_user'],
               host=CONFIG['mysql_name_host'], password=CONFIG['mysql_password'],
               charset=CONFIG['mysql_charset'], port=CONFIG['mysql_port'])


class BaseModel(Model):
    ''' Создание модели БД '''

    class Meta:
        ''' Создание модели БД '''
        database = db


class City(BaseModel):
    id = PrimaryKeyField()

