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
EXPOSE 80

CMD git clone -b ${branch:-master} http://github.com/pantherhackers/PantherBot; cd ./PantherBot; ./setup.sh; ./start.sh
