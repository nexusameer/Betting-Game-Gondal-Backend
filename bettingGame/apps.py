from django.apps import AppConfig
import asyncio

class BettinggameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bettingGame'

    def ready(self):
        # Run the event loop in a separate thread
        from threading import Thread
        loop = asyncio.new_event_loop()
        Thread(target=self.start_async_loop, args=(loop,), daemon=True).start()

    def start_async_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_event_loop())
        loop.close()

    async def run_event_loop(self):
        from .consumer import GameConsumer
        await GameConsumer.session_management()