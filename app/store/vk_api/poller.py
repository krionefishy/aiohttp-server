import asyncio
from asyncio import Task
from app.store import Store


class Poller:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.is_running = False
        self.poll_task: Task | None = None

    async def start(self) -> None:
        # TODO: добавить asyncio Task на запуск poll
        """А ниче тот факт, что на Go это было бы проще сделать. Советую присмотреться, язык то неплохой"""
        self.is_running = True
    
        if not self.poll_task:
            return
        
        try:
            await asyncio.wait_for(self.poll_task, timeout=5.0)  
        except asyncio.TimeoutError:
            self.logger.warning("server stopped before end of task, timeouterror")
            self.poll_task.cancel()
            try:
                await self.poll_task  
            except asyncio.CancelledError:
                pass
        except Exception as e:
            self.logger.error(f"Error during poller graceful shutdown: {e}")
        finally:
            self.poll_task = None

    async def stop(self) -> None:
        self.is_running = False
        self.poll_task.cancel()

    async def poll(self) -> None:
            while self.is_running:
                try:
                    await self.store.vk_api.poll()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.store.vk_api.logger.error(f"Poll loop error: {e}")
                    await asyncio.sleep(1) 
