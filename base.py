import random

from peewee import __exception_wrapper__ as exc_wrapper, OperationalError, IntegrityError
from peewee import MySQLDatabase, Model, fn, BooleanField
from peewee import PrimaryKeyField, DateField, CharField, IntegerField, DateTimeField, ForeignKeyField, Case, TextField
from config import CONFIG
from playhouse.mysql_ext import JSONField


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


db = MyRetryDB(
    database=CONFIG['mysql_base'],
    user=CONFIG['mysql_user'],
    host=CONFIG['mysql_name_host'],
    password=CONFIG['mysql_password'],
    charset=CONFIG['mysql_charset'],
    port=CONFIG['mysql_port'],
)


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

    @classmethod
    def add_many(cls, professions_list):
        cls.insert_many(
            rows=professions_list,
            fields=(
                cls.name,
            ),
        ).on_conflict_ignore().execute()

    @classmethod
    def get_by_text(cls, text):
        predicate = True
        for word in text.split():
            predicate &= cls.name ** f'%{word}%'
        result = list(cls.select().where(predicate).order_by(fn.Rand()).limit(5000))
        return result


class Resume(BaseModel):
    id = PrimaryKeyField()
    platform = ForeignKeyField(Platform, backref='resumes')
    platform_resume_id = CharField()
    platform_resume_tm_create = DateTimeField()
    platform_resume_tm_update = DateTimeField()
    city = ForeignKeyField(City, backref='resumes')
    profession = ForeignKeyField(Profession, backref='resumes')
    sex = CharField()
    age = IntegerField()
    salary_from = IntegerField()
    salary_to = IntegerField()
    currency = CharField()
    experience_months = IntegerField()
    summary_info = JSONField()
    link = CharField()
    tm = DateTimeField()

    class Meta:
        db_table = 'resume'

    @classmethod
    def get_resume_count(cls):
        return cls.select().count()

    @classmethod
    def add(cls, data_list):
        with db.atomic():
            cls.insert_many(data_list).on_conflict_replace().execute()

    @classmethod
    def get_by_professions(cls, professions):
        return cls.select().where(
            cls.profession.in_(professions)
        )


class PlatformCity(BaseModel):
    id = PrimaryKeyField()
    platform_id = ForeignKeyField(Platform)
    city_id = ForeignKeyField(City)
    platform_city_id = CharField()

    class Meta:
        db_table = 'platform_city'

    @classmethod
    def add(
            cls,
            platform_id,
            city_id,
            platform_city_id,
    ):
        try:
            cls.create(
                platform_id=platform_id,
                city_id=city_id,
                platform_city_id=platform_city_id,
            ).on
        except Exception as ex:
            pass

    @classmethod
    def get_by_name(cls, name):
        return cls.select().join(City).where(
            City.name == name
        ).first()


class Vacancy(BaseModel):
    id = PrimaryKeyField()
    platform = ForeignKeyField(Platform, backref='vacancies')
    platform_vacancy_id = CharField()
    platform_vacancy_tm_create = DateTimeField()
    city = ForeignKeyField(City, backref='vacancies')
    profession = ForeignKeyField(Profession, backref='vacancies')
    salary_from = IntegerField()
    salary_to = IntegerField()
    schedule = CharField()
    currency = CharField()
    experience_months_from = IntegerField()
    experience_months_to = IntegerField()
    summary_info = JSONField()
    link = CharField()
    employer_name = CharField()
    contact_email = CharField()
    contact_phone = CharField()
    contact_person = CharField()
    tm = DateTimeField()

    class Meta:
        db_table = 'vacancy'

    @classmethod
    def add(cls, data_list):
        with db.atomic():
            cls.insert_many(data_list).on_conflict_replace().execute()

    @classmethod
    def get_by_professions(cls, professions):
        return cls.select().where(
            cls.profession.in_(professions)
        )


class User(BaseModel):
    id = PrimaryKeyField()
    username = CharField()
    full_name = CharField()
    email = CharField()
    hashed_password = CharField()
    disabled = BooleanField()

    class Meta:
        db_table = 'user'

    @classmethod
    def get_by_username(cls, username):
        return cls.get_or_none(cls.username == username)

    @classmethod
    def add(cls, username, hashed_password, email=None, fullname=None):
        return cls.create(
            username=username,
            hashed_password=hashed_password,
            email=email,
            fullname=fullname,
        )


class WhatsappInstance(BaseModel):
    id = PrimaryKeyField()
    instance_id = CharField()
    instance_token = CharField()
    user_id = ForeignKeyField(User)
    is_login = BooleanField()

    class Meta:
        db_table = 'whatsapp_instance'

    @classmethod
    def set_user(cls, user_id):
        instance = cls.get_or_none(
            cls.user_id == user_id,
            cls.is_login == False,
        )
        if instance:
            return instance
        instance = cls.select().where(
            cls.user_id.is_null(),
            cls.is_login == False,
        ).first()
        if not instance:
            return
        instance.user_id = user_id

        instance.save()
        return instance

    @classmethod
    def login_user(cls, user_id):
        cls.update({'is_login': True}).where(cls.user_id == user_id).execute()

    @classmethod
    def logout_user(cls, user_id):
        cls.update({'user_id': None, 'is_login': False}).where(cls.user_id == user_id).execute()

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.get_or_none(cls.user_id == user_id)

    @classmethod
    def get_by_logged_user(cls, user_id):
        return cls.get_or_none(cls.user_id == user_id, cls.is_login == True)


class WhatsappMessage(BaseModel):
    id = PrimaryKeyField()
    user_id = IntegerField()
    subscriber_phone = CharField()
    subscriber_name = CharField()
    text = TextField()
    type = CharField()
    tm = DateTimeField()

    TYPE_INCOMING = 'INCOMING'
    TYPE_OUTGOING = 'OUTGOING'

    class Meta:
        db_table = 'whatsapp_message'

    @classmethod
    def add(
            cls,
            user_id,
            subscriber_phone,
            subscriber_name,
            text,
            type,
    ):
        cls.create(
            user_id=user_id,
            subscriber_phone=subscriber_phone,
            subscriber_name=subscriber_name,
            text=text,
            type=type,
        )

    @classmethod
    def get_chat(
            cls,
            user_id,
            subscriber_phone,
    ):
        return list((cls.select().where(
            cls.user_id == user_id,
            cls.subscriber_phone == subscriber_phone
        ).dicts()))

    @classmethod
    def get_subscriber_list(cls, user_id):
        return cls.select().where(
            cls.user_id == user_id,
        ).group_by(cls.subscriber_phone)
