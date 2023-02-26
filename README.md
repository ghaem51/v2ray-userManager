# v2ray-userManager
python script to add user in v2ray with expire time
## install step
> 1.download usermanger python script   
> 2.update .env file with your v2ray config json file location   
> 3.set cron job to auto remove exp user from config json   
## crontab config
run crontab -e
add this
```
1 12 * * * /usr/bin/python3 /path/to/usermanager.py check_expire
```
this will run check user expire every day at 12:01 AM
## Note
your archived_users.json location must be exist 
you can create empty file with
```
touch /etc/v2ray/archived_users.json
```
