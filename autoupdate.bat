set updtime=%date%, %time%
git pull
fetchdata.py
rankings.py
website.py
git add --all --verbose
git commit -m "Auto-updater - %updtime%" --verbose
git push --verbose
