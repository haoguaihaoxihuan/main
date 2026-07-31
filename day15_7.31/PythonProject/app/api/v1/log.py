from flask import Blueprint, request
from app.core.response import json as api_json
from app.core.dependencies import login_required, role_required
from app.services.log_service import query_logs

bp = Blueprint("log", __name__)


@bp.route("/", methods=["GET"])
@login_required
@role_required("admin")
def logs():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    page = max(page, 1)
    per_page = max(per_page, 1)
    user_id = request.args.get("user_id", type=int)
    action = request.args.get("action", "").strip() or None
    result = query_logs(page=page, per_page=per_page, user_id=user_id, action=action)
    return api_json(result)