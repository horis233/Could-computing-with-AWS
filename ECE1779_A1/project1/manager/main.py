from flask import render_template, redirect, url_for, request, g
from manager import admin


@admin.route('/',methods=['GET'])
@admin.route('/index',methods=['GET'])
@admin.route('/main',methods=['GET'])
# Display an HTML page with links
def main():
    return render_template("main.html",title="Landing Page")
