#!/bin/bash

source task1_env/bin/activate
python3 -m grpc_tools.protoc -I=./source --python_out=./source --grpc_python_out=./source --pyi_out=./source ./source/chatServer.proto
