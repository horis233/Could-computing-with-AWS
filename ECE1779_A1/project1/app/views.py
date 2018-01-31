from app import webapp
from flask import render_template

@webapp.route('/',methods=['GET'])
#Return html to the homepage
def main():
    return render_template("main.html")