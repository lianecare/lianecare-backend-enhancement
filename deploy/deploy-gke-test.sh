#!/bin/bash

docker buildx build --platform linux/amd64 -f compose/production/django/Dockerfile -t europe-west3-docker.pkg.dev/lianecare-342010/solace/solace:test .

docker push europe-west3-docker.pkg.dev/lianecare-342010/solace/solace:test
