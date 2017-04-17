# -*- coding: utf-8 -*-
from peewee import *
from settings import WEBSERVER_DB

################
##   PeeWee   ##
################

### Database ###
jentuDB = SqliteDatabase(WEBSERVER_DB)


### Request subscribers ###

def jentuDB_connect():
	jentuDB.connect()

def jentuDB_close():
	if not jentuDB.is_closed():
		jentuDB.close()


### PeeWee Models ###

class BaseModel(Model):
	class Meta:
		database = jentuDB

class Answer(BaseModel):
	id = PrimaryKeyField()
	next_id = ForeignKeyField('self', related_name='parents', db_column='next_id', null=True, index=True, unique=False, on_delete='SET NULL', on_update='CASCADE')
	delay = IntegerField(null=True, default=0)
	message_type = CharField(default='text')
	message = TextField(default='')

	class Meta:
		order_by = ('id',)

class Response(BaseModel):
	id = ForeignKeyField(Answer, related_name='markups', db_column='id', null=True, on_delete='CASCADE', on_update='CASCADE')
	next_id = ForeignKeyField(Answer, related_name='answers', db_column='next_id', null=True, on_delete='CASCADE', on_update='CASCADE')
	text = TextField(default='')

	class Meta:
		indexes = (
			(('id', 'next_id'), False),
		)

class User(BaseModel):
	id = PrimaryKeyField()
	username = TextField(null=True)
	checkpoint = ForeignKeyField(Answer, related_name='saved_users', db_column='checkpoint', default=1, null=True, index=True, unique=False, on_delete='SET DEFAULT', on_update='CASCADE')
	achievement = TextField(default='[]')

	class Meta:
		order_by = ('id',)


### SQLite Functions ###
@jentuDB.transaction()
def get_user(message):
	return User.get_or_create(id=message.from_user.id, defaults={"username": message.from_user.first_name, "checkpoint": 1, "achievement": '[]'})[0]


### Just for debug ###
if __name__ == '__main__':
	jentuDB.create_tables([User, Answer, Response], safe=True)