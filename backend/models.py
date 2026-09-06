from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Architecture(Base):
    __tablename__ = "architectures"

    id = Column(Integer, primary_key=True, index=True)
    family_name = Column(String, nullable=False)
    architecture = Column(String, nullable=False)
    generation_series = Column(String, nullable=False)

    gpus = relationship("Gpu", back_populates="arch_info")

class Gpu(Base):
    __tablename__ = "gpus"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    vram_gb = Column(Integer, nullable=False)
    memory_type = Column(String, nullable=True)
    bus_width_bits = Column(Integer, nullable=True)
    architecture_id = Column(Integer, ForeignKey("architectures.id"), nullable=True)

    # Категории использования (Use Cases)
    for_games = Column(Boolean, default=True)
    for_3d = Column(Boolean, default=False)
    for_ml = Column(Boolean, default=False)
    for_office = Column(Boolean, default=True)

    # Типаж бюджета: 'budget', 'mid', 'flagship'
    budget_tier = Column(String, default="mid")

    arch_info = relationship("Architecture", back_populates="gpus")