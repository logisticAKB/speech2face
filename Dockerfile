FROM python:3.8

WORKDIR /usr/src/speech2face

COPY ./requirements.txt /usr/src/speech2face/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/speech2face/entrypoint.sh

COPY . /usr/src/speech2face/

ENTRYPOINT ["/usr/src/speech2face/entrypoint.sh"]