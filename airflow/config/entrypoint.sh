#!/usr/bin/env bash
# ORIGINAL SOURCE: https://github.com/nicor88/aws-ecs-airflow/

case "$1" in
  webserver)
    airflow db init
		sleep 5
    exec airflow webserver
    ;;
  scheduler)
    sleep 15
    exec airflow "$@"
    ;;
  version)
    exec airflow "$@"
    ;;
  *)
    exec "$@"
    ;;
esac
