import json
from io import BytesIO
from flask import Blueprint, request, send_file
from app.core.database import get_db
from app.core.response import json as api_json, BizException
from app.core.dependencies import login_required, role_required, get_current_user
from app.models.experiment import Experiment
from app.utils.visualizer import MODEL_CHART_FUNCS
from app.services.ml_service import train_model, predict_all, predict_upload, export_model, import_model

bp = Blueprint("model", __name__)


@bp.route("/train", methods=["POST"])
@login_required
@role_required("admin")
def train():
    body = request.get_json(silent=True) or {}
    models_list = body.get("models_list")
    test_size = body.get("test_size", 0.2)
    random_state = body.get("random_state", 42)
    params = body.get("params")
    result = train_model(models_list=models_list, test_size=test_size,
                         random_state=random_state, params=params)
    return api_json(result)


@bp.route("/experiments", methods=["GET"])
@login_required
def experiments():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    page = max(page, 1)
    per_page = max(per_page, 1)
    model_name = request.args.get("model_name", "").strip() or None
    db = get_db()
    items, total = Experiment.paginate(db, page=page, per_page=per_page, model_name=model_name)
    return api_json({
        "items": [{
            "id": e.id, "model_name": e.model_name,
            "accuracy": e.accuracy, "precision": e.precision,
            "recall": e.recall, "f1_score": e.f1_score,
            "roc_auc": e.roc_auc, "params": e.params,
            "model_path": e.model_path, "is_best": e.is_best,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        } for e in items],
        "total": total, "page": page, "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page else 0,
    })


@bp.route("/best", methods=["GET"])
@login_required
def best():
    db = get_db()
    exp = Experiment.find_best(db)
    if not exp:
        raise BizException(3002, "无最佳模型，请先训练", 400)
    return api_json({
        "id": exp.id, "model_name": exp.model_name,
        "accuracy": exp.accuracy, "precision": exp.precision,
        "recall": exp.recall, "f1_score": exp.f1_score,
        "roc_auc": exp.roc_auc, "params": exp.params,
        "model_path": exp.model_path, "is_best": exp.is_best,
    })


@bp.route("/predict", methods=["POST"])
@login_required
def predict():
    body = request.get_json(silent=True) or {}
    model_name = body.get("model_name")
    result = predict_all(model_name=model_name)
    return api_json(result)


@bp.route("/predict_upload", methods=["POST"])
@login_required
def predict_upload_route():
    if "file" not in request.files:
        raise BizException(1001, "请上传预测文件", 400)
    file = request.files["file"]
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise BizException(1001, "仅支持.xlsx/.xls格式", 400)
    file_data = BytesIO(file.read())
    model_name = request.form.get("model_name")
    result = predict_upload(file_data, model_name=model_name)
    return api_json(result)


@bp.route("/visualization/<chart_type>", methods=["GET"])
@login_required
def visualization(chart_type):
    if chart_type not in MODEL_CHART_FUNCS:
        raise BizException(1001, f"未知图表类型: {chart_type}，可选: {list(MODEL_CHART_FUNCS.keys())}", 400)
    db = get_db()
    experiments = db.query(Experiment).order_by(Experiment.id.desc()).all()
    if not experiments:
        raise BizException(3002, "无实验记录，请先训练模型", 400)
    chart_func = MODEL_CHART_FUNCS[chart_type]
    if chart_type == "roc_curve":
        all_roc = []
        for e in experiments:
            try:
                p = json.loads(e.params) if e.params else {}
                roc = p.get("roc", {})
                if roc:
                    all_roc.append({"name": e.model_name, "fpr": roc["fpr"], "tpr": roc["tpr"]})
            except (json.JSONDecodeError, TypeError):
                continue
        if not all_roc:
            raise BizException(3002, "无ROC数据", 400)
        b64 = chart_func(all_roc[0]["fpr"], all_roc[0]["tpr"])
    elif chart_type == "metrics_comparison":
        results = {}
        for e in experiments:
            results[e.model_name] = {
                "accuracy": e.accuracy, "precision": e.precision,
                "recall": e.recall, "f1_score": e.f1_score, "roc_auc": e.roc_auc,
            }
        b64 = chart_func(results)
    elif chart_type == "confusion_matrix":
        p = json.loads(experiments[0].params) if experiments[0].params else {}
        cm = p.get("confusion_matrix", [[0, 0], [0, 0]])
        b64 = chart_func(cm, experiments[0].model_name)
    elif chart_type == "feature_importance":
        p = json.loads(experiments[0].params) if experiments[0].params else {}
        fi = p.get("feature_importances", [])
        fn = p.get("feature_names", [])
        b64 = chart_func(fi, fn)
    else:
        raise BizException(1001, f"未知图表类型: {chart_type}", 400)
    return api_json({"chart_type": chart_type, "image_base64": b64, "format": "png"})


@bp.route("/export/<model_name>", methods=["GET"])
@login_required
@role_required("admin")
def export_model_route(model_name):
    path = export_model(model_name)
    return send_file(path, as_attachment=True, download_name=f"{model_name}.joblib")


@bp.route("/import", methods=["POST"])
@login_required
@role_required("admin")
def import_model_route():
    if "file" not in request.files:
        raise BizException(1001, "请上传模型文件", 400)
    file = request.files["file"]
    if not file.filename:
        raise BizException(1001, "请选择文件", 400)
    result = import_model(file.read(), file.filename)
    return api_json(result)