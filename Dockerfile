FROM python:3.12.4-alpine

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN apk update

# 安装带有旧版 libcurl 的 curl
RUN apk add --update build-base cmake c-ares-dev
RUN cp examples/curl-7.71.0.tar.gz /tmp
RUN tar -xvf /tmp/curl-7.71.0.tar.gz -C /tmp/
RUN cd /tmp/curl-7.71.0 && ./configure --enable-ares && make && make install

# 安装锁定的运行时依赖
RUN uv sync --frozen --no-default-groups

# 降权后下载的文件将写入此目录。
RUN mkdir -p /usr/src/app/loot && chown 1000:1000 /usr/src/app/loot

# 将 uv 运行时状态保存在非特权用户可写的位置。
ENV UV_CACHE_DIR=/tmp/uv-cache

ENTRYPOINT ["uv", "run", "--no-sync", "python3"]
