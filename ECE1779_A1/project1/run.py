#!venv/bin/python
from app import webapp
from manager import admin
webapp.run(host='0.0.0.0',debug=True)
# admin.run(host='0.0.0.0',debug=True)