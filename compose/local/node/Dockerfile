FROM node:10-stretch-slim

WORKDIR /app

COPY ./package.json /app

RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y python2.7
RUN npm config set python /usr/bin/python2.7

RUN npm install && npm cache clean --force

ENV PATH ./node_modules/.bin/:$PATH
