from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


class EmailRecord(Base):
    __tablename__ = "email_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="generated")
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @classmethod
    def bulk_create(cls, db: Session, records: list[dict]) -> int:
        objs = [cls(**r) for r in records]
        db.add_all(objs)
        db.commit()
        return len(objs)

    @classmethod
    def paginate(cls, db: Session, page: int = 1, per_page: int = 50,
                 status: str = None, user_id: int = None) -> tuple[list["EmailRecord"], int]:
        query = db.query(cls)
        if status:
            query = query.filter(cls.status == status)
        if user_id:
            query = query.filter(cls.created_by == user_id)
        total = query.count()
        items = query.order_by(cls.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    @classmethod
    def find_by_id(cls, db: Session, record_id: int) -> Optional["EmailRecord"]:
        return db.query(cls).filter(cls.id == record_id).first()

    @classmethod
    def delete_by_ids(cls, db: Session, record_ids: list[int]) -> int:
        count = db.query(cls).filter(cls.id.in_(record_ids)).delete(synchronize_session=False)
        db.commit()
        return count