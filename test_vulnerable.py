from vulnerable import app


def test_hello_returns_expected_message():
    client = app.test_client()

    response = client.get('/hello?name=CI')

    assert response.status_code == 200
    assert b'Hello, CI!' in response.data


def test_hello_escapes_reflected_input():
    client = app.test_client()

    response = client.get('/hello?name=<script>alert(1)</script>')

    assert response.status_code == 200
    assert b'<script>alert(1)</script>' not in response.data
    assert b'&lt;script&gt;alert(1)&lt;/script&gt;' in response.data


def test_security_headers_are_present():
    client = app.test_client()

    response = client.get('/hello?name=CI')

    assert response.headers['Content-Security-Policy'] == "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert response.headers['Referrer-Policy'] == 'no-referrer'
    assert response.headers['Permissions-Policy'] == 'geolocation=(), microphone=(), camera=()'
    assert response.headers['Cache-Control'] == 'no-store'
