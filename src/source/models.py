# src/source/models.py
from peewee import Model, CharField, IntegerField, SqliteDatabase
from src.settings import settings

# Initialize the database connection
db = SqliteDatabase(settings.db_url.replace('sqlite:///', ''))

class BaseModel(Model):
    class Meta:
        database = db

class Channel(BaseModel):
    channel_id = CharField(primary_key=True)
    last_message_id = IntegerField(null=True)
