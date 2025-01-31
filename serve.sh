#!/usr/bin/env bash

gunicorn --bind `hostname`:8052 --reload --log-level info --workers 1 --threads 8 --timeout 0 main:server
