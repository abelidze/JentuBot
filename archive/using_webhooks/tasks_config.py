# -*- coding: utf-8 -*-
from celery import Celery

app = Celery('tasks_config', broker='redis://127.0.0.1:8060//', include=['tasks'])