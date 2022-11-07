# https://github.com/docker-library/haproxy/blob/b07fcf19b4ee54ef37ffbf7241372961ddc97b8c/2.4/alpine/Dockerfile

FROM alpine:3.16

# roughly, https://git.alpinelinux.org/aports/tree/main/haproxy/haproxy.pre-install?h=3.12-stable
RUN set -eux; \
  addgroup --gid 99 --system haproxy; \
  adduser \
    --disabled-password \
    --home /var/lib/haproxy \
    --ingroup haproxy \
    --no-create-home \
    --system \
    --uid 99 \
    haproxy \
  ; \
  mkdir /var/lib/haproxy; \
  chown haproxy:haproxy /var/lib/haproxy

ENV HAPROXY_VERSION 2.4.19

# copy local haproxy
WORKDIR /usr/src/haproxy
COPY haproxy .

# see https://sources.debian.net/src/haproxy/jessie/debian/rules/ for some helpful navigation of the possible "make" arguments
RUN set -eux; \
  \
  apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    linux-headers \
    lua5.3-dev \
    make \
    openssl \
    openssl-dev \
    pcre2-dev \
    readline-dev \
    tar \
  ; \
  \
  makeOpts=' \
    TARGET=linux-musl \
    USE_GETADDRINFO=1 \
    USE_LUA=1 LUA_INC=/usr/include/lua5.3 LUA_LIB=/usr/lib/lua5.3 \
    USE_OPENSSL=1 \
    USE_PCRE2=1 USE_PCRE2_JIT=1 \
    USE_PROMEX=1 \
    \
    EXTRA_OBJS=" \
    " \
  '; \
  \
  nproc="$(getconf _NPROCESSORS_ONLN)"; \
  eval "make -C /usr/src/haproxy -j '$nproc' all $makeOpts"; \
  eval "make -C /usr/src/haproxy install-bin $makeOpts"; \
  \
  mkdir -p /usr/local/etc/haproxy; \
  cp -R /usr/src/haproxy/examples/errorfiles /usr/local/etc/haproxy/errors; \
  rm -rf /usr/src/haproxy; \
  \
  runDeps="$( \
    scanelf --needed --nobanner --format '%n#p' --recursive /usr/local \
      | tr ',' '\n' \
      | sort -u \
      | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }' \
  )"; \
  apk add --no-network --virtual .haproxy-rundeps $runDeps; \
  apk del --no-network .build-deps; \
  \
# smoke test
  haproxy -v

# https://www.haproxy.org/download/1.8/doc/management.txt
# "4. Stopping and restarting HAProxy"
# "when the SIGTERM signal is sent to the haproxy process, it immediately quits and all established connections are closed"
# "graceful stop is triggered when the SIGUSR1 signal is sent to the haproxy process"
STOPSIGNAL SIGUSR1

COPY  --chmod=755 haproxy_docker_entrypoint.sh /usr/local/bin/
ENTRYPOINT ["haproxy_docker_entrypoint.sh"]

USER haproxy
CMD ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]