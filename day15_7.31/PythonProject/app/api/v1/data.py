from io import BytesIO
from flask import Blueprint, request, send_file
from openpyxl import Workbook
from sqlalchemy import func as sa_func
from app.core.database import get_db
from app.core.response import json, BizException
from app.core.dependencies import login_required, get_current_user
from app.models.customers import Customer
from app.utils.data_processor import parse_excel
from app.utils.visualizer import EDA_CHART_FUNCS

bp = Blueprint("data", __name__)


def _build_filters():
    filters = {}
    gender = request.args.get("gender", "").strip()
    if gender:
        filters["gender"] = gender
    age_min = request.args.get("age_min", "").strip()
    if age_min:
        filters["age_min"] = int(age_min)
    age_max = request.args.get("age_max", "").strip()
    if age_max:
        filters["age_max"] = int(age_max)
    previously_insured = request.args.get("previously_insured", "").strip()
    if previously_insured:
        filters["previously_insured"] = int(previously_insured)
    keyword = request.args.get("keyword", "").strip()
    if keyword:
        filters["keyword"] = keyword
    return filters


@bp.route("/upload", methods=["POST"])
@login_required
def upload():
    if "file" not in request.files:
        raise BizException(1001, "请上传文件", 400)

    file = request.files["file"]
    if not file.filename:
        raise BizException(1001, "请选择文件", 400)

    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise BizException(2002, "仅支持.xlsx/.xls格式", 400)

    file_data = file.read()
    if len(file_data) > 10 * 1024 * 1024:
        raise BizException(1001, "文件大小不能超过10MB", 400)

    valid_rows, quality_report, errors = parse_excel(BytesIO(file_data))
    if not valid_rows:
        raise BizException(2002, "Excel中没有有效数据行", 400)

    db = get_db()
    user = get_current_user()

    db.query(Customer).delete()
    Customer.bulk_create(db, valid_rows, user.id)

    return json({
        "imported_count": len(valid_rows),
        "quality_report": quality_report,
        "errors": errors,
    })


@bp.route("/customers", methods=["GET"])
@login_required
def customers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    page = max(page, 1)
    per_page = max(per_page, 1)

    filters = _build_filters()
    db = get_db()
    items, total = Customer.paginate(db, page=page, per_page=per_page, filters=filters)

    return json({
        "items": [{
            "id": c.id,
            "gender": c.gender,
            "age": c.age,
            "region_code": c.region_code,
            "policy_sales_channel": c.policy_sales_channel,
            "previously_insured": c.previously_insured,
            "annual_premium": c.annual_premium,
            "vintage": c.vintage,
            "vehicle_age": c.vehicle_age,
            "vehicle_damage": c.vehicle_damage,
            "driving_license": c.driving_license,
            "response": c.response,
            "predicted_prob": c.predicted_prob,
            "uploaded_by": c.uploaded_by,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        } for c in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page else 0,
    })


@bp.route("/export", methods=["GET"])
@login_required
def export():
    filters = _build_filters()
    db = get_db()
    items, _ = Customer.paginate(db, page=1, per_page=999999, filters=filters)

    wb = Workbook()
    ws = wb.active
    ws.title = "customers"
    headers = [
        "id", "gender", "age", "region_code", "policy_sales_channel",
        "previously_insured", "annual_premium", "vintage", "vehicle_age",
        "vehicle_damage", "driving_license", "response", "predicted_prob",
        "uploaded_by", "created_at"
    ]
    ws.append(headers)
    for c in items:
        ws.append([
            c.id, c.gender, c.age, c.region_code, c.policy_sales_channel,
            c.previously_insured, c.annual_premium, c.vintage, c.vehicle_age,
            c.vehicle_damage, c.driving_license, c.response,
            c.predicted_prob, c.uploaded_by,
            c.created_at.isoformat() if c.created_at else None,
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="customers_export.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    db = get_db()
    total = Customer.count(db)
    response_0 = db.query(Customer).filter(Customer.response == 0).count()
    response_1 = db.query(Customer).filter(Customer.response == 1).count()
    male_count = db.query(Customer).filter(Customer.gender == "Male").count()
    female_count = db.query(Customer).filter(Customer.gender == "Female").count()
    age_stats = db.query(
        sa_func.min(Customer.age),
        sa_func.max(Customer.age),
        sa_func.avg(Customer.age)
    ).first()

    return json({
        "total": total,
        "response_distribution": {"0": response_0, "1": response_1},
        "gender_distribution": {"Male": male_count, "Female": female_count},
        "age_stats": {
            "min": age_stats[0] if age_stats[0] is not None else 0,
            "max": age_stats[1] if age_stats[1] is not None else 0,
            "avg": round(age_stats[2], 2) if age_stats[2] is not None else 0,
        },
    })


@bp.route("/quality", methods=["GET"])
@login_required
def quality():
    db = get_db()
    customers = db.query(Customer).all()
    if not customers:
        return json({
            "total_rows": 0, "total_cols": 0,
            "missing_values": {}, "duplicates": 0, "dtypes": {}
        })
    cols = ["id", "gender", "age", "region_code", "policy_sales_channel",
            "previously_insured", "annual_premium", "vintage", "vehicle_age",
            "vehicle_damage", "driving_license", "response"]
    total_rows = len(customers)
    total_cols = len(cols)
    missing_values = {}
    for col in cols:
        missing = sum(1 for c in customers if getattr(c, col, None) is None)
        missing_values[col] = missing
    from collections import Counter
    id_counts = Counter(c.id for c in customers)
    duplicates = sum(v - 1 for v in id_counts.values() if v > 1)
    dtypes = {
        "id": "int", "gender": "str", "age": "int", "region_code": "str",
        "policy_sales_channel": "str", "previously_insured": "int",
        "annual_premium": "float", "vintage": "int", "vehicle_age": "str",
        "vehicle_damage": "str", "driving_license": "int", "response": "int"
    }
    return json({
        "total_rows": total_rows, "total_cols": total_cols,
        "missing_values": missing_values, "duplicates": duplicates, "dtypes": dtypes
    })


@bp.route("/visualization/<chart_type>", methods=["GET"])
@login_required
def visualization(chart_type):
    if chart_type not in EDA_CHART_FUNCS:
        raise BizException(1001, f"未知图表类型: {chart_type}，可选: {list(EDA_CHART_FUNCS.keys())}", 400)
    db = get_db()
    customers = db.query(Customer).all()
    if not customers:
        raise BizException(2001, "没有客户数据", 400)
    chart_func = EDA_CHART_FUNCS[chart_type]
    if chart_type == "response_distribution":
        resp_0 = sum(1 for c in customers if c.response == 0)
        resp_1 = sum(1 for c in customers if c.response == 1)
        b64 = chart_func({"0": resp_0, "1": resp_1})
    elif chart_type == "gender_response":
        data = [{"gender": c.gender, "response": c.response} for c in customers]
        b64 = chart_func(data)
    elif chart_type == "age_distribution":
        ages = [c.age for c in customers]
        b64 = chart_func(ages)
    elif chart_type == "premium_distribution":
        premiums = [c.annual_premium for c in customers]
        b64 = chart_func(premiums)
    else:
        raise BizException(1001, f"未知图表类型: {chart_type}", 400)
    return json({"chart_type": chart_type, "image_base64": b64, "format": "png"})