from playhouse.mysql_ext import JSONField
from peewee import __exception_wrapper__ as exc_wrapper, OperationalError, IntegrityError
from peewee import MySQLDatabase, Model, fn
from peewee import PrimaryKeyField, DateField, CharField, IntegerField, DateTimeField, ForeignKeyField
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
    name = CharField()

    class Meta:
        db_table = 'city'


class Platform(BaseModel):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        db_table = 'platform'


class Profession(BaseModel):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        db_table = 'profession'


class Resume(BaseModel):
    id = PrimaryKeyField()
    platform_id = ForeignKeyField(Platform, backref='resumes')
    platform_resume_id = CharField()
    city_id = ForeignKeyField(City, backref='resumes')
    profession_id = ForeignKeyField(Profession, backref='resumes')
    sex = CharField()
    age = IntegerField()
    salary_from = IntegerField()
    salary_to = IntegerField()
    currency = CharField()
    experience_months = IntegerField()
    summary_info = JSONField()
    link = CharField()

    class Meta:
        db_table = 'resume'

    @classmethod
    def get_resume_count(cls):
        return cls.select().count()
