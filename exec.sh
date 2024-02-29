#!/usr/bin/env bash

docker build -t codeblind.ai/app .
docker run -p 3000:3000 --init codeblind.ai/app