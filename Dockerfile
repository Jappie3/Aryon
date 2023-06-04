FROM alpine:3.18.0

COPY ./requirements.txt /app/requirements.txt

RUN apk add --no-cache --virtual=build-deps gcc musl-dev python3-dev libffi-dev \
	&& apk add --no-cache curl python3 py3-pip su-exec \
	&& python3 -m pip install --upgrade pip \
    && python3 -m pip install -r /app/requirements.txt \
    # create Aryon user
	&& addgroup -g 2002 aryon \
	&& adduser -D -s /bin/false -H -u 2002 -G aryon aryon \
    # set permissions & ownership
    && chmod -R 770 /app \
    && chown -R aryon:aryon /app \
    # cleanup
	&& apk del --purge build-deps \
	&& rm -fr /root/.cache

COPY ./entrypoint.sh /
RUN chmod 770 /entrypoint.sh \
	&& chown aryon:aryon /entrypoint.sh

HEALTHCHECK --interval=30s --retries=3 CMD curl --fail http://localhost:5000 || exit 1
EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
