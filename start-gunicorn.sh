#!/bin/bash

exec gunicorn server:app -k gevent --worker-connections 1000
