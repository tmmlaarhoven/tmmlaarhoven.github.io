setlocal enabledelayedexpansion
@ECHO OFF

:wait
set /a "minu=%time:~3,2%"
if !minu! LEQ 15 (
	set /a "delay=(15-!minu!)*60"
)
if !minu! GTR 15 (
	set /a "delay=(75-!minu!)*60"
)
timeout !delay!

:loop
set updtime=%date%, %time%
git pull
fetchdata.py
fetchdata-special.py
rankings.py
website.py
git add --all --verbose
git commit -m "Auto-updater - %updtime%" --verbose
git push --verbose
goto wait
