#!/bin/bash

systemctl restart redis-server
sudo docker run -d --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management
source task1_env/bin/activate
python3 ./source/start_server.py
