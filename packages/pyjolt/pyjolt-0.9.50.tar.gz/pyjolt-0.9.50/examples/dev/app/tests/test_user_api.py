"""
User API tests

Add more tests as needed
"""

async def test_get_users(client):
    res = await client.get("/api/v1/users")
    assert res.status_code == 200
