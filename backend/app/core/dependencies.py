from fastapi import Request


async def get_db_conn(request: Request):
    async with request.app.state.db_manager.get_conn() as conn:
        yield conn
