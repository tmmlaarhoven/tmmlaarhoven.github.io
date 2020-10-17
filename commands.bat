SET updmessage = "Auto-update - %date%, %time%"
git pull
REM fetchdata.py
REM rankings.py
REM website.py
git add --all --verbose
git commit -m %updmessage% --verbose
git push --verbose
