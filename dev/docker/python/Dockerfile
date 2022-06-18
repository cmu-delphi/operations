# start with a standard python 3 image
FROM python:3.8-buster

# use delphi's timezome
RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime

# specify a working directory inside the container
WORKDIR /usr/src/app

# install python packages
COPY repos/delphi/operations/dev/docker/python/assets/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# copy over all source files
COPY repos repos
RUN chmod -R o+r repos/

# configure the image to match the delphi server
COPY repos/delphi/operations/dev/docker/python/assets/setup.sh .
RUN bash setup.sh
