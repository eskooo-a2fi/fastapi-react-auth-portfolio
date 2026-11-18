VALID = {'email': ' Person@Example.com ', 'password': 'correct-horse-battery-staple'}


def test_registration_login_and_me(client):
    registration = client.post('/auth/register', json=VALID)
    assert registration.status_code == 201
    assert registration.json() == {'id': 1, 'email': 'person@example.com', 'is_active': True}
    assert 'hashed_password' not in registration.text
    assert client.post('/auth/register', json=VALID).status_code == 409

    login = client.post('/auth/login', json={'email': 'PERSON@example.com', 'password': VALID['password']})
    assert login.status_code == 200
    assert login.json()['token_type'] == 'bearer'
    token = login.json()['access_token']
    response = client.get('/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json()['email'] == 'person@example.com'


def test_invalid_inputs_and_bad_credentials(client):
    assert client.post('/auth/register', json={'email': 'not-email', 'password': 'x'}).status_code == 422
    assert client.post('/auth/register', json=VALID).status_code == 201
    assert client.post('/auth/login', json={'email': 'person@example.com', 'password': 'wrong'}).status_code == 401
    assert client.get('/auth/me').status_code == 401
    assert client.get('/auth/me', headers={'Authorization': 'Bearer bad.token.value'}).status_code == 401


def test_form_token_endpoint(client):
    client.post('/auth/register', json=VALID)
    token = client.post('/auth/token', data={'username': 'person@example.com', 'password': VALID['password']})
    assert token.status_code == 200
    assert token.json()['access_token']
