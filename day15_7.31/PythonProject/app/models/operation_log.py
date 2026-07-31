from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @classmethod
    def create(cls, db: Session, user_id: int, action: str, details: str = None) -> "OperationLog":
        log = cls(user_id=user_id, action=action, details=details)
        db.add(log)
        db.commit()
        return log

    @classmethod
    def paginate(cls, db: Session, page: int = 1, per_page: int = 50,
                 user_id: int = None, action: str = None) -> tuple[list["OperationLog"], int]:
        query = db.query(cls)
        if user_id:
            query = query.filter(cls.user_id == user_id)
        if action:
            query = query.filter(cls.action == action)
        total = query.count()
        items = query.order_by(cls.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return items, total