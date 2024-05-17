# cleanup_oc_files_lock.py
Python script to get rid of old entries in Nextclouds oc_files_lock table
created by rakurtz in 2024

## Requirements:
`pip install mysql-connector-python`

## Database cofiguration:
create an unpriviled user for this task!
`CREATE USER 'cleanup_user'@'localhost' IDENTIFIED BY 'some_password';`
`GRANT SELECT, DELETE ON nextcloud.oc_files_lock TO 'cleanup_user'@'localhost';`

## add to crontab via `crontab -e` to be daily run at midnight
`0 0 * * * /usr/bin/python3 /path/to/cleanup_oc_files_lock.py`