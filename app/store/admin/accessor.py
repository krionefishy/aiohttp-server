import typing 
if typing.TYPE_CHECKING:
    from app.web.app import Application

import bcrypt
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from aiohttp.web_exceptions import HTTPConflict
from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor
from app.admin.models import Admin

class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        admin_from_config = app.config.admin
        
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(
            admin_from_config.password.encode("utf-8"), salt
        ).decode("utf-8")
        
        async with self.app.database.session() as session:
            try:
                stmt = insert(AdminModel).values(
                    email=admin_from_config.email,
                    password=hashed_password
                )
                stmt = stmt.on_conflict_do_nothing(index_elements=['email'])
                
                await session.execute(stmt)
                await session.commit()
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error creating admin: {e}")
                raise

    async def get_by_email(self, email: str) -> Admin | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(AdminModel).where(AdminModel.email == email)
            )
            admin = result.scalar_one_or_none()
            if admin:
                return Admin(
                    id=admin.id,
                    email=admin.email,
                    password=admin.password
                )
            return None

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session() as session:
            try:
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(
                    password.encode("utf-8"), salt
                ).decode("utf-8")
                
                result = await session.execute(
                    insert(AdminModel)
                    .values(email=email, password=hashed_password)
                    .returning(AdminModel)
                )
                await session.commit()
                admin = result.scalar_one()
                return Admin(
                    id=admin.id,
                    email=admin.email,
                    password=admin.password
                )
            except IntegrityError:
                await session.rollback()
                raise HTTPConflict(reason="admin already exists")
            
    async def get_by_id(self, id: int) -> Admin | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(AdminModel).where(AdminModel.id == id)
            )
            admin = result.scalar_one_or_none()
            if admin:
                return Admin(
                    id=admin.id,
                    email=admin.email,
                    password=admin.password
                )
            return None