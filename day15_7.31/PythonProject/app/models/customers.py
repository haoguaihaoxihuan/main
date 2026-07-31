from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    region_code: Mapped[str] = mapped_column(String(50), nullable=False)
    policy_sales_channel: Mapped[str] = mapped_column(String(50), nullable=False)
    previously_insured: Mapped[int] = mapped_column(Integer, nullable=False)
    annual_premium: Mapped[float] = mapped_column(Float, nullable=False)
    vintage: Mapped[int] = mapped_column(Integer, nullable=False)
    vehicle_age: Mapped[str] = mapped_column(String(50), nullable=False)
    vehicle_damage: Mapped[str] = mapped_column(String(10), nullable=False)
    driving_license: Mapped[int] = mapped_column(Integer, nullable=False)
    response: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_prob: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uploaded_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @classmethod
    def bulk_create(cls, db: Session, rows: list[dict], user_id: int) -> int:
        customers = []
        for row in rows:
            customer = cls(
                id=row["id"],
                gender=row["gender"],
                age=row["age"],
                region_code=row["region_code"],
                policy_sales_channel=row["policy_sales_channel"],
                previously_insured=row["previously_insured"],
                annual_premium=row["annual_premium"],
                vintage=row["vintage"],
                vehicle_age=row["vehicle_age"],
                vehicle_damage=row["vehicle_damage"],
                driving_license=row["driving_license"],
                response=row["response"],
                uploaded_by=user_id,
            )
            customers.append(customer)
        db.add_all(customers)
        db.commit()
        return len(customers)

    @classmethod
    def paginate(cls, db: Session, page: int = 1, per_page: int = 50, filters: dict = None) -> tuple[list["Customer"], int]:
        query = db.query(cls)
        if filters:
            if filters.get("gender"):
                query = query.filter(cls.gender == filters["gender"])
            if filters.get("age_min") is not None:
                query = query.filter(cls.age >= filters["age_min"])
            if filters.get("age_max") is not None:
                query = query.filter(cls.age <= filters["age_max"])
            if filters.get("previously_insured") is not None:
                query = query.filter(cls.previously_insured == filters["previously_insured"])
            if filters.get("keyword"):
                query = query.filter(cls.id == filters["keyword"])
        total = query.count()
        items = query.order_by(cls.id).offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    @classmethod
    def count(cls, db: Session) -> int:
        return db.query(cls).count()

    @classmethod
    def find_high_potential(cls, db: Session, top_percent: float = 0.1) -> list["Customer"]:
        probs = [p for (p,) in db.query(cls.predicted_prob).filter(cls.predicted_prob.isnot(None)).all()]
        if not probs:
            return []
        probs.sort()
        threshold_idx = int(len(probs) * (1 - top_percent))
        if threshold_idx >= len(probs):
            threshold_idx = len(probs) - 1
        threshold = probs[threshold_idx]
        return db.query(cls).filter(cls.predicted_prob >= threshold).order_by(cls.predicted_prob.desc()).all()