from datetime import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, func
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

engine = create_engine('sqlite:///test.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class Base(MappedAsDataclass, DeclarativeBase):
    query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)

class SugarBlend(Base):
    __tablename__ = "sugar_blend"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.utc_timestamp(), default=None
    )

class TeaServing(Base):
    __tablename__ = "tea_serving"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.utc_timestamp(), default=None
    )

class TrialSuggestions(Base):
    __tablename__ = "trial_suggestion"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.utc_timestamp(), default=None
    )

