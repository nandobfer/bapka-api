#!/bin/sh
cd /home/bapkasorvetes/cupons_webserver/bapka-api
screen -m -d -S bapka-api python3 -m flask run --port=4000 --debugger --host="0.0.0.0" --cert=../../ssl/certs/cupons_bapkasorvetes_com_br_da29f_1faa9_1668268697_1c36aca5cb2cb6eeae02f44c346bc2a3.crt --key=ssl.key

# 04c7e485f4909d3d6c933577843f62c73976