from __future__ import division
import os
import json
from collections import OrderedDict
from flask import (Flask, request, session, render_template, jsonify, 
                   redirect, url_for, flash, make_response)
from flask.ext.github import GitHub, GitHubError

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
    return sorted(gh.get('user/repos'), key=lambda x: x["name"])

def get_repo_languages(repo):
    return gh.get('repos/%s/%s/languages' % (repo["owner"]["login"], repo["name"]))

def get_all_languages(repos):
    results = {}
    total_bytes = 0

    # Get all the raw data
    for r in repos:
        langs = get_repo_languages(r)
        for k, v in langs.items():
            if not k in results:
                results[k] = {}
                results[k]["bytes"] = v
                results[k]["repos"] = [r["name"]]
            else:
                results[k]["bytes"] += v
                results[k]["repos"].append(r["name"])
            total_bytes += v

    # Calculate percentages
    for k, v in results.items():
        results[k]["percent"] = v["bytes"] / total_bytes * 100

    return OrderedDict(sorted(results.items(), key=lambda x: x[1]["bytes"], 
                                               reverse=True))

# View functions
@app.route("/")
def index():
    if not "github_access_token" in session:
        return redirect(url_for('intro'))
    return render_template("index.html")

@app.route("/data")
def data():
    if not "github_access_token" in session:
        return make_response(jsonify({'error': 'No access token.'}), 403)

    try:
        repos = get_gh_repos()
        langs = get_all_languages(repos)
        return jsonify(user=session["github_user"],
                       repo_count=len(repos),
                       langs=langs)
    except GitHubError, e:
        session.pop('github_access_token', None)
        session.pop('github_user', None)
        return make_response(jsonify({'error': str(e)}), 403)

@app.route("/intro")
def intro():
    if "github_access_token" in session:
        return redirect(url_for('index'))
    return render_template("intro.html")

@app.route("/auth")
def auth():
    return gh.authorize()

@app.route("/callback")
@gh.authorized_handler
def callback(token):
    next_url = request.args.get('next') or url_for('index')
    if token is None:
        flash("There was a problem authorizing.")
        return redirect(url_for("intro"))

    session['github_access_token'] = token
    session['github_user'] = gh.get('user')["login"]
    return redirect(next_url)

# Temporary testing function to see the current auth token
@app.route('/temp')
def temp():
    return session['github_access_token']

if __name__ == '__main__':
    app.run(debug=True)
