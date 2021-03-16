@ECHO OFF
setlocal enabledelayedexpansion

:wait
set /a "hour=%hour:~0,2%"
set /a "hour=!hour: =!"
set /a "minu=%time:~3,2%"
set /a "minu=!minu: =!"
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
FetchData.py
FetchDataSpecial.py
Rankings.py
ScanPlayers.py
if !hour! GTR 22 (
	MakePlots.py
	RankingsUsers.py
)
Website.py
git add --all --verbose
git commit -m "Auto-updater - %updtime%" --verbose
git push --verbose
goto wait
