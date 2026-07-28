import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import matplotlib
import matplotlib.font_manager as fm

os.makedirs("output", exist_ok=True)

# 清除字体缓存
fm._load_fontmanager(try_read_cache=False)

# 设置seaborn整体绘图风格（注意：这会覆盖matplotlib的字体设置）
sns.set_style("whitegrid")    # 可选：white / dark / whitegrid / darkgrid / ticks
sns.set_context("notebook")   # 控制字体大小：paper / notebook / talk / poster

# 【重要】在seaborn样式设置之后，重新配置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "SimSun"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 12

# 创建保存图片文件夹，避免报错
if not os.path.exists("sns_output"):
    os.mkdir("sns_output")


# 先下载保存到本地，再从本地读取（避免网络不佳导致的问题）
# tips = sns.load_dataset("tips")       # 小费数据集（餐饮消费）
# iris = sns.load_dataset("iris")       # 鸢尾花数据集
# flights = sns.load_dataset("flights") # 航班客流时序数据

# 保存到本地CSV文件
# tips.to_csv("tips.csv", index=False)
# # iris.to_csv("iris.csv", index=False)
# # flights.to_csv("flights.csv", index=False)

# print("数据集已保存到本地CSV文件")

print("=== 从本地CSV文件读取数据集 ===")
tips = pd.read_csv("tips.csv")
iris = pd.read_csv("iris.csv")

print("=== tips数据集前5行 ===")
print(tips.head())
print("\n=== 数据集字段类型 ===")
print(tips.dtypes)

"""习题 1：绘制小费金额 (`tip`) 的分布直方图，要求包含核密度曲线，分箱数为 30。"""
plt.figure(figsize=(8, 5))
sns.histplot(data=tips, x="tip", kde=True, bins=30, color="purple")
plt.title("小费金额分布直方图（含核密度）", fontsize=13)
plt.xlabel("消费金额")
plt.ylabel("频次")
plt.tight_layout()
plt.savefig("output/01_hist.png", dpi=300, bbox_inches="tight")
plt.show()


"""习题 2：绘制总账单 (`total_bill`) 的核密度图，按是否吸烟 (`smoker`) 分组对比。"""
plt.figure(figsize=(8, 5))
sns.kdeplot(data=tips, x="total_bill", hue="smoker", linewidth=2)
plt.title("总账单核密度（按吸烟分组）", fontsize=13)
plt.xlabel("总账单")
plt.ylabel("密度")
plt.tight_layout()
plt.savefig("output/ex02_kde.png", dpi=300, bbox_inches="tight")
plt.show()


"""习题 3：绘制箱线图，X 轴为用餐时段 (`time`)，Y 轴为小费 (`tip`)，按性别 (`sex`) 分组颜色。"""
plt.figure(figsize=(8, 5))
sns.boxplot(data=tips, x="time", y="tip", hue="sex", palette="Set2")
plt.title("不同时段小费分布（分性别）", fontsize=13)
plt.xlabel("用餐时段")
plt.ylabel("小费")
plt.tight_layout()
plt.savefig("output/ex03_boxplot.png", dpi=300, bbox_inches="tight")
plt.show()


"""习题 4：绘制小提琴图，X 轴为星期 (`day`)，Y 轴为小费 (`tip`)，按时段 (`time`) 分组并分割显示 (`split=True`)。"""
plt.figure(figsize=(9, 5))
sns.violinplot(data=tips, x="day", y="tip", hue="time", split=True, palette="RdBu")
plt.title("各星期小费分布（分时段分割小提琴图）", fontsize=13)
plt.xlabel("星期")
plt.ylabel("小费")
plt.tight_layout()
plt.savefig("output/ex04_violin.png", dpi=300, bbox_inches="tight")
plt.show()


"""习题 5：绘制柱状图，X 轴为星期 (`day`)，Y 轴为小费 (`tip`)，**不显示误差线**。"""
plt.figure(figsize=(7, 5))
sns.barplot(data=tips, x="day", y="tip", palette="Blues_d", ci=None)
plt.title("各星期平均小费（无误差线）", fontsize=13)
plt.xlabel("星期")
plt.ylabel("平均小费")
plt.tight_layout()
plt.savefig("output/ex05_bar.png", dpi=300, bbox_inches="tight")
plt.show()


"""习题 6：计算数值列的相关系数，绘制热力图，要求显示数值 (`annot=True`)，配色使用 `coolwarm`。"""
plt.figure(figsize=(6, 5))
corr_matrix = tips.select_dtypes(include=[np.number]).corr()
sns.heatmap(
    corr_matrix,
    annot=True,
    cmap="coolwarm",
    vmin=-1, vmax=1,
    square=True,
    linewidths=0.5
)
plt.title("数值特征相关性热力图", fontsize=13)
plt.tight_layout()
plt.savefig("output/ex06_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()


"""习题 7：绘制回归图，X 轴为账单，Y 轴为小费。要求按吸烟情况 (`smoker`) 分别画出两条回归线进行对比。"""
plt.figure(figsize=(8, 5))
sns.regplot(data=tips[tips["smoker"]=="Yes"], x="total_bill", y="tip",
            color="red", label="吸烟", scatter_kws={"alpha":0.4})
sns.regplot(data=tips[tips["smoker"]=="No"], x="total_bill", y="tip",
            color="blue", label="不吸烟", scatter_kws={"alpha":0.4})
plt.title("账单与小费回归关系（按吸烟分组）", fontsize=13)
plt.xlabel("总账单")
plt.ylabel("小费")
plt.legend()
plt.tight_layout()
plt.savefig("output/ex07_regplot.png", dpi=300, bbox_inches="tight")
plt.show()


"""习题 8：使用尾花数据 (`iris`)，选取 `sepal_length`, `sepal_width`, `petal_length` 和 `species` 字段，绘制配对散点矩阵 (`pairplot`)。"""
iris_sub = iris[["sepal_length", "sepal_width", "petal_length", "species"]]
g = sns.pairplot(iris_sub, hue="species", height=2)
g.fig.suptitle("鸢尾花特征配对矩阵", y=1.02, fontsize=14)
g.savefig("output/ex08_pairplot.png", dpi=300, bbox_inches="tight")
plt.show()


"""习题 9：创建一个 2 行 1 列的子图画布：
  * 上图：账单密度的核密度图。
  * 下图：男女平均小费的柱状图。"""
fig, axes = plt.subplots(2, 1, figsize=(8, 10))
# 上图
sns.kdeplot(data=tips, x="total_bill", fill=True, ax=axes[0])
axes[0].set_title("总账单核密度图", fontsize=13)
axes[0].set_xlabel("总账单")
axes[0].set_ylabel("密度")
# 下图
sns.barplot(data=tips, x="sex", y="tip", ax=axes[1], ci=None, palette="pastel")
axes[1].set_title("男女平均小费", fontsize=13)
axes[1].set_xlabel("性别")
axes[1].set_ylabel("平均小费")
plt.tight_layout()
plt.savefig("output/ex09_subplots.png", dpi=300, bbox_inches="tight")
plt.show()


"""习题 10（综合）：创建一个 1 行 2 列的子图画布：
  * 左图：男女消费金额分布的小提琴图。
  * 右图：一周每日平均消费的柱状图。
  * 设置总标题为"餐饮消费综合可视化图表"。"""
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
# 左图：男女总账单的小提琴图
sns.violinplot(data=tips, x="sex", y="total_bill", ax=axes[0], palette="Set3")
axes[0].set_title("男女消费金额小提琴图", fontsize=13)
axes[0].set_xlabel("性别")
axes[0].set_ylabel("总账单")
# 右图：每日平均总账单的柱状图
sns.barplot(data=tips, x="day", y="total_bill", ax=axes[1], ci=None, palette="Oranges_d")
axes[1].set_title("各星期平均消费额", fontsize=13)
axes[1].set_xlabel("星期")
axes[1].set_ylabel("平均总账单")
plt.tight_layout()
plt.savefig("output/ex10_combined.png", dpi=300, bbox_inches="tight")
plt.show()