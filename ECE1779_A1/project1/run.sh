#!/bin/bash
/home/ubuntu/Desktop/ece1779/aws/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers=1 --access-logfile access.log --error-logfile error.log app:webapp