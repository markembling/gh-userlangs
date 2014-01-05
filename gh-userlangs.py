from __future__ import division
import os
from flask import Flask, request, session, render_template, redirect, url_for
from flask.ext.github import GitHub

# Config
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_CALLBACK_URL = 'http://localhost:5000/callback'

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.environ.get('SESSION_SECRET')
gh = GitHub(app)

@gh.access_token_getter
def token_getter():
    return session.get("github_access_token")

# GitHub functions
def get_gh_repos():
    return gh.get('user/repos')

def get_repo_languages(repo):
    return gh.get('repos/%s/%s/languages' % (repo["owner"]["login"], repo["name"]))

def get_all_languages(repos):
    results = {}
    for r in repos:
        langs = get_repo_languages(r)
        for k, v in langs.items():
            if not k in results:
                results[k] = v
            else:
                results[k] += v
    return results

def get_language_percents(langs):
    results = {}
    total = sum(langs.values())
    for k, v in langs.items():
        results[k] = v / total * 100
    return results


# View functions
@app.route("/")
def index():
    repo_count = None
    langs = None
    langs_percents = None
    if "github_access_token" in session:
        repos = get_gh_repos()
        repo_count = len(repos)
        langs = get_all_languages(repos)
        langs_percents = get_language_percents(langs)

    return render_template("index.html", repo_count=repo_count,
                                         langs=langs,
                                         langs_percents=langs_percents)

@app.route("/auth")
def auth():
    return gh.authorize()

@app.route("/callback")
@gh.authorized_handler
def callback(token):
    next_url = request.args.get('next') or url_for('index')
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
