@echo off
chcp 1251
title JentuBot

cd ..
cls
echo Starting JentuBot Services...
sleep 1
start "Redis" cmd /k "title 'Redis' && cd config && redis-server redis.conf"
sleep 2
echo Redis started!
start "Celery" cmd /k "title 'Celery' && celery worker -A tasks --loglevel=info"
sleep 2
echo Celery started!
start "JentuPHP" cmd /k "title 'JentuPHP' && cd jentudb && php -S 0.0.0.0:80 router.php"
sleep 1
echo JentuPHP started!
sleep 1

:loop
python main.py
echo "JentuBot is crashed!"
echo.
echo "###########################################"
echo "#       JentuBot is restarting now        #"
echo "###########################################"
goto loop