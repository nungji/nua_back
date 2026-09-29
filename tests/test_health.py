from httpx import ASGITransport, AsyncClient

from nua.app import create_app
from nua.db.session import create_engine


async def test_health_returns_ok():
    app = create_app(
        engine=create_engine('postgresql+asyncpg://nua:nua@localhost:5432/nua'),
        cors_origins=['*']
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response = await client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
