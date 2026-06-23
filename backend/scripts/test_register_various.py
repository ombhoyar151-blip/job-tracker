import asyncio
import httpx

async def try_password(pw):
    async with httpx.AsyncClient() as ac:
        r = await ac.post('http://127.0.0.1:8000/api/auth/register', json={
            'name': 'Tester',
            'email': f'tester_{len(pw)}@example.com',
            'password': pw
        })
        print(f'pw_len={len(pw)} status={r.status_code} body={r.text[:200]}')

async def main():
    for pw in ['short', '', 'x'*50, 'x'*73]:
        await try_password(pw)

if __name__ == '__main__':
    asyncio.run(main())
