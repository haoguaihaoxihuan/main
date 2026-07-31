from app.core.database import SessionLocal
from app.models.operation_log import OperationLog


def query_logs(page: int = 1, per_page: int = 50, user_id: int = None, action: str = None) -> dict:
    db = SessionLocal()
    try:
        items, total = OperationLog.paginate(db, page=page, per_page=per_page, user_id=user_id, action=action)
        return {
            "items": [{
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            } for log in items],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if per_page else 0,
        }
    finally:
        db.close()