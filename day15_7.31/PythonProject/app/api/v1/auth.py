from flask import Blueprint, request
from pydantic import ValidationError
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.core.response import json, BizException
from app.core.dependencies import login_required, role_required, get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.auth import LoginRequest, RegisterRequest, UpdateProfileRequest, UpdatePasswordRequest

bp = Blueprint("auth", __name__)

def _parse_body(model_cls):
    """公共辅助：取 JSON body → Pydantic 校验 → 返回模型实例
    逐字思路：
    1. request.get_json(silent=True) 取 body，取不到返回 None
    2. body 为 None 用空字典兜底
    3. 校验不过抛 BizException(1001)
    """
    body = request.get_json(silent=True) or {}
    try:
        return model_cls(**body)
    except ValidationError:
        raise BizException(1001, "参数校验错误，请检查请求体字段", 400)

def _token_response(user: User) -> dict:
    """拼统一的 token 响应体（登录/注册复用）"""
    return json({
        "access_token": create_access_token(user.username),
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {"id": user.id, "username": user.username, "role": user.role},
    })

@bp.route("/register", methods=["POST"])
def register():
    """注册：查重-哈希-入库-签JWT(返回token)"""
    req = _parse_body(RegisterRequest)
    db = get_db()
    user = User.find_by_username(db, req.username)
    if user:
        raise BizException(1004, "用户名已存在", 400)
    user = User.create(db, req.username, hash_password(req.password), role = "user")
    return _token_response(user)
    
@bp.route("/me", methods=["GET"])
@login_required
def me():
    """获取当前登录用户信息（需登录）"""
    user = get_current_user()
    return json({
        "id": user.id,
        "username": user.username,
        "role": user.role
    })

@bp.route("/users", methods=["GET"])
@role_required("admin")
def users():
    """获取所有用户列表（仅 admin 可访问）"""
    db = get_db()
    user_list = User.all_users(db)
    return json([{
        "id": u.id,
        "username": u.username,
        "role": u.role
    } for u in user_list])

@bp.route("/login", methods=["POST"])
def login():
    """登录：校验用户名密码 → 签发 JWT"""
    req = _parse_body(LoginRequest)
    db = get_db()
    user = User.find_by_username(db, req.username)
    if not user or not verify_password(req.password, user.password_hash):
        raise BizException(1001, "用户名或密码错误", 401)
    return _token_response(user)


@bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    req = _parse_body(UpdateProfileRequest)
    user = get_current_user()
    db = get_db()

    new_username = req.new_username.strip()
    # 检查新用户名是否已被其他用户占用
    existing = User.find_by_username(db, new_username)
    if existing and existing.id != user.id:
        raise BizException(1004, "用户名已被占用", 400)

    user.update_username(db, new_username)
    return json({
        "id": user.id,
        "username": user.username,
        "role": user.role
    })


@bp.route("/password", methods=["PUT"])
@login_required
def update_password():
    """修改当前登录用户的密码"""
    req = _parse_body(UpdatePasswordRequest)
    user = get_current_user()
    db = get_db()
    # 校验旧密码
    if not verify_password(req.old_password, user.password_hash):
        raise BizException(1001, "旧密码错误", 401)
    # 加密新密码并更新
    new_hash = hash_password(req.new_password)
    user.update_password(db, new_hash)
    return json({"message": "密码修改成功"})
