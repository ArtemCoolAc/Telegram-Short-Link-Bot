# Telegram-Short-Link-Bot
A simple bot on Python3 with Telegram API. 
The bot has 2 functions: 
 1. return short variant of link using https://rel.ink/
 2. asking for return several (e.g. 10) last successful links.
 
# Shortening 
The bot uses API https://rel.ink/api/links/ </br> So you are able to make links like https://rel.ink/RgeNkO </br>
You need to use command /shorten and URL you want to make shorter. </br>
For example:
after sending a message </br> /shorten https://mail.ru </br>
you will get the answer <q>Сокращенная ссылка https://rel.ink/nKDQvx</q> (the text is in Russian) </br>
Be careful! Please include schema to URL because only valid URL can be shortened or you'll get appropriate message.

# History
It is possible to get history of last several successful shortenings. </br>
The suitable command for it is: /history <i>quantity</i> The default value is 10 </br>
The output is carried out in reverse chronological order with mentionting user URL, short URL and date with time

# Building and running
What you need to do:
1. clone repository (git clone https://github.com/ArtemCoolAc/Telegram-Short-Link-Bot)
2. install docker and docker-compose if not installed
3. create your new bot using BotFather in Telegram and copy API Token
4. create .env file:</br>
POSTGRES_USER=</br>
POSTGRES_DB=</br>
POSTGRES_PASSWORD=</br>
POSTGRES_HOST=postgresql</br>
POSTGRES_PORT=5432</br>
PGDATA=/var/lib/postgresql/data/pgdata</br>
TELEGRAM_TOKEN=</br>
Fulfill empty fields with some text data you like
5. build and run with following commands: </br>
docker-compose build</br>
docker-compose up -d</br>
