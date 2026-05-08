"""
FirstResponderHub — Flask app serving the landing page + roadmap MVPs.

Standalone (no freshsky_common dependency). Landing page is templated;
the roadmap items (training tracker, pre-incident plan, SOG search,
apparatus check, recruitment funnel) live at /tools/<slug> using a
shared form template + LLM fallback chain (US/EU providers only).
"""
import os
import logging

import requests
from flask import Response, Flask, jsonify, render_template, request

from tools_data import TOOLS, get_tool, all_slugs

app = Flask(__name__)

logger = logging.getLogger(__name__)
_HTTP_TIMEOUT = 35


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
    extras = ''.join(
        f'  <url><loc>https://firstresponder.freshskyai.com/tools/{s}</loc>'
        f'<changefreq>monthly</changefreq><priority>0.7</priority></url>\n'
        for s in all_slugs()
    )
    return Response(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url><loc>https://firstresponder.freshskyai.com/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
        '  <url><loc>https://firstresponder.freshskyai.com/tools</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>\n'
        + extras +
        '</urlset>\n',
        mimetype='application/xml',
    )


@app.route('/privacy')
def _privacy():
    return Response(_PRIVACY_HTML, mimetype='text/html')


@app.route('/terms')
def _terms():
    return Response(_TERMS_HTML, mimetype='text/html')


# ─── LLM fallback chain (US/EU providers only) ──────────────────────────

def _llm_groq(system, user):
    key = os.environ.get('GROQ_KEY', '')
    if not key:
        return None
    r = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={'Authorization': f'Bearer {key}'},
        json={'model': os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile'),
              'messages': [{'role': 'system', 'content': system},
                           {'role': 'user', 'content': user}],
              'temperature': 0.3},
        timeout=_HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']


def _llm_cerebras(system, user):
    key = os.environ.get('CEREBRAS_KEY', '')
    if not key:
        return None
    r = requests.post(
        'https://api.cerebras.ai/v1/chat/completions',
        headers={'Authorization': f'Bearer {key}'},
        json={'model': os.environ.get('CEREBRAS_MODEL', 'llama-3.3-70b'),
              'messages': [{'role': 'system', 'content': system},
                           {'role': 'user', 'content': user}],
              'temperature': 0.3},
        timeout=_HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']


def _llm_gemini(system, user):
    key = os.environ.get('GEMINI_KEY', '')
    if not key:
        return None
    r = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/'
        f'gemini-2.5-flash:generateContent?key={key}',
        headers={'Content-Type': 'application/json'},
        json={'system_instruction': {'parts': [{'text': system}]},
              'contents': [{'role': 'user', 'parts': [{'text': user}]}],
              'generationConfig': {'temperature': 0.3}},
        timeout=_HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()['candidates'][0]['content']['parts'][0]['text']


def _llm_mistral(system, user):
    key = os.environ.get('MISTRAL_KEY', '')
    if not key:
        return None
    r = requests.post(
        'https://api.mistral.ai/v1/chat/completions',
        headers={'Authorization': f'Bearer {key}'},
        json={'model': os.environ.get('MISTRAL_MODEL', 'mistral-small-latest'),
              'messages': [{'role': 'system', 'content': system},
                           {'role': 'user', 'content': user}],
              'temperature': 0.3},
        timeout=_HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']


_PROVIDERS = [
    ('groq', _llm_groq),
    ('cerebras', _llm_cerebras),
    ('gemini', _llm_gemini),
    ('mistral', _llm_mistral),
]


def _llm(system: str, user: str) -> str:
    last_err = None
    for name, fn in _PROVIDERS:
        try:
            out = fn(system, user)
            if out:
                return out.strip()
        except Exception as e:
            last_err = e
            logger.warning('Provider %s failed: %s', name, e)
    raise RuntimeError(f'All providers failed: {last_err}')


# ─── /tools index + per-tool routes ─────────────────────────────────────

@app.route('/tools')
def _tools_index():
    return render_template('tools_index.html', slugs=all_slugs(), tools=TOOLS)


@app.route('/tools/<slug>', methods=['GET', 'POST'])
def _tools_run(slug):
    tool = get_tool(slug)
    if not tool:
        return Response('Tool not found', status=404, mimetype='text/plain')

    result = None
    error = None
    submitted = {}
    if request.method == 'POST':
        # Collect form data (only declared fields)
        for field_key, _label, _kind in tool['fields']:
            submitted[field_key] = (request.form.get(field_key) or '').strip()[:4000]
        # Reject empty submissions to save LLM call
        if not any(v for v in submitted.values()):
            error = 'Please fill in at least one field.'
        else:
            user_msg = '\n\n'.join(f'{k}:\n{v}' for k, v in submitted.items() if v)
            try:
                result = _llm(tool['system_prompt'], user_msg)
            except Exception as e:
                logger.exception('LLM error for %s', slug)
                error = ('All AI providers are currently unreachable. '
                         f'Please try again in a minute. ({type(e).__name__})')

    return render_template(
        'tools_run.html',
        slug=slug, tool=tool, submitted=submitted,
        result=result, error=error,
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
