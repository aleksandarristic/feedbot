#!/usr/bin/env bash

echo "[$(date +'%m-%d-%Y %H:%M:%S')] - Starting update_feeds.sh script."

# change working dir to where the python script is
cd /path-to-feedbot/

# run python from your .venv
/path-to-feedbot/.venv/bin/python /path-to-feedbot/feedbot.py

# adjust this path to where you want to put your rss feed xml;
# I am putting it to a statically served folder on my server
cp *.xml /var/www/html/rss/

# dirty way to set correct ownership of the xml files in the rss directory. but it works.
sudo chown www-user:www-data /var/www/html/rss/*.xml

echo "[$(date +'%m-%d-%Y %H:%M:%S')] - update_feeds.sh script done."