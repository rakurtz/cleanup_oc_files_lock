# cleanup_oc_files_lock.py
# Python script to get rid of old entries in Nextclouds oc_files_lock table
# created by rakurtz in 2024
#
# Requirements:
# `pip install mysql-connector-python`
#
# Database cofiguration:
# create an unpriviled user for this task!
# CREATE USER 'cleanup_user'@'localhost' IDENTIFIED BY 'some_password';
# GRANT SELECT, DELETE ON nextcloud.oc_files_lock TO 'cleanup_user'@'localhost';
#
# add to crontab via `crontab -e` to be daily run at midnight
# `0 0 * * * /usr/bin/python3 /path/to/cleanup_oc_files_lock.py`

import sys
import os
import mysql.connector
from datetime import datetime, timedelta


# My script params
time_delta_in_hours = 24
notify_to_email = "name@email.com"

db_config = {
    'user': 'cleanup_user',
    'password': 'some_password',
    'host': 'localhost',
    'database': 'nextcloud'
}

# Calculate the timestamp for 24 hours ago
time_threshold = datetime.now() - timedelta(hours=time_delta_in_hours)

# Connect to the database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Delete records older than 24 hours
delete_query = """
DELETE FROM oc_files_lock 
WHERE creation < %s
"""

cursor.execute(delete_query, (time_threshold,))
conn.commit()
affected_rows = cursor.rowcount

# Close the connection
cursor.close()
conn.close()

# print result and notify via mail if result > 0
result_message = f"{sys.argv[0]}: {cursor.rowcount} rows from oc_files_lock older than 24h deleted."
print(result_message)

if affected_rows > 0:
    mail_command = f"echo {result_message} | mail -s 'nc_files_lock: Deleted values older than {time_delta_in_hours}h' {notify_to_email}"
    os.system(mail_command)
