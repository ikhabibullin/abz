#!/bin/sh

echo "waiting for postgres..."

while  ! nc -z postgres 5432; do
  sleep 0.1
done

echo "postgres started"

exec "$@"