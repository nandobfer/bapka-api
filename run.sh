#!/bin/sh
cd /home/bapkasorvetes/cupons_webserver/bapka-api
screen -m -d -S bapka-api python3 -m flask run --port=4000 --debugger --host="0.0.0.0" --cert=cupons_bapkasorvetes_com_br.crt --key=ssl.key