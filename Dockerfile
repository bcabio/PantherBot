FROM mhijazi1/pantherbot-env

COPY . /PantherBot
WORKDIR /PantherBot

RUN ./setup.sh

EXPOSE 80
CMD ./start.sh