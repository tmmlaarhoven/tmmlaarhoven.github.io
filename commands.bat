SET updtime = %date%, %time%
git pull
REM fetchdata.py
REM rankings.py
REM website.py
git add --all --verbose
git commit -m "Auto-update - %updtime%" --verbose
git push --verbose
