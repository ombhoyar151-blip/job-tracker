import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as ac:
        reg = await ac.post('http://localhost:8000/api/auth/register', json={
            'name': 'Local Tester',
            'email': 'localtester@example.com',
            'password': 'Secret123!'
        })
        print('register:', reg.status_code, reg.text)
        login = await ac.post('http://localhost:8000/api/auth/login', json={'email': 'localtester@example.com', 'password': 'Secret123!'})
        print('login:', login.status_code, login.text)

if __name__ == '__main__':
    asyncio.run(main())
