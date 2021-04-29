@ECHO OFF
setlocal enabledelayedexpansion

:wait
set /a "hour=%hour:~0,2%"
set /a "hour=!hour: =!"
set /a "minu=%time:~3,2%"
set /a "minu=!minu: =!"
if !minu! LEQ 15 (
	set /a "delay=(15-!minu!)*60+21600"
)
if !minu! GTR 15 (
	set /a "delay=(75-!minu!)*60+21600"
)
timeout !delay!

:loop
set updtime=%date%, %time%
git pull
FetchData.py
Caller.py
git add --all --verbose
git commit -m "Auto-updater - %updtime%" --verbose
git push --verbose
goto wait
