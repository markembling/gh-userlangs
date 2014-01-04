import os
from flask import Flask, request, session, render_template, redirect, url_for, render_template_string
from flask.ext.github import GitHub

# Config
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_CALLBACK_URL = 'http://localhost:5000/callback'

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.environ.get('SESSION_SECRET')
gh = GitHub(app)

@app.route("/")
def home():
    t = 'Introduction page goes here. <a href="{{ url_for("auth") }}">Auth me</a>'
    return render_template_string(t)

@app.route("/auth")
def auth():
    return gh.authorize()

@app.route("/callback")
@gh.authorized_handler
def callback(token):
    next_url = request.args.get('next') or url_for('home')
    if token is None:
        #flash("Authorization failed.")
        #return redirect(next_url)
        return "Authorization failed"

    session['github_access_token'] = token
    return redirect(next_url)

# Temporary testing function to see the current auth token
@app.route('/temp')
def temp():
    return session['github_access_token']

if __name__ == '__main__':
    app.run(debug=True)
