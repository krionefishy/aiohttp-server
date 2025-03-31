import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application




class Store:
    def __init__(self, app: "Application"):
        self.app = app
        from app.store.vk_api.accessor import VkApiAccessor
        from app.store.admin.accessor import AdminAccessor
        from app.store.quiz.accessor import QuizAccessor
        from app.store.bot.manager import BotManager
        self.admins = AdminAccessor(app)
        self.quizzes = QuizAccessor(app)
        self.bots_manager = BotManager(app)
        self.vk_api = VkApiAccessor(app) 


        
    async def connect(self):
        await self.vk_api.connect(self.app)  
        await self.admins.connect()
    
    async def disconnect(self):
        await self.vk_api.disconnect(self.app)  
        await self.admins.disconnect()


    
def setup_store(app: "Application") -> None:
    app.store = Store(app)
