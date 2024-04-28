from __future__ import annotations

from datetime import datetime
from math import dist, sqrt
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
from sqlalchemy.schema import UniqueConstraint

import tea.math
import numpy as np

engine = create_engine('sqlite:///test.db', echo=False)
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
    __tablename__ = "sugar_blend"
    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=None,
    )

    @property
    def gross_weight(self):
        return sum(self.point_array)

    @property
    def point_array(self):
        return np.array([self.sugar, self.vanillin, self.ethyl_vanillin])

    def scaled_composition(self, weight):
        data_fields = dict(sugar=self.sugar, vanillin=self.vanillin, ethyl_vanillin=self.ethyl_vanillin)
        scaled_blend = tea.math.scale_to_target_weight(data_fields, weight)
        return SugarBlend(**scaled_blend)
    
    def nearest_blend(self, other: SugarBlend):
        point = tea.math.find_closest_point_on_line(np.array([0,0,0]), self.point_array, other.point_array)
        return SugarBlend(
            sugar=point[0],
            vanillin=point[1],
            ethyl_vanillin=point[2],
        )
    
    def __sub__(self, other) -> float:
        if isinstance(other, SugarBlend):
            return dist(self.point_array, other.point_array)
        
        return super().__sub__(other)


class TeaServing(Base):
    water: Mapped[float]
    sugar: Mapped[float]
    almond_milk: Mapped[float]
    blend: Mapped[int] = mapped_column(ForeignKey("sugar_blend.id"))
    quality: Mapped[float] = mapped_column(nullable=True, default=None)
    __tablename__ = "tea_serving"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=None,
    )


class TrialSuggestion(Base):
    water: Mapped[float]
    sugar: Mapped[float]
    almond_milk: Mapped[float]
    blend: Mapped[int] = mapped_column(ForeignKey("sugar_blend.id"))
    __tablename__ = "trial_suggestion"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=None,
    )
    __table_args__ = (UniqueConstraint("water", "sugar", "almond_milk", "blend", name="mixture_idx"), )
