"""
FirstResponderHub — minimal Flask app serving the static landing page.

Standalone (no freshsky_common dependency) so it stays light + isolated
from consumer-portfolio churn. The whole app is one route serving an
HTML template.
"""
import os

from flask import Response, Flask, jsonify, render_template

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


_PRIVACY_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Privacy — Fresh Sky AI for First Responders</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font-family:system-ui,sans-serif;max-width:760px;margin:40px auto;padding:0 20px;line-height:1.6;color:#0f172a}h1{margin-bottom:.5em}h2{margin-top:1.5em;font-size:1.1rem}a{color:#1e3a8a}</style>
</head><body>
<a href="/">← Back to Fresh Sky AI for First Responders</a>
<h1>Privacy Policy — Fresh Sky AI for First Responders</h1>
<p><em>Last updated 2026-05-07</em></p>
<h2>What we collect</h2>
<p>Fresh Sky AI for First Responders is a stateless tool. We do <strong>not</strong> require accounts. We do <strong>not</strong> store the text or voice input you submit. We do <strong>not</strong> upload member rosters, patient data, or any personally identifying information.</p>
<h2>What we send to AI providers</h2>
<p>The text or voice transcript you submit is sent to one of several US/EU-jurisdiction LLM providers (Groq, Cerebras, Mistral, HuggingFace via Together, Sambanova, Cloudflare Workers AI, or Google Gemini) for processing. None of these providers train on inputs from our paid-tier API calls (Gemini's free tier may; we do not pass PII).</p>
<h2>What gets logged</h2>
<p>Standard request metadata (IP address, timestamp, response code) is logged by Google Cloud Run for operational purposes (debugging, abuse prevention) and rotated automatically per Google retention defaults. We do not associate logs with individual users.</p>
<h2>Cookies</h2>
<p>A Flask session cookie is set to remember ephemeral state during your visit. It expires when you close the browser. No third-party tracking, no advertising cookies.</p>
<h2>Children</h2>
<p>Some of our tools (e.g. CAPStudy) are designed to be used by minors aged 12+. We do not collect any personally identifying information from anyone, including minors. Parents/guardians of cadets aged 12-17 may use the tool freely.</p>
<h2>Contact</h2>
<p>Questions: <a href="mailto:admin@freshskyllc.com">admin@freshskyllc.com</a>. Operator: Fresh Sky LLC, Somerset County, NJ.</p>
</body></html>"""

_TERMS_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Terms of Use — Fresh Sky AI for First Responders</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font-family:system-ui,sans-serif;max-width:760px;margin:40px auto;padding:0 20px;line-height:1.6;color:#0f172a}h1{margin-bottom:.5em}h2{margin-top:1.5em;font-size:1.1rem}a{color:#1e3a8a}</style>
</head><body>
<a href="/">← Back to Fresh Sky AI for First Responders</a>
<h1>Terms of Use — Fresh Sky AI for First Responders</h1>
<p><em>Last updated 2026-05-07</em></p>
<h2>What this is</h2>
<p>Fresh Sky AI for First Responders is a free volunteer-built tool offered by Fresh Sky LLC for use by U.S. fire departments, EMS, and police. No charge. No contract. No license required.</p>
<h2>What this is not</h2>
<p>Fresh Sky AI for First Responders is <strong>not</strong> affiliated with any government agency, military service, or official entity. Output is AI-generated and intended as a draft or study aid only — the human user is responsible for verifying accuracy against authoritative current sources before acting on or filing anything.</p>
<h2>Use at your own discretion</h2>
<p>You agree to use the tool in good faith. Do not submit personally identifying information (PII) about third parties, patient health information (PHI), or classified/sensitive operational details. The tool is not designed to handle such data and we do not warrant against any misuse.</p>
<h2>No warranty</h2>
<p>The tool is provided "as is" without warranty of any kind. Fresh Sky LLC disclaims all liability for damages arising from use or misuse of the output.</p>
<h2>Changes</h2>
<p>We may update or discontinue the tool without notice. If a tool is retired, this URL will redirect or be retired in tandem.</p>
<h2>Contact</h2>
<p>Questions: <a href="mailto:admin@freshskyllc.com">admin@freshskyllc.com</a>.</p>
</body></html>"""


@app.route('/robots.txt')
def _robots():
    return Response(
        "User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /metrics\nDisallow: /health\n"
        "Sitemap: https://firstresponder.freshskyai.com/sitemap.xml\n",
        mimetype='text/plain',
    )


@app.route('/sitemap.xml')
def _sitemap():
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url><loc>https://firstresponder.freshskyai.com/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
        '</urlset>\n',
        mimetype='application/xml',
    )


@app.route('/privacy')
def _privacy():
    return Response(_PRIVACY_HTML, mimetype='text/html')


@app.route('/terms')
def _terms():
    return Response(_TERMS_HTML, mimetype='text/html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
