FROM python:3.9

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/user/.local/bin:${PATH}

RUN apt-get update && \
    apt-get install -y \
        gosu \
        ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --non-unique --gid 1000 user && \
    useradd --non-unique --uid 1000 --gid 1000 --create-home user

ADD requirements.txt /
RUN gosu user pip3 install -r /requirements.txt

ADD --chown=user:user setup.py requirements.in README.md /opt/aoirint_matvtool/
ADD --chown=user:user aoirint_matvtool /opt/aoirint_matvtool/aoirint_matvtool
RUN cd /opt/aoirint_matvtool && \
    gosu user pip3 install .

WORKDIR /work
ENTRYPOINT [ "gosu", "user", "matvtool" ]
