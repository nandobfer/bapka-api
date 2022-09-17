#!/bin/sh
cd /home/bapkasorvetes/cupons_webserver/bapka-api
screen -m -d -S bapka-api flask run --port=4000 --debugger=true --host="0.0.0.0" --cert=ssl.crt --key=ssl.key