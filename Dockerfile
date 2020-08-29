FROM python:3.7

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN mkdir /application
COPY ./requirements.txt ./application/requirements.txt
RUN pip install -r ./application/requirements.txt

COPY ./ application
WORKDIR /application