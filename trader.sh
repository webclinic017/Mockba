#!/bin/bash

# Activate the virtual environment
source /opt/Mockba/venv/bin/activate
echo 'Start trader'
# Execute the Python script
/opt/Mockba/venv/bin/python3 /opt/Mockba/forever.py /opt/Mockba/TelegramBot.py

#echo 'Start Telegram Bot'
#/opt/Mockba/venv/bin/python3 /opt/Mockba/forever.py /opt/Mockba/TelegramBot.py
exit 0
