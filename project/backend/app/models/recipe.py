from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from datetime import datetime
from app.core.database import Base


class RecipeModel(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, unique=True, nullable=False, index=True)
    recipe_name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    step_count = Column(Integer, nullable=False)
    total_time = Column(Integer, nullable=False)
    enable = Column(Boolean, default=True)

    steps_data = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
