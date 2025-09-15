# syntax=docker/dockerfile:1
ARG PYTHON_IMAGE=python:3.11

FROM "${PYTHON_IMAGE}" AS build-venv

ARG DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /uvx /bin/

# uvの動作設定
# - バイトコードを生成
# - 仮想環境にパッケージの実体をコピー
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Python仮想環境を作成して、依存関係をインストール
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=./uv.lock,target=/opt/aoirint_matvtool/uv.lock \
    --mount=type=bind,source=./pyproject.toml,target=/opt/aoirint_matvtool/pyproject.toml <<EOF
    cd /opt/aoirint_matvtool

    UV_PROJECT_ENVIRONMENT="/opt/python_venv" uv sync --locked --no-dev --no-editable --no-install-project
EOF

# アプリケーションのソースコードを追加
COPY ./aoirint_matvtool /opt/aoirint_matvtool/aoirint_matvtool

# Python仮想環境にPATHを通す
ENV PATH="/opt/python_venv/bin:${PATH}"

# アプリケーションのソースコードを追加
COPY ./aoirint_matvtool /opt/aoirint_matvtool/aoirint_matvtool

# バージョンを置換して、アプリケーションをパッケージとしてインストール
ARG APP_VERSION="0.0.0"
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=./uv.lock,target=/opt/aoirint_matvtool/uv.lock \
    --mount=type=bind,source=./pyproject.toml,target=/opt/aoirint_matvtool/pyproject.toml <<EOF
    cd /opt/aoirint_matvtool

    sed -i "s/__version__ = \"0.0.0\"/__version__ = \"${APP_VERSION}\"/" ./aoirint_matvtool/__init__.py

    UV_PROJECT_ENVIRONMENT="/opt/python_venv" uv sync --locked --no-dev --no-editable
EOF

FROM "${PYTHON_IMAGE}" AS runtime

ARG DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN <<EOF
    set -eu

    apt-get update

    apt-get install -y --no-install-recommends \
        ffmpeg

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

COPY --from=build-venv /opt/python_venv /opt/python_venv
ENV PATH="/opt/python_venv/bin:${PATH}"

USER "1000:1000"

ENTRYPOINT [ "matvtool" ]
