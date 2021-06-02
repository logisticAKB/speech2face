FROM python:3.8

WORKDIR /storage/speech2face

COPY ./requirements.txt /storage/speech2face/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get -y update
RUN apt-get install -y libsndfile1 ffmpeg

COPY ./entrypoint.sh /storage/speech2face/entrypoint.sh

COPY . /storage/speech2face/

ENTRYPOINT ["/storage/speech2face/entrypoint.sh"]