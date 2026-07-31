from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


class Experiment(Base):
    __tablename__ = "experiments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[float] = mapped_column(Float, nullable=False)
    recall: Mapped[float] = mapped_column(Float, nullable=False)
    f1_score: Mapped[float] = mapped_column(Float, nullable=False)
    roc_auc: Mapped[float] = mapped_column(Float, nullable=False)
    params: Mapped[str] = mapped_column(Text, nullable=True)
    model_path: Mapped[str] = mapped_column(String(255), nullable=False)
    is_best: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @classmethod
    def create(cls, db: Session, model_name: str, accuracy: float, precision: float,
               recall: float, f1: float, roc_auc: float, params: str, model_path: str,
               is_best: bool = False) -> "Experiment":
        exp = cls(
            model_name=model_name,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            roc_auc=roc_auc,
            params=params,
            model_path=model_path,
            is_best=is_best,
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)
        return exp

    @classmethod
    def paginate(cls, db: Session, page: int = 1, per_page: int = 50,
                 model_name: str = None) -> tuple[list["Experiment"], int]:
        query = db.query(cls)
        if model_name:
            query = query.filter(cls.model_name == model_name)
        total = query.count()
        items = query.order_by(cls.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    @classmethod
    def find_best(cls, db: Session) -> "Experiment":
        return db.query(cls).filter(cls.is_best == True).first()

    @classmethod
    def clear_best(cls, db: Session):
        db.query(cls).filter(cls.is_best == True).update({"is_best": False})
        db.commit()