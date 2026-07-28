"""练习任务1: 房价预测
**任务描述**: 使用加州房价数据集,完成以下任务:
1. 加载数据并进行探索性分析
2. 进行特征工程(标准化、特征选择)
3. 使用线性回归、决策树、随机森林分别训练模型
4. 比较三种模型的性能(MSE、R²)
5. 输出特征重要性排序"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 1. 加载数据并探索性分析
print("\n1. 加载数据与探索性分析 ")
housing = fetch_california_housing()
X = pd.DataFrame(housing.data, columns=housing.feature_names)
y = pd.Series(housing.target, name='MedHouseValue')

print(f"样本数: {X.shape[0]}, 特征数: {X.shape[1]}")
print(f"\n特征名称: {list(housing.feature_names)}")
print(f"\n数据预览:\n{X.head()}")
print(f"\n统计描述:\n{X.describe()}")
print(f"\n目标变量统计:\n{y.describe()}")

# 绘制特征分布与相关性
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()
for i, col in enumerate(X.columns):
    axes[i].hist(X[col], bins=50, color='steelblue', edgecolor='white')
    axes[i].set_title(col)
    axes[i].set_xlabel('')
plt.suptitle('特征分布直方图', fontsize=14)
plt.tight_layout()
plt.savefig('01_feature_distribution.png', dpi=100)
plt.close()
print("已保存特征分布图: 01_feature_distribution.png")

# 相关性热力图
plt.figure(figsize=(10, 8))
corr = pd.concat([X, y], axis=1).corr()
import seaborn as sns

sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('特征相关性热力图')
plt.tight_layout()
plt.savefig('02_correlation_heatmap.png', dpi=100)
plt.close()
print("已保存相关性热力图: 02_correlation_heatmap.png")

# 2. 特征工程
print("\n2. 特征工程 ")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("已完成标准化")

# 特征选择 (SelectKBest, k=5)
selector = SelectKBest(score_func=f_regression, k=5)
X_train_selected = selector.fit_transform(X_train_scaled, y_train)
X_test_selected = selector.transform(X_test_scaled)
selected_features = X.columns[selector.get_support()].tolist()
print(f"选择的特征 (k=5): {selected_features}")
print(f"特征选择后维度: {X_train_selected.shape}")

# 3. 训练三种模型
print("\n--- 3. 模型训练 ---")

models = {
    '线性回归': LinearRegression(),
    '决策树': DecisionTreeRegressor(max_depth=10, random_state=42),
    '随机森林': RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
}

results = []
for name, model in models.items():
    if name == '线性回归':
        model.fit(X_train_selected, y_train)
        y_pred = model.predict(X_test_selected)
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    results.append({'模型': name, 'MSE': mse, 'R²': r2})
    print(f"{name}: MSE={mse:.4f}, R²={r2:.4f}")

# 4. 模型性能对比
print("\n4. 模型性能对比 ")
df_results = pd.DataFrame(results)
print(df_results.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].bar(df_results['模型'], df_results['MSE'], color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
axes[0].set_title('MSE 对比 (越低越好)')
axes[0].set_ylabel('MSE')
axes[0].grid(axis='y', alpha=0.3)

axes[1].bar(df_results['模型'], df_results['R²'], color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
axes[1].set_title('R**2 对比 (越接近1越好)')
axes[1].set_ylabel('R**2')
axes[1].set_ylim([0, 1])
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('03_model_comparison.png', dpi=100)
plt.close()
print("已保存模型对比图: 03_model_comparison.png")

# 5. 特征重要性排序 (基于随机森林)
print("\n5. 特征重要性排序 (随机森林)")
rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
print(importances.to_string())

plt.figure(figsize=(10, 6))
importances.plot(kind='barh', color='steelblue')
plt.title('随机森林特征重要性排序')
plt.xlabel('重要性')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('04_feature_importance.png', dpi=100)
plt.close()
print("已保存特征重要性图: 04_feature_importance.png")

print("\n" + "=" * 50)
print("任务完成!")
print("=" * 50)
