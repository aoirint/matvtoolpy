# syntax=docker/dockerfile:1.3-labs
ARG BASE_IMAGE=ubuntu:focal
ARG BASE_RUNTIME_IMAGE=${BASE_IMAGE}
FROM ${BASE_IMAGE} AS python-env

ARG DEBIAN_FRONTEND=noninteractive
ARG PYENV_VERSION=v2.3.4
ARG PYTHON_VERSION=3.9.13
ARG PYTHON_ROOT=/opt/python

RUN <<EOF
    apt-get update

    apt-get install -y \
        make \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        wget \
        curl \
        llvm \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libffi-dev \
        liblzma-dev \
        git

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

RUN <<EOF
  git clone https://github.com/pyenv/pyenv.git /opt/pyenv
  git checkout "${PYENV_VERSION}"

  PREFIX=/opt/python-build $PYENV_ROOT/plugins/python-build/install.sh
  /opt/python-build/bin/python-build -v "${PYTHON_VERSION}" "${PYTHON_ROOT}"

  rm -rf /opt/python-build /opt/pyenv
EOF


FROM ${BASE_RUNTIME_IMAGE} AS runtime-env

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

COPY --from=python-env /opt/python /opt/python

ADD requirements.txt /
RUN gosu user pip3 install -r /requirements.txt

ADD --chown=user:user setup.py requirements.in README.md /opt/aoirint_matvtool/
ADD --chown=user:user aoirint_matvtool /opt/aoirint_matvtool/aoirint_matvtool
RUN cd /opt/aoirint_matvtool && \
    gosu user pip3 install .

WORKDIR /work
ENTRYPOINT [ "gosu", "user", "matvtool" ]
