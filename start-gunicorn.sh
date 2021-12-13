#!/bin/bash

exec gunicorn server:app
