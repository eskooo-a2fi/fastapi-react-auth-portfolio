from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.database import get_db
from app.main import app


def database_down():
    raise OperationalError('SELECT internal_data', (), OSError('private connection details'))


def test_readiness_uses_a_real_database_connection(client: TestClient):
    assert client.get('/health').json() == {'status': 'ok'}
    assert client.get('/ready').json() == {'status': 'ready'}


def test_database_outage_returns_503_without_leaking_details(client: TestClient):
    previous = app.dependency_overrides[get_db]
    registered = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'strong-password-12345',
    })
    assert registered.status_code == 201
    login = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'strong-password-12345',
    })
    token = login.json()['access_token']
    app.dependency_overrides[get_db] = database_down
    try:
        responses = [
            client.get('/ready'),
            client.get('/auth/me', headers={'Authorization': f'Bearer {token}'}),
        ]
        for response in responses:
            assert response.status_code == 503
            assert response.json() == {'detail': 'Database temporarily unavailable'}
            assert response.headers['Retry-After'] == '5'
            assert 'internal_data' not in response.text
            assert 'private connection' not in response.text

        registration = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'strong-password-12345',
        })
        assert registration.status_code == 503
        assert registration.json()['detail'] == 'Database temporarily unavailable'
        assert client.get('/health').status_code == 200
    finally:
        app.dependency_overrides[get_db] = previous

    assert client.get('/ready').status_code == 200
