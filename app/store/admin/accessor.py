import typing
import bcrypt
from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor
from aiohttp.web_exceptions import HTTPConflict

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        # TODO: создать админа по данным в config.yml здесь

        admin_from_config = app.config.admin

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(admin_from_config.password.encode("utf-8"), salt)

        admin = Admin(id=self.app.database.next_admin_id , 
                      email=admin_from_config.email, 
                      password=hashed_password.decode("utf-8"))
        

        self.app.database.admins.append(admin)



    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None



    async def create_admin(self, email: str, password: str) -> Admin:
        exists = await self.get_by_email(email)
        if exists:
            raise HTTPConflict(reason="admin already exists")
        
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

        admin = Admin(
            id=self.app.database.next_admin_id,
            email=email,
            password=str(hashed_password)
        )
        
        self.app.database.admins.append(admin)

        return admin
