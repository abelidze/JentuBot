# -*- coding: utf-8 -*-
import json
from peewee import *
from settings import WEBSERVER_DB

################
##   PeeWee   ##
################

### Database ###
jentuDB = SqliteDatabase(WEBSERVER_DB, pragmas=( ('journal_mode', 'MEMORY'), ('foreign_keys', 1), ))


### Deffered Types ###
DeferredSave = DeferredRelation()


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
	answer_id = PrimaryKeyField()
	next_id = ForeignKeyField('self', related_name='parents', db_column='next_id', null=True, index=True, unique=False, on_delete='SET NULL', on_update='CASCADE')
	delay = FloatField(null=True, default=0.0)
	force_send = BooleanField(default=False)
	message_type = CharField(default='text')
	message = TextField(default='')

	class Meta:
		order_by = ('answer_id',)


class User(BaseModel):
	user_id = PrimaryKeyField()
	username = CharField(null=True)
	menu_id = IntegerField(null=True)
	checkpoint = ForeignKeyField(Answer, related_name='saved_users', db_column='checkpoint', default=1, null=True, index=True, unique=False, on_delete='SET DEFAULT', on_update='CASCADE')
	saving = IntegerField(default=-1)
	state = TextField(default='wait')
	lang = CharField(default='ru')

	# Function will return a 2-tuple: (user=object, created=bool)
	@jentuDB.transaction()
	def create_user(message):
		return User.get_or_create(user_id=message.from_user.id, defaults={"username": message.from_user.first_name, "menu_id": -1, "checkpoint": 1, "saving": -1, "state": 'wait', "lang": 'ru'})

	# Function will check user, his stopping and return <user: object> or None on fail
	@jentuDB.transaction()
	def get_user(message, error="GET-USER ERROR "):
		try:
			user = User.get(User.user_id == message.from_user.id)
		except User.DoesNotExist:
			log(error, message.from_user)
			return None

		if(user.state == 'stop'):
			return None

		return user

	# Function will return executed update query or None if it failed
	@jentuDB.transaction()
	def update_user(self=None, user_id=None, **kwargs):
		if user_id is None:
			if self is None:
				return None
			else:
				user_id = self.user_id
		return (User.update(**kwargs).where(User.user_id == user_id)).execute()

	# Function will return executed delete query
	@jentuDB.transaction()
	def delete_user(user_id):
		return (User.delete().where(User.user_id == user_id)).execute()

	# Restart user's invisible goals
	@jentuDB.transaction()
	def restart_goals(self=None, user_id=None):
		if user_id is None:
			if self is None:
				return False
			else:
				user_id = self.user_id
		try:
			achieves = Achievement.select().where(Achievement.visible == False)
			Goal.delete().where(Goal.user == user_id, Goal.achievement.in_(achieves)).execute()
			return True
		except:
			return False

	# Load user's invisible goals
	@jentuDB.transaction()
	def load_goals(self=None, user_id=None, save_id=None):
		if save_id is None:
			return None
		if user_id is None:
			if self is None:
				return False
			else:
				user_id = self.user_id
		return True

	# Restart game
	@jentuDB.transaction()
	def restart_game(self=None, user_id=None):
		if self is None:
			if user_id is None:
				return False
			else:
				try:
					self = User.get(User.user_id == user_id)
				except:
					return False
		self.restart_goals()
		return self.update_user(state='wait', checkpoint=1)

	# Load game
	@jentuDB.transaction()
	def load_game(self=None, user_id=None, save_id=None):
		if save_id == None:
			return False
		if self is None:
			if user_id is None:
				return False
			else:
				try:
					self = User.get(User.user_id == user_id)
				except:
					return False
		try:
			save = Save.get(Save.id == save_id)
		except Save.DoesNotExist:
			return False
		
		goal_data = json.loads(save.data)
		self.restart_goals()
		try:
			if(len(goal_data) > 0):
				row_dic = ({'user': self.user_id, 'achievement': goal_achieve, 'value': goal_value, 'active': goal_active} for goal_achieve, goal_value, goal_active in goal_data)
				Goal.insert_many(row_dic).execute()
		except:
			print('WTF')
			return False

		return save.saved_id

	# Save game
	@jentuDB.transaction()
	def save_game(self=None, user_id=None, caption=None, save_id=None):
		if self is None:
			if user_id is None:
				return False
			else:
				try:
					self = User.get(User.user_id == user_id)
				except:
					return False

		a_data = json.dumps([(goal.achievement.achievement_id, goal.value, goal.active) for goal in self.user_goals.join(Achievement).where(Achievement.visible == False)])
		if(caption != None):
			if(Save.select().where(Save.title == caption).exists()):
				return False
			return Save.create(user=self.user_id, saved_id=self.checkpoint, title=caption, data=a_data)

		elif(save_id != None):
			self.update_user(saving=save_id)
			return (Save.update(saved_id=self.checkpoint, data=a_data).where(Save.id == save_id)).execute()

		elif(self.saving != None):
			return (Save.update(saved_id=self.checkpoint, data=a_data).where(Save.id == self.saving)).execute()

		return False

	# Save game
	@jentuDB.transaction()
	def delete_game(self=None, user_id=None, save_id=None):
		if save_id == None:
			return False
		if self is None:
			if user_id is None:
				return False
			else:
				try:
					self = User.get(User.user_id == user_id)
				except:
					return False
		try:
			self.update_user(saving=-1)
			(Save.delete().where(Save.id == save_id)).execute()
			return True
		except:
			return False

	# Function will process achievement and return:
	# * True if it's reached (only once),
	# * False if not or failed
	@jentuDB.transaction()
	def process_achievement(self=None, user_id=None, achieve_id=1):
		if(achieve_id == None) or (achieve_id == ''):
			return False

		if user_id is None:
			if self is None:
				return False
			else:
				user_id = self.user_id

		goal = Goal.get_or_create(user=user_id, achievement=achieve_id, defaults={"value": 0, "active": False})[0]

		if not goal.active:
			goal.value += 1
			goal.save()
			return goal.check()
		else:
			return False

	class Meta:
		order_by = ('user_id',)


class Achievement(BaseModel):
	achievement_id = PrimaryKeyField()
	achievement_type = TextField(default='default')
	visible = BooleanField(default=True)
	caption = CharField(null=True, default='\U0001F31F')
	name = CharField(null=True, default='Unknown achievement')
	content = TextField(null=True, default='No content')
	objective = IntegerField(default=1)

	class Meta:
		order_by = ('achievement_id',)


class Response(BaseModel):
	id = PrimaryKeyField()
	answer_id = ForeignKeyField(Answer, related_name='markups', db_column='answer_id', null=True, on_delete='CASCADE', on_update='CASCADE')
	next_id = ForeignKeyField(Answer, related_name='answers', db_column='next_id', null=True, on_delete='CASCADE', on_update='CASCADE')
	achieve_id = ForeignKeyField(Achievement, related_name='activators', db_column='achieve_id', null=True, on_delete='SET NULL', on_update='CASCADE')
	requirement = TextField(default='[]')
	text = TextField(default='')

	class Meta:
		indexes = (
			(('answer_id', 'next_id'), False),
		)
		order_by = ('answer_id',)


class Save(BaseModel):
	id = PrimaryKeyField()
	user = ForeignKeyField(User, related_name='user_saves', db_column='user', null=True, on_delete='CASCADE', on_update='CASCADE')
	saved_id = ForeignKeyField(Answer, related_name='attached_saves', db_column='saved_id', null=True, on_delete='CASCADE', on_update='CASCADE')
	title = CharField(null=True, default='User-Save')
	data = TextField(default='[]')

	class Meta:
		indexes = (
			(('user', 'saved_id'), False),
		)
		order_by = ('user',)


class Goal(BaseModel):
	user = ForeignKeyField(User, related_name='user_goals', db_column='user', null=True, on_delete='CASCADE', on_update='CASCADE')
	achievement = ForeignKeyField(Achievement, related_name='attached_goals', db_column='achievement', null=True, on_delete='CASCADE', on_update='CASCADE')
	value = IntegerField(default=0)
	active = BooleanField(default=False)

	@jentuDB.transaction()
	def check(self=None, user_id=None, achievement_id=None):
		if self is None:
			if(achievement_id is None) or (user_id is None):
				return None
			else:
				self = Goal.get(Goal.user == user_id, Goal.achievement == achievement_id)

		if not self.active:
			if(self.achievement.objective <= self.value):
				self.active = True
				self.save()

		return self.active

	class Meta:
		indexes = (
			(('user', 'achievement'), False),
		)
		order_by = ('user',)


DeferredSave.set_model(Save)


### Just for debug ###
if __name__ == '__main__':
	jentuDB.create_tables([User, Answer, Response, Achievement, Goal, Save], safe=True)