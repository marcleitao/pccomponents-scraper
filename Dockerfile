FROM python:3.8-alpine
ENV PORT=8081
ADD . /tmp/
WORKDIR /tmp
RUN set -ex \
  && apk update \
  && apk add --no-cache build-base curl dumb-init --update openssl \
  && rm -rf /var/cache/apk/* \
  && pip install bs4 requests slackclient
EXPOSE ${PORT}
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python", "webscraper.py"]
