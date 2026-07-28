"""
练习任务2: 客户流失预测

**任务描述**: 构建一个二分类模型,预测客户是否会流失。
1. 生成模拟客户数据(年龄、消费金额、使用时长、是否流失)
2. 进行数据预处理(标准化、处理类别特征)
3. 使用逻辑回归、SVM、随机森林训练模型
4. 输出分类报告、混淆矩阵、ROC曲线
5. 分析哪个模型效果最好,为什么
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_curve, auc, precision_recall_curve,
                             ConfusionMatrixDisplay)

# 解决中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
np.random.seed(42)
n_samples = 1000

age = np.random.randint(18, 65, n_samples)
monthly_spend = np.random.exponential(200, n_samples)
usage_months = np.random.randint(1, 60, n_samples)
complaints = np.random.poisson(0.5, n_samples)

# 生成模拟客户数据(年龄、消费金额、使用时长、是否流失)
score = (0.01 * monthly_spend) + (0.02 * usage_months) - (0.5 * complaints) + np.random.normal(0, 0.5, n_samples)
prob_churn = 1 / (1 + np.exp(-score))
churn = (prob_churn > 0.5).astype(int)

data = pd.DataFrame({
    '年龄': age,
    '月消费金额': monthly_spend,
    '使用时长_月': usage_months,
    '投诉次数': complaints,
    '是否流失': churn
})

print("客户流失预测（模拟数据）")
print(f"样本数: {len(data)}, 流失比例: {data['是否流失'].mean():.2%}")

#进行数据预处理(标准化、处理类别特征)
X = data.drop('是否流失', axis=1)
y = data['是否流失']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 使用逻辑回归、SVM、随机森林训练模型
models = {
    '逻辑回归': LogisticRegression(random_state=42),
    'SVM': SVC(probability=True, random_state=42),
    '随机森林': RandomForestClassifier(n_estimators=50, random_state=42)
}

results = {}
for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    results[name] = {'y_pred': y_pred, 'y_prob': y_prob}
    print(f"\n{name} 分类报告:")
    print(classification_report(y_test, y_pred, target_names=['未流失', '流失']))

# 输出分类报告、混淆矩阵、ROC曲线
# 混淆矩阵
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, (name, res) in zip(axes, results.items()):
    cm = confusion_matrix(y_test, res['y_pred'])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['未流失', '流失'])
    disp.plot(ax=ax, cmap='Blues', values_format='d')
    ax.set_title(f'{name} 混淆矩阵')
plt.tight_layout()
plt.savefig('simulation_confusion.png', dpi=100)
plt.close()

# ROC & PR 曲线
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for name, res in results.items():
    fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
    axes[0].plot(fpr, tpr, label=f'{name} (AUC={auc(fpr,tpr):.3f})')
    prec, rec, _ = precision_recall_curve(y_test, res['y_prob'])
    axes[1].plot(rec, prec, label=name)

axes[0].plot([0,1], [0,1], 'k--', label='随机')
axes[0].set_title('ROC 曲线')
axes[0].legend()
axes[0].grid(alpha=0.3)

axes[1].axhline(y_test.mean(), color='gray', linestyle='--', label='基线')
axes[1].set_title('PR 曲线')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('simulation_curves.png', dpi=100)
plt.close()
print("\n已保存图片: simulation_confusion.png, simulation_curves.png")