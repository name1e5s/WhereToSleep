#!/bin/bash

# use root user to execute this script

pkill uvicorn
echo YOUR_PASSWORD_HERE | openconnect --protocol=gp --user=YOUR_USERNAME_HERE --passwd-on-stdin  vpn.bupt.edu.cn&
sleep 60
python3 jwgl.py
pkill openconnect
SLEEP_LIST=result.json JWGL_LIST=jwgl.json uvicorn backend:app --host 0.0.0.0 --port 4514&