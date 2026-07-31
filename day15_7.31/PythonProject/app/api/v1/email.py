from flask import Blueprint, request
from app.core.database import get_db
from app.core.response import json as api_json, BizException
from app.core.dependencies import login_required, get_current_user
from app.models.email_record import EmailRecord
from app.services.email_service import get_targets, generate_emails, get_prompt, update_prompt

bp = Blueprint("email", __name__)


@bp.route("/targets", methods=["GET"])
@login_required
def targets():
    percentile = request.args.get("percentile", 0.9, type=float)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    db = get_db()
    result = get_targets(db, percentile=percentile, page=page, per_page=per_page)
    return api_json(result)


@bp.route("/generate", methods=["POST"])
@login_required
def generate():
    body = request.get_json(silent=True) or {}
    customer_ids = body.get("customer_ids")
    limit = body.get("limit", 5)
    user = get_current_user()
    db = get_db()
    result = generate_emails(db, user.id, customer_ids=customer_ids, limit=limit)
    return api_json(result)


@bp.route("/prompt", methods=["GET"])
@login_required
def prompt_get():
    db = get_db()
    result = get_prompt(db)
    return api_json(result)


@bp.route("/prompt", methods=["PUT"])
@login_required
def prompt_put():
    body = request.get_json(silent=True) or {}
    content = body.get("content", "")
    if not content:
        raise BizException(1001, "prompt内容不能为空", 400)
    db = get_db()
    result = update_prompt(db, content)
    return api_json(result)


@bp.route("/records", methods=["GET"])
@login_required
def records():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    page = max(page, 1)
    per_page = max(per_page, 1)
    status = request.args.get("status", "").strip() or None
    user_id = request.args.get("user_id", type=int)
    db = get_db()
    items, total = EmailRecord.paginate(db, page=page, per_page=per_page, status=status, user_id=user_id)
    return api_json({
        "items": [{
            "id": r.id, "customer_id": r.customer_id,
            "subject": r.subject, "content": r.content,
            "status": r.status, "created_by": r.created_by,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in items],
        "total": total, "page": page, "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page else 0,
    })


@bp.route("/records/<int:record_id>", methods=["GET"])
@login_required
def record_detail(record_id):
    db = get_db()
    r = EmailRecord.find_by_id(db, record_id)
    if not r:
        raise BizException(2001, "邮件记录不存在", 404)
    return api_json({
        "id": r.id, "customer_id": r.customer_id,
        "subject": r.subject, "content": r.content,
        "status": r.status, "created_by": r.created_by,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    })


@bp.route("/records/<int:record_id>", methods=["PUT"])
@login_required
def record_update(record_id):
    db = get_db()
    r = EmailRecord.find_by_id(db, record_id)
    if not r:
        raise BizException(2001, "邮件记录不存在", 404)
    body = request.get_json(silent=True) or {}
    if "subject" in body:
        r.subject = body["subject"]
    if "content" in body:
        r.content = body["content"]
    db.commit()
    return api_json({"id": r.id, "subject": r.subject, "status": r.status})


@bp.route("/records/<int:record_id>", methods=["PATCH"])
@login_required
def record_status(record_id):
    db = get_db()
    r = EmailRecord.find_by_id(db, record_id)
    if not r:
        raise BizException(2001, "邮件记录不存在", 404)
    body = request.get_json(silent=True) or {}
    status = body.get("status", "").strip()
    if status not in ("generated", "sent", "failed"):
        raise BizException(1001, "状态值无效，可选: generated/sent/failed", 400)
    r.status = status
    db.commit()
    return api_json({"id": r.id, "status": r.status})


@bp.route("/records/<int:record_id>", methods=["DELETE"])
@login_required
def record_delete(record_id):
    db = get_db()
    r = EmailRecord.find_by_id(db, record_id)
    if not r:
        raise BizException(2001, "邮件记录不存在", 404)
    db.delete(r)
    db.commit()
    return api_json({"deleted": record_id})


@bp.route("/records/batch_delete", methods=["POST"])
@login_required
def records_batch_delete():
    body = request.get_json(silent=True) or {}
    ids = body.get("ids", [])
    if not ids or not isinstance(ids, list):
        raise BizException(1001, "ids参数必须是非空数组", 400)
    deleted = EmailRecord.delete_by_ids(get_db(), ids)
    return api_json({"deleted_count": deleted})