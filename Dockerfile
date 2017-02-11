FROM debian:wheezy-slim

RUN apt-get update; apt-get install -y \
	build-essential \
	libssl-dev \
	libffi-dev \
	python-dev \
	python-pip \
	git

RUN pip install --upgrade pip
RUN pip install urllib3[secure]

COPY ./ ./PantherBot
WORKDIR ./PantherBot
RUN ./setup.sh 

EXPOSE 80


CMD ./start.sh
