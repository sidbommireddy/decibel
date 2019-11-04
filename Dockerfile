FROM python:3.7-slim AS compile-image
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

# The COPY Dockerfile instruction adds files into the image as a new layer.
# It is common to use the COPY instruction to copy your application code into an image.

RUN mkdir /app

WORKDIR /app

COPY src/decibelinsights.py /app

COPY requirements.txt ./requirements.txt

# The RUN Dockerfile instruction allows you to run commands inside the image which create new layers.
# Each RUN instruction creates a single new layer.
RUN pip install -r requirements.txt

# The EXPOSE Dockerfile instruction documents the network port that the application uses.
EXPOSE 5000

# The ENTRYPOINT Dockerfile instruction sets the default application to run when the image is started as a container.

# CMD python ./decibelinsights.py

ENTRYPOINT [ "python" ]

CMD [ "decibelinsights.py" ]


