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
time_threshold = f"{int(time_threshold.timestamp())}" # convert to unix timestamp as integer as string
# Connect to the database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Get user_id (these might need to update their sync-clients)
select_query = """
SELECT unique user_id FROM oc_files_lock 
WHERE creation < %s
"""
cursor.execute(select_query, (time_threshold,))
rows = cursor.fetchall() # returns a list of tuples like (user_id, some_other_value)

user_ids = "\n".join([t[0] for t in rows]) # joins the first element of the above tuple to a newline separated string


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
result_message = f"{sys.argv[0]}: {cursor.rowcount} rows from oc_files_lock older than {time_delta_in_hours}h deleted."
print(result_message)

result_message = f"{result_message}\n\n user_ids:\n {user_ids}"
if affected_rows > 0:
    mail_command = f"""mail -s 'nc_files_lock: Deleted values older than {time_delta_in_hours}h' {notify_to_email} << EOF
{result_message}
EOF"""
    os.system(mail_command)