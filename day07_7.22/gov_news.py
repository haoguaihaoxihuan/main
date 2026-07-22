#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python爬虫作业：BeautifulSoup抓取中国政府网新闻（最终修正版）
技术栈：requests + BeautifulSoup4 + html.parser + SQLAlchemy + SQLite
目标网址：https://www.gov.cn/toutiao/liebiao/

【重要提示】
- 本程序仅抓取第1~10页，用于课程学习，禁止商用
- 已配置防反爬措施：请求头伪装、随机延时、超时设置
- 单线程串行抓取，不使用多线程/代理IP
- 数据库唯一约束冲突已妥善处理，程序不会因重复链接而中断
"""

# ==================== 第一部分：导入依赖库 ====================
# 导入requests用于发送HTTP请求，获取网页源码
import requests
# 导入time和random用于控制抓取间隔，模拟人类行为，降低反爬风险
import time
import random
# 导入csv用于将数据库数据导出为CSV文件（拓展功能）
import csv
# 从bs4导入BeautifulSoup，这是核心的HTML解析库，用于从网页源码中提取数据
from bs4 import BeautifulSoup
# 导入SQLAlchemy相关模块：数据库引擎、字段类型、ORM基类、会话工厂等
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
# 导入SQLAlchemy的异常类，用于处理数据库操作中的错误，特别是唯一约束冲突
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# 导入urllib3用于禁用SSL警告（因为代码中使用了verify=False，会触发不安全请求警告）
import urllib3

# 禁用SSL警告（因为使用了verify=False，忽略不安全请求警告）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ==================== 第二部分：数据库模型 ====================
# 创建SQLite数据库引擎，连接到本地文件gov_news.db（如果不存在会自动创建）
engine = create_engine("sqlite:///gov_news.db", echo=False)
# 使用declarative_base创建ORM基类，后续所有数据表模型都将继承自该基类
Base = declarative_base()
# 创建数据库会话工厂，用于生成与数据库交互的会话对象
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class GovNews(Base):
    """新闻数据表模型，映射到数据库中的gov_news表"""
    __tablename__ = "gov_news"  # 指定表名
    # 定义表字段：id为自增主键，title为标题（字符串，长度500），publish_time为发布时间（字符串），link为新闻链接
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500))
    publish_time = Column(String(30))
    link = Column(String(800), unique=True)  # unique=True确保链接不重复，防止抓取重复数据


# 创建表（如果数据库中不存在该表，则根据模型定义创建）
Base.metadata.create_all(bind=engine)


# ==================== 第三部分：请求头配置 ====================
# 构造HTTP请求头，模拟真实浏览器访问，这是反爬虫的第一道防线
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Referer": "https://www.gov.cn/",  # 设置来源页面，部分网站会检查Referer
}

# 创建一个Session对象，可以复用连接并持久化请求头，提高效率
session = requests.Session()
session.headers.update(headers)


# ==================== 第四部分：单页抓取函数 ====================
def crawl_page(page_num, db_session):
    """
    抓取指定页码的新闻，并逐条存入数据库（每条单独提交，避免唯一约束中断）
    参数：
        page_num: 页码（整数，1~10）
        db_session: 数据库会话对象（用于操作数据库）
    返回：
        True: 抓取成功（即使部分数据重复跳过）
        False: 发生严重错误（如403、网络异常等）
    """
    # 构造该页的URL，根据目标网站规则，首页为home_1.htm，后续页码为home_2.htm ... home_10.htm
    url = f"https://www.gov.cn/toutiao/liebiao/home_{page_num}.htm"
    print(f"\n>>> 正在抓取第 {page_num} 页: {url}")

    try:
        # 使用session发送GET请求，timeout设置超时时间（秒），verify=False关闭SSL证书验证（避免某些网络环境拦截）
        resp = session.get(url, timeout=5, verify=False)

        # 检查HTTP状态码，如果是403（Forbidden），说明被服务器反爬，立即终止
        if resp.status_code == 403:
            print(f"[警告] 第{page_num}页返回403，触发反爬，终止抓取")
            return False

        # 将响应内容解码为UTF-8（中国政府网使用UTF-8编码）
        resp.encoding = "utf-8"

        # ========== BeautifulSoup核心解析开始 ==========
        # 使用BeautifulSoup解析HTML源码，解析器选择"html.parser"（Python内置，无需额外安装）
        # 也可以换成"lxml"（需安装lxml库），效果类似
        soup = BeautifulSoup(resp.text, "html.parser")

        # 使用CSS选择器定位新闻列表容器
        # 通过查看网页源码，发现新闻列表在div.news_box下的ul li中
        # 首先尝试主选择器"div.news_box ul li"
        news_list = soup.select("div.news_box ul li")
        if not news_list:
            # 如果主选择器没找到，使用备用选择器".news_box li"（更宽泛）
            news_list = soup.select(".news_box li")

        # 输出本页找到的新闻条数（用于调试和日志）
        print(f"    本页共找到 {len(news_list)} 条新闻")

        # 记录本页成功入库的数量
        success_count = 0

        # 遍历每条新闻的li标签（使用enumerate获取序号，方便输出日志）
        for idx, item in enumerate(news_list, start=1):
            try:
                # ---------- 提取标题和链接 ----------
                # 使用select_one在当前li中查找h4下的a标签（新闻标题通常放在h4 a中）
                title_tag = item.select_one("h4 a")
                if not title_tag:
                    continue  # 如果没有找到标题标签，跳过该条
                # 使用get_text(strip=True)获取文本内容，并去除首尾空白字符
                title = title_tag.get_text(strip=True)
                # 使用get("href")获取a标签的href属性值（链接）
                href = title_tag.get("href")
                if not href:
                    continue  # 如果没有链接，跳过

                # 补全链接：部分href是相对路径（如"/xxx"），需要拼接完整URL
                if href.startswith("http"):
                    full_link = href  # 已经是绝对链接
                else:
                    full_link = "https://www.gov.cn" + href  # 拼接网站域名

                # ---------- 提取发布时间 ----------
                # 使用select_one在当前li中查找span.date（发布时间）
                time_tag = item.select_one("span.date")
                if not time_tag:
                    continue  # 如果没有时间标签，跳过
                pub_time = time_tag.get_text(strip=True)  # 获取文本内容并去除空白

                # 空值过滤：如果标题或时间为空，跳过
                if not title or not pub_time:
                    continue

                # ---------- 关键修正：每条新闻单独提交，避免唯一约束导致整体失败 ----------
                # 创建数据库模型对象，对应一条新闻记录
                news = GovNews(title=title, publish_time=pub_time, link=full_link)
                # 将对象添加到数据库会话（缓存中）
                db_session.add(news)
                # 立即提交（commit）到数据库，如果该链接已存在，会触发IntegrityError（唯一约束冲突）
                # 这样每条新闻独立提交，不会因为一条重复而导致整页数据丢失
                db_session.commit()
                success_count += 1  # 成功计数

            except IntegrityError:
                # 捕获唯一约束冲突异常（链接重复）
                # 回滚当前这条记录（撤销add操作），保证会话恢复到正常状态
                db_session.rollback()
                print(f"    [{idx}] 跳过：链接已存在（重复新闻）")
                continue  # 跳过该条，继续处理下一条
            except Exception as e:
                # 捕获其他单条处理异常（如字段长度超限等）
                db_session.rollback()  # 回滚当前这条
                print(f"    [{idx}] 单条处理异常：{e}")
                continue  # 继续下一条

        # 本页处理完成，输出成功入库条数
        print(f"    ✓ 第{page_num}页处理完成，成功入库 {success_count} 条")
        return True  # 返回True表示该页抓取成功

    # ---------- 异常处理 ----------
    except requests.exceptions.Timeout:
        # 请求超时异常
        print(f"[错误] 第{page_num}页请求超时")
        return False
    except requests.exceptions.RequestException as e:
        # 其他网络请求异常（如连接错误、DNS错误等）
        print(f"[错误] 第{page_num}页网络异常：{e}")
        return False
    except Exception as e:
        # 其他未知异常（如解析错误等）
        print(f"[错误] 第{page_num}页未知异常：{e}")
        return False


# ==================== 第五部分：导出CSV（拓展功能） ====================
def export_to_csv():
    """将数据库全部数据导出为CSV文件（使用utf-8-sig编码，以便Excel正常打开）"""
    db = SessionLocal()  # 创建数据库会话
    try:
        # 查询所有新闻，按id升序排列
        all_news = db.query(GovNews).order_by(GovNews.id).all()
        # 打开CSV文件，newline=''防止写入多余空行，encoding='utf-8-sig'添加BOM，Excel可识别
        with open("gov_news.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(["id", "标题", "发布时间", "链接"])
            # 遍历每条新闻，写入一行数据
            for news in all_news:
                writer.writerow([news.id, news.title, news.publish_time, news.link])
        print(f"\n>>> CSV导出成功！共导出 {len(all_news)} 条新闻到 gov_news.csv")
    except Exception as e:
        print(f"CSV导出失败：{e}")
    finally:
        db.close()  # 关闭会话，释放资源


# ==================== 第六部分：交互式菜单（拓展选做） ====================
def show_menu():
    """显示交互菜单选项"""
    print("\n" + "=" * 50)
    print("   中国政府网新闻爬虫 - 交互菜单")
    print("=" * 50)
    print("1. 抓取指定单页（1-10）")
    print("2. 批量抓取第1~10页（课程要求）")
    print("3. 将数据库导出为CSV")
    print("4. 退出程序")
    print("=" * 50)


def interactive_mode():
    """交互式菜单主循环，让用户选择操作"""
    while True:
        show_menu()
        choice = input("请输入选项（1/2/3/4）：").strip()

        if choice == "1":
            # 单页抓取
            page = input("请输入页码（1-10）：").strip()
            if page.isdigit() and 1 <= int(page) <= 10:
                db = SessionLocal()
                crawl_page(int(page), db)
                db.close()
            else:
                print("页码无效，请输入1-10之间的数字")

        elif choice == "2":
            # 批量抓取第1~10页
            db = SessionLocal()
            for page in range(1, 11):
                result = crawl_page(page, db)
                if not result:  # 如果某页抓取失败，终止后续
                    print("\n[系统] 抓取异常，终止后续")
                    break
                if page < 10:
                    # 随机休眠2~4秒，模拟人类浏览行为，减轻服务器压力，防止被反爬
                    sleep_time = random.uniform(2, 4)
                    print(f"    休眠 {sleep_time:.2f} 秒...")
                    time.sleep(sleep_time)
            db.close()
            export_to_csv()  # 抓取完成后自动导出CSV
            print("批量抓取完成！")

        elif choice == "3":
            export_to_csv()

        elif choice == "4":
            print("再见！")
            break

        else:
            print("输入无效，请重新选择")


# ==================== 第七部分：主程序入口 ====================
if __name__ == "__main__":
    """
    默认执行方式：直接批量抓取第1~10页（满足基础作业要求）
    若想使用交互式菜单，请将下面的代码注释掉，并取消注释 interactive_mode() 那行
    """
    # ---------- 默认模式：直接批量抓取 ----------
    print("=" * 50)
    print("   开始批量抓取中国政府网新闻（第1~10页）")
    print("   解析器：html.parser，每条新闻单独提交，防止唯一约束中断")
    print("=" * 50)

    db_session = SessionLocal()  # 创建数据库会话

    # 循环抓取第1页到第10页
    for page in range(1, 11):
        result = crawl_page(page, db_session)
        if not result:  # 如果某页失败，终止循环
            print("\n[系统] 抓取异常，终止后续")
            break
        # 每抓取一页后，随机休眠2~4秒，避免请求频率过高触发反爬
        if page < 10:
            sleep_time = random.uniform(2, 4)
            print(f"    休眠 {sleep_time:.2f} 秒...")
            time.sleep(sleep_time)

    db_session.close()  # 关闭会话

    print("\n" + "=" * 50)
    print("   抓取流程全部结束！")
    print("   数据库文件：gov_news.db")
    print("=" * 50)

    # 自动导出CSV文件
    export_to_csv()

    # ---------- 交互式菜单模式（如需启用，取消下面注释，并注释掉上面的批量抓取） ----------
    # interactive_mode()