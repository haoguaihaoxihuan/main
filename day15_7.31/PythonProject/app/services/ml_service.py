import os
import json
import numpy as np
import pandas as pd
from io import BytesIO
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
import joblib
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.response import BizException
from app.models.customers import Customer
from app.models.experiment import Experiment
from app.utils.data_processor import parse_excel


MODEL_NAMES = ["logistic_regression", "xgboost", "random_forest"]

FEATURE_COLS = [
    "gender", "age", "driving_license", "region_code", "previously_insured",
    "vehicle_age", "vehicle_damage", "annual_premium", "policy_sales_channel", "vintage"
]
TARGET_COL = "response"


def _ensure_model_dir():
    os.makedirs(settings.MODEL_DIR, exist_ok=True)


def _load_customers_as_df(db):
    customers = db.query(Customer).all()
    if not customers:
        raise BizException(2001, "没有客户数据，请先上传数据", 400)
    rows = []
    for c in customers:
        rows.append({
            "gender": c.gender,
            "age": c.age,
            "driving_license": c.driving_license,
            "region_code": c.region_code,
            "previously_insured": c.previously_insured,
            "vehicle_age": c.vehicle_age,
            "vehicle_damage": c.vehicle_damage,
            "annual_premium": c.annual_premium,
            "policy_sales_channel": c.policy_sales_channel,
            "vintage": c.vintage,
            "response": c.response,
        })
    return pd.DataFrame(rows)


def _preprocess(df: pd.DataFrame, scaler: StandardScaler = None, fit: bool = False):
    df = df.copy()
    df["gender"] = df["gender"].map({"Male": 0, "Female": 1})
    df["vehicle_damage"] = df["vehicle_damage"].map({"No": 0, "Yes": 1})
    df["vehicle_age"] = df["vehicle_age"].map({"< 1 Year": 0, "1-2 Year": 1, "> 2 Years": 2})
    numeric_cols = ["age", "annual_premium", "region_code", "policy_sales_channel", "vintage"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if scaler is None:
        scaler = StandardScaler()
    if fit:
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    else:
        df[numeric_cols] = scaler.transform(df[numeric_cols])
    return df, scaler


def _get_model(name: str, params: dict = None, scale_pos_weight: float = 1.0):
    p = params or {}
    if name == "logistic_regression":
        return LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=p.get("random_state", 42), **{k: v for k, v in p.items() if k != "random_state"}
        )
    elif name == "xgboost":
        import xgboost as xgb
        return xgb.XGBClassifier(
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            random_state=p.get("random_state", 42),
            use_label_encoder=False,
            **{k: v for k, v in p.items() if k not in ("random_state", "use_label_encoder")}
        )
    elif name == "random_forest":
        return RandomForestClassifier(
            class_weight="balanced",
            random_state=p.get("random_state", 42),
            **{k: v for k, v in p.items() if k != "random_state"}
        )
    else:
        raise BizException(1001, f"未知模型: {name}", 400)


def _compute_metrics(y_true, y_pred, y_proba):
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_proba)), 4),
    }


def train_model(models_list: list = None, test_size: float = 0.2, random_state: int = 42,
                 params: dict = None) -> dict:
    db = SessionLocal()
    try:
        df = _load_customers_as_df(db)
        df, scaler = _preprocess(df, fit=True)
        X = df[FEATURE_COLS].values
        y = df[TARGET_COL].values.astype(int)
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
        except ValueError:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
        n_neg = int((y_train == 0).sum())
        n_pos = int((y_train == 1).sum())
        spw = n_neg / n_pos if n_pos > 0 else 1.0
        if models_list is None:
            models_list = MODEL_NAMES
        _ensure_model_dir()
        Experiment.clear_best(db)
        results = {}
        best_auc = -1
        best_model_name = None
        for name in models_list:
            model_params = (params or {}).get(name, {})
            model = _get_model(name, model_params, spw)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]
            metrics = _compute_metrics(y_test, y_pred, y_proba)
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            cm = confusion_matrix(y_test, y_pred)
            if hasattr(model, "feature_importances_"):
                fi = model.feature_importances_.tolist()
            elif hasattr(model, "coef_"):
                fi = model.coef_[0].tolist()
            else:
                fi = []
            params_json = json.dumps({
                "roc": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
                "confusion_matrix": cm.tolist(),
                "feature_importances": fi,
                "feature_names": FEATURE_COLS,
            })
            model_path = os.path.join(settings.MODEL_DIR, f"{name}.joblib")
            joblib.dump({"model": model, "scaler": scaler}, model_path)
            results[name] = metrics
            is_best = metrics["roc_auc"] > best_auc
            if is_best:
                best_auc = metrics["roc_auc"]
                best_model_name = name
            Experiment.create(
                db, name, metrics["accuracy"], metrics["precision"],
                metrics["recall"], metrics["f1_score"], metrics["roc_auc"],
                params_json, model_path, is_best=False
            )
        best_exp = db.query(Experiment).filter(
            Experiment.model_name == best_model_name
        ).order_by(Experiment.id.desc()).first()
        if best_exp:
            best_exp.is_best = True
            db.commit()
        return {"best_model": best_model_name, "results": results}
    except BizException:
        raise
    except Exception as e:
        raise BizException(3001, f"训练失败: {str(e)}", 500)
    finally:
        db.close()


def predict_all(model_name: str = None) -> dict:
    db = SessionLocal()
    try:
        if model_name:
            exp = db.query(Experiment).filter(Experiment.model_name == model_name).order_by(Experiment.id.desc()).first()
        else:
            exp = Experiment.find_best(db)
        if not exp:
            raise BizException(3002, "无可用模型，请先训练", 400)
        model_path = exp.model_path
        if not os.path.exists(model_path):
            raise BizException(3002, f"模型文件不存在: {model_path}", 400)
        bundle = joblib.load(model_path)
        model = bundle["model"]
        scaler = bundle["scaler"]
        customers = db.query(Customer).all()
        if not customers:
            raise BizException(2001, "没有客户数据", 400)
        rows = []
        for c in customers:
            rows.append({
                "gender": c.gender,
                "age": c.age,
                "driving_license": c.driving_license,
                "region_code": c.region_code,
                "previously_insured": c.previously_insured,
                "vehicle_age": c.vehicle_age,
                "vehicle_damage": c.vehicle_damage,
                "annual_premium": c.annual_premium,
                "policy_sales_channel": c.policy_sales_channel,
                "vintage": c.vintage,
                "response": c.response,
            })
        df = pd.DataFrame(rows)
        df_processed, _ = _preprocess(df, scaler=scaler, fit=False)
        X = df_processed[FEATURE_COLS].values
        probs = model.predict_proba(X)[:, 1]
        for i, c in enumerate(customers):
            c.predicted_prob = float(probs[i])
        db.commit()
        return {"model_name": exp.model_name, "predicted_count": len(customers)}
    except BizException:
        raise
    except Exception as e:
        raise BizException(3002, f"预测失败: {str(e)}", 500)
    finally:
        db.close()


def predict_upload(file_data: BytesIO, model_name: str = None) -> dict:
    db = SessionLocal()
    try:
        if model_name:
            exp = db.query(Experiment).filter(Experiment.model_name == model_name).order_by(Experiment.id.desc()).first()
        else:
            exp = Experiment.find_best(db)
        if not exp:
            raise BizException(3002, "无可用模型，请先训练", 400)
        model_path = exp.model_path
        if not os.path.exists(model_path):
            raise BizException(3002, f"模型文件不存在: {model_path}", 400)
        bundle = joblib.load(model_path)
        model = bundle["model"]
        scaler = bundle["scaler"]
        valid_rows, quality_report, errors = parse_excel(file_data)
        if not valid_rows:
            raise BizException(2002, "Excel中没有有效数据行", 400)
        df = pd.DataFrame(valid_rows)
        df_processed, _ = _preprocess(df, scaler=scaler, fit=False)
        X = df_processed[FEATURE_COLS].values
        probs = model.predict_proba(X)[:, 1]
        predictions = []
        for i, row in enumerate(valid_rows):
            predictions.append({
                "id": row.get("id"),
                "predicted_prob": round(float(probs[i]), 4),
            })
        positive_count = sum(1 for p in predictions if p["predicted_prob"] >= 0.5)
        negative_count = len(predictions) - positive_count
        return {
            "model_name": exp.model_name,
            "total_count": len(predictions),
            "statistics": {"positive": positive_count, "negative": negative_count},
            "predictions": predictions,
        }
    except BizException:
        raise
    except Exception as e:
        raise BizException(3002, f"预测失败: {str(e)}", 500)
    finally:
        db.close()


def export_model(model_name: str) -> str:
    path = os.path.join(settings.MODEL_DIR, f"{model_name}.joblib")
    if not os.path.exists(path):
        raise BizException(3002, f"模型文件不存在: {model_name}", 400)
    return path


def import_model(file_data: bytes, filename: str) -> dict:
    if not filename.lower().endswith(".joblib"):
        raise BizException(1001, "仅支持.joblib格式", 400)
    _ensure_model_dir()
    save_path = os.path.join(settings.MODEL_DIR, filename)
    with open(save_path, "wb") as f:
        f.write(file_data)
    try:
        joblib.load(save_path)
    except Exception:
        os.remove(save_path)
        raise BizException(2002, "模型文件格式无效", 400)
    name = filename.replace(".joblib", "")
    return {"model_name": name, "path": save_path}