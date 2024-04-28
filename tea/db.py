from datetime import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, func
from sqlalchemy import String, DateTime
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

engine = create_engine('sqlite:///test.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         expire_on_commit=False,
                                         bind=engine))


class Base(MappedAsDataclass, DeclarativeBase):
    query = db_session.query_property()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def init_db():
    Base.metadata.create_all(bind=engine)


class SugarBlend(Base):
    sugar: Mapped[float]
    vanillin: Mapped[float]
    ethyl_vanillin: Mapped[float]
    # tea_servings: Mapped[List["TeaServing"]] = relationship(
    #      back_populates="sugar_blend", cascade="all, delete-orphan"
    # )

    __tablename__ = "sugar_blend"
    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=None,
    )


class TeaServing(Base):
    water: Mapped[float]
    sugar: Mapped[float]
    almond_milk: Mapped[float]
    blend: Mapped[int] = mapped_column(ForeignKey("sugar_blend.id"))
    # sugar_blend: Mapped[SugarBlend] = relationship(back_populates="tea_servings")

    quality: Mapped[float] = mapped_column(nullable=True, default=None)
    __tablename__ = "tea_serving"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=None,
    )


class TrialSuggestions(Base):
    __tablename__ = "trial_suggestion"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.utc_timestamp(), default=None
    )
