# syntax=docker/dockerfile:1
ARG BASE_IMAGE=ubuntu:22.04
ARG BASE_RUNTIME_IMAGE=${BASE_IMAGE}

FROM ${BASE_IMAGE} AS python-env

ARG DEBIAN_FRONTEND=noninteractive
ARG PYENV_VERSION=v2.6.7
ARG PYTHON_VERSION=3.11.13

RUN <<EOF
    set -eu

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
    set -eu

    git clone https://github.com/pyenv/pyenv.git /opt/pyenv
    cd /opt/pyenv
    git checkout "${PYENV_VERSION}"

    PREFIX=/opt/python-build /opt/pyenv/plugins/python-build/install.sh
    /opt/python-build/bin/python-build -v "${PYTHON_VERSION}" /opt/python

    rm -rf /opt/python-build /opt/pyenv
EOF


FROM ${BASE_RUNTIME_IMAGE} AS runtime-env

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/user/.local/bin:/opt/python/bin:${PATH}

RUN <<EOF
    set -eu

    apt-get update
    apt-get install -y \
        gosu \
        ffmpeg
    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

RUN <<EOF
    set -eu

    groupadd --non-unique --gid 1000 user
    useradd --non-unique --uid 1000 --gid 1000 --create-home user
EOF

COPY --from=python-env /opt/python /opt/python

ARG POETRY_VERSION=1.8.5
RUN <<EOF
    set -eu

    gosu user pip install "poetry==${POETRY_VERSION}"

    gosu user poetry config virtualenvs.in-project true

    mkdir -p /home/user/.cache/pypoetry/{cache,artifacts}
    chown -R "user:user" /home/user/.cache
EOF

RUN <<EOF
    set -eu

    mkdir -p /code/matvtoolpy
    chown -R "user:user" /code/matvtoolpy
EOF

ADD ./pyproject.toml ./poetry.lock /code/matvtoolpy/
RUN --mount=type=cache,uid=1000,gid=1000,target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid=1000,gid=1000,target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    cd /code/matvtoolpy
    gosu user poetry install --no-root --only main
EOF

ENV PATH=/code/matvtoolpy/.venv/bin:${PATH}
ADD ./aoirint_matvtool /code/matvtoolpy/aoirint_matvtool
ADD ./README.md /code/matvtoolpy/

RUN --mount=type=cache,uid=1000,gid=1000,target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid=1000,gid=1000,target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    cd /code/matvtoolpy
    gosu user poetry install --only main
EOF

WORKDIR /work
ENTRYPOINT [ "gosu", "user", "matvtool" ]
