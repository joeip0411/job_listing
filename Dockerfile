# BUILD: docker build --rm -t airflow .
# ORIGINAL SOURCE: https://github.com/puckel/docker-airflow

# FROM python:3.7-slim
FROM ubuntu:22.04
LABEL version="1.0"
LABEL maintainer="joeip"

# Never prompts the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Airflow
ARG AIRFLOW_VERSION=2.6.3
ENV AIRFLOW_HOME=/usr/local/airflow
ENV AIRFLOW_GPL_UNIDECODE=yes

# celery config
ARG CELERY_REDIS_VERSION=5.2.7
ARG PYTHON_REDIS_VERSION=4.6.0

ARG TORNADO_VERSION=6.2
ARG WERKZEUG_VERSION=2.2.3
ARG PYOPENSSL_VERSION=23.2.0
ARG PYTZ_VERSION=2023.3
ARG PYASN1_VERSION=0.4.8

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8
ENV LC_ALL en_US.UTF-8

ENV TZ=UTC

RUN mkdir -p /usr/share/man/man1/

RUN set -ex \
    && buildDeps=' \
        python3-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        build-essential \
        libblas-dev \
        liblapack-dev \
        libpq-dev \
        git \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        ${buildDeps} \
        sudo \
        python3-pip \
        python3-requests \
        default-mysql-client \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat-traditional \
        locales \
        openjdk-8-jre-headless \
        python3.10-venv \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow \
    && pip install -U pip setuptools wheel \
    && pip install Cython \
    && pip install pytz==${PYTZ_VERSION} \
    && pip install pyOpenSSL==${PYOPENSSL_VERSION} \
    && pip install ndg-httpsclient \
    && pip install pyasn1==${PYASN1_VERSION} \
    && pip install apache-airflow[async,crypto,celery,kubernetes,jdbc,password,postgres,s3,slack,amazon,pandas,docker]==${AIRFLOW_VERSION} --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.6.3/constraints-3.7.txt\
    && pip install werkzeug==${WERKZEUG_VERSION} \
    && pip install redis==${PYTHON_REDIS_VERSION} \
    && pip install celery[redis]==${CELERY_REDIS_VERSION} \
    && pip install flask_oauthlib \
    && pip install psycopg2-binary \
    && pip install tornado==${TORNADO_VERSION} \
    && apt-get purge --auto-remove -yqq ${buildDeps} \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

COPY airflow/config/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R airflow: ${AIRFLOW_HOME}

USER airflow

COPY airflow/requirements.txt .
RUN pip install --user -r requirements.txt --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.6.3/constraints-3.7.txt

COPY airflow/config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

COPY airflow/dags ${AIRFLOW_HOME}/dags
COPY airflow/tests ${AIRFLOW_HOME}/tests
COPY airflow/CI ${AIRFLOW_HOME}/CI
COPY infra ${AIRFLOW_HOME}/infra

ENV PYTHONPATH ${AIRFLOW_HOME}

EXPOSE 8080 5555 8793

WORKDIR ${AIRFLOW_HOME}

RUN python3 -m venv dbt_venv \
    && . dbt_venv/bin/activate \
    && pip install --no-cache-dir dbt-spark[PyHive] dbt-core \
    && deactivate

ENTRYPOINT ["/entrypoint.sh"]
