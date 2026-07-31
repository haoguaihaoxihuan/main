from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="default")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def get_active(cls, db: Session) -> Optional["PromptTemplate"]:
        return db.query(cls).filter(cls.is_active == True).first()

    @classmethod
    def update_content(cls, db: Session, content: str) -> "PromptTemplate":
        tpl = db.query(cls).filter(cls.is_active == True).first()
        if not tpl:
            tpl = cls(name="default", content=content, is_active=True)
            db.add(tpl)
        else:
            tpl.content = content
        db.commit()
        db.refresh(tpl)
        return tpl