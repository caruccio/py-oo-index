# -*- coding: utf-8 -*-

import os, sys
from flask import Flask, g, request, session, url_for, redirect, flash, render_template
from flask.ext.github import GitHub

app = Flask(__name__)
try:
	app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_CLIENT_ID']
	app.config['GITHUB_CLIENT_SECRET'] = os.environ['GITHUB_CLIENT_SECRET']
	app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me')

except KeyError, ex:
	app.config['GITHUB_CLIENT_ID'] = 'FAKE-CLIENT-ID'
	app.config['GITHUB_CLIENT_SECRET'] = 'FAKE-CLIENT-SECRET'
	print >>sys.stderr, "Missing config: %s (Please fix)" % ex

app.config['GITHUB_CALLBACK_URL'] = 'http://' + os.environ.get('OPENSHIFT_APP_DNS', 'localhost:5000') + '/login/callback'

github = GitHub(app)

## authentication ##########

@app.before_request
def before_request():
	try:
		g.user = session['user']
	except KeyError:
		g.user = None

@app.route('/login')
def login():
	return github.authorize()

@app.route('/login/callback')
@github.authorized_handler
def authorized(token):
	next_url = request.args.get('next') or url_for('index')
	if token is None:
		return redirect(next_url)

	session['token'] = token
	session['user']  = github.get('user')['login']
	return redirect(next_url)

@github.access_token_getter
def token_getter():
	return session.get('token')

@app.route('/logout')
def logout():
	session.pop('user', None)
	session.pop('token', None)
	return redirect(url_for('index'))

## views ############

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
	if not g.user:
		return redirect(url_for('login'))

	form_data = {}
	if request.method == 'POST':
		try:
			form_data['type'] = request.form['type']
			form_data['github-username'] = request.form['github-username']
			form_data['github-repository'] = request.form['github-repository']
		except KeyError, ex:
			flash('Missing field: %s' % ex)
			return render_template('add.html') #, **form_data)
		form_data['alternate-name'] = request.form.get('alternate-name')
		form_data['cartridges'] = request.form.get('cartridges')
		send_pull_request(form_data)
	return render_template('add.html') #, **form_data)

def send_pull_request(form_data):
	flash("Error", "error")

##########################
if __name__ == "__main__":
	app.run(debug=True)
