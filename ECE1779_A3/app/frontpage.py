from flask import render_template, redirect, url_for, session
from app import webapp, index


@webapp.route('/')
def frontpage():
        if 'username' in session and session['authenticated'] is True:
                username = session['username']
                return redirect(url_for('index', username=username))
        else:
                return render_template('frontpage.html')
