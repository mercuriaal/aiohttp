import asyncio

import aiopg
from aiohttp import web

import config
from models import db, Advertisement

app = web.Application()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def set_connection():
    return await db.set_bind(config.POTSGRE_URI)


async def disconnect():
    return await db.pop_bind().close()


async def pg_pool(app):
    async with aiopg.create_pool(config.POTSGRE_URI) as pool:
        app['pg_pool'] = pool
        yield
        pool.close()


async def orm_engine(app):
    print('engine started')
    app['db'] = db
    await set_connection()
    await db.gino.create_all()
    yield
    await disconnect()


class AdvertisementView(web.View):

    async def get(self):
        user_id = int(self.request.match_info['user_id'])
        user = await Advertisement.get_or_404(user_id)
        return web.json_response(user.to_dict())

    async def post(self):
        data = await self.request.json()
        user = await Advertisement.create_instance(**data)
        return web.json_response(user.to_dict())

    async def patch(self):
        instance_id = int(self.request.match_info['user_id'])
        instance = await Advertisement.get_or_404(instance_id)
        data = await self.request.json()
        await instance.update(**data).apply()
        return web.json_response({'status': 'patched'})

    async def delete(self):
        instance_id = int(self.request.match_info['user_id'])
        instance = await Advertisement.get_or_404(instance_id)
        await instance.delete()
        return web.json_response({'status': 'deleted'})


class AdvertisementsView(web.View):

    async def get(self):
        pool = self.request.app['pg_pool']
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT id, title, description FROM advertisement')
                ads = await cursor.fetchall()
                return web.json_response(ads)


app.add_routes([web.get('/advertisement/get/{user_id:\d+}', AdvertisementView),
                web.post('/advertisement/', AdvertisementView),
                web.patch('/advertisement/patch/{user_id:\d+}', AdvertisementView),
                web.delete('/advertisement/delete/{user_id:\d+}', AdvertisementView),
                web.get('/advertisements', AdvertisementsView)])
app.cleanup_ctx.append(orm_engine)
app.cleanup_ctx.append(pg_pool)
web.run_app(app, port=8085)
