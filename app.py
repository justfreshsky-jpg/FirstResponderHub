"""
FirstResponderHub — minimal Flask app serving the static landing page.

Standalone (no freshsky_common dependency) so it stays light + isolated
from consumer-portfolio churn. The whole app is one route serving an
HTML template.
"""
import os

from flask import Flask, jsonify, render_template

app = Flask(__name__)


@app.after_request
def _security_headers(resp):
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    resp.headers.setdefault('X-Frame-Options', 'DENY')
    resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    resp.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    return resp


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify(status='ok')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
