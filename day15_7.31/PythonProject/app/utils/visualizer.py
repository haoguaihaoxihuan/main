import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from app.core.response import BizException

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return b64


def plot_response_distribution(response_counts: dict) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["未购买 (0)", "已购买 (1)"]
    values = [response_counts.get("0", 0), response_counts.get("1", 0)]
    colors = ["#3498db", "#e74c3c"]
    ax.bar(labels, values, color=colors)
    ax.set_title("Response Distribution")
    ax.set_ylabel("Count")
    for i, v in enumerate(values):
        ax.text(i, v + max(values) * 0.01, str(v), ha="center", fontsize=10)
    return _fig_to_base64(fig)


def plot_gender_response(data: list[dict]) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))
    categories = ["Male-0", "Male-1", "Female-0", "Female-1"]
    counts = {c: 0 for c in categories}
    for d in data:
        key = f"{d['gender']}-{d['response']}"
        if key in counts:
            counts[key] += 1
    values = [counts[c] for c in categories]
    colors = ["#3498db", "#e74c3c", "#3498db", "#e74c3c"]
    ax.bar(categories, values, color=colors)
    ax.set_title("Gender x Response")
    ax.set_ylabel("Count")
    return _fig_to_base64(fig)


def plot_age_distribution(ages: list[int]) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(ages, bins=20, color="#3498db", edgecolor="white")
    ax.set_title("Age Distribution")
    ax.set_xlabel("Age")
    ax.set_ylabel("Count")
    return _fig_to_base64(fig)


def plot_premium_distribution(premiums: list[float]) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(premiums, bins=20, color="#2ecc71", edgecolor="white")
    ax.set_title("Annual Premium Distribution")
    ax.set_xlabel("Annual Premium")
    ax.set_ylabel("Count")
    return _fig_to_base64(fig)


def plot_roc_curve(fpr: list, tpr: list) -> str:
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="#e74c3c", linewidth=2, label="ROC Curve")
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve")
    ax.legend()
    return _fig_to_base64(fig)


def plot_metrics_comparison(results: dict) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    model_names = list(results.keys())
    metrics = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    x = np.arange(len(model_names))
    width = 0.15
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]
    for i, metric in enumerate(metrics):
        values = [results[m].get(metric, 0) for m in model_names]
        ax.bar(x + i * width, values, width, label=metric, color=colors[i])
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(model_names)
    ax.set_ylabel("Score")
    ax.set_title("Model Metrics Comparison")
    ax.legend()
    return _fig_to_base64(fig)


def plot_confusion_matrix(cm: list, model_name: str = "") -> str:
    fig, ax = plt.subplots(figsize=(5, 4))
    cm = np.array(cm)
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Pred 0", "Pred 1"])
    ax.set_yticklabels(["True 0", "True 1"])
    ax.set_title(f"Confusion Matrix{f' - {model_name}' if model_name else ''}")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    fontsize=14, color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im, ax=ax)
    return _fig_to_base64(fig)


def plot_feature_importance(importances: list, feature_names: list) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    pairs = sorted(zip(importances, feature_names), key=lambda x: x[0], reverse=True)
    imp, names = zip(*pairs) if pairs else ([], [])
    ax.barh(range(len(names)), imp, color="#3498db")
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.set_xlabel("Importance")
    ax.set_title("Feature Importance")
    ax.invert_yaxis()
    return _fig_to_base64(fig)


EDA_CHART_FUNCS = {
    "response_distribution": plot_response_distribution,
    "gender_response": plot_gender_response,
    "age_distribution": plot_age_distribution,
    "premium_distribution": plot_premium_distribution,
}

MODEL_CHART_FUNCS = {
    "roc_curve": plot_roc_curve,
    "metrics_comparison": plot_metrics_comparison,
    "confusion_matrix": plot_confusion_matrix,
    "feature_importance": plot_feature_importance,
}