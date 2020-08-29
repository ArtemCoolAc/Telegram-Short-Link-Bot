FROM python:3.7

RUN mkdir /application
COPY ./requirements.txt ./application/requirements.txt
RUN pip install -r ./application/requirements.txt

COPY ./ application
WORKDIR /application