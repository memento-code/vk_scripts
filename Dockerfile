FROM python:3-onbuild

RUN apt-get update && apt-get install -y \
    cron \
    rsyslog

COPY cron /etc/cron.d/sample
RUN mkdir /data
CMD service rsyslog start && service cron start && tail -f /var/log/syslog