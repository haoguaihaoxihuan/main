import pymysql

# 数据库连接配置（请根据实际情况修改）
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Fairy111932823',
    'database': 'test7.20',
    'charset': 'utf8mb4'
}

# 建表 SQL
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS test (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '测试ID',
    test VARCHAR(50) NOT NULL COMMENT '测试内容'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试表';
"""

def create_table():
    connection = None
    try:
        # 连接
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TABLE_SQL)
            connection.commit()
            print("数据表 'test' 创建成功")
    except pymysql.MySQLError as e:
        print(f"数据库错误: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    create_table()