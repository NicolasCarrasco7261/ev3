from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/hello')
def hello():
    name = escape(request.args.get('name', 'World'))
    return f'Hello, {name}!'

if __name__ == '__main__':
    app.run(debug=False)
