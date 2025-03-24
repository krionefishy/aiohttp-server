from dataclasses import dataclass, field

from app.quiz.models import Theme
from app.admin.models import Admin
from app.quiz.models import Question
import uuid
from datetime import datetime, timedelta

@dataclass 
class Cookie:
    session_id: str
    admin_id: int
    expires_at: datetime


@dataclass
class Database:
    # TODO: добавить поля admins и questions 
    questions: list[Question] = field(default_factory=list)
    admins: list[Admin] = field(default_factory=list)
    themes: list[Theme] = field(default_factory=list)

    @property
    def next_question_id(self) -> int:
        return len(self.questions) + 1

    @property
    def next_admin_id(self) -> int:
        return len(self.admins) + 1

    @property
    def next_theme_id(self) -> int:
        return len(self.themes) + 1

    def clear(self):
        self.themes.clear()
        self.questions.clear()
        self.admins.clear() 

class CookieStorage:
    def __init__(self):
        self.sessions: list[Cookie] = []
    
    async def create_session(self, adminId: int, session_id: str):
        cookie = Cookie(
            session_id=session_id,
            admin_id=adminId,
            expires_at=datetime.now() + timedelta(days=1)
        )
        self.sessions.append(cookie)
        

    async def is_valid_cookie(self, session_id: str) -> bool:
        for s in self.sessions:
            if s.sessionId == session_id:
                if datetime.now() < s.expires_at:
                    return True
                return False
        return False 
    

    async def list_cookies_debug(self) -> list[Cookie]:
        return self.sessions
    