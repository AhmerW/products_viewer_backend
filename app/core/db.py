from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.models.field_model import *
from app.models.user_model import *
from app.models.product_model import *
from app.models.models import *
from app.models.category_model import *
from app.models.default_model import *

from app.services.user_service import create_user

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    from sqlmodel import SQLModel, delete

    print("initiating db")
    

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.username == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            username=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            roles=[UserRoles.admin, UserRoles.editor, UserRoles.viewer],
        )
        user = create_user(session=session, user_create=user_in)


