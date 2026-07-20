import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'Fairy111932823',
    'database': 'test7.20',
    'charset': 'utf8mb4'
}

def get_conn():
    return pymysql.connect(**DB_CONFIG)

def insert(content):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO test (test) VALUES (%s)", (content,))
            conn.commit()
            print(f"插入成功，ID: {cur.lastrowid}")
    finally:
        conn.close()

def select_all():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, test FROM test")
            rows = cur.fetchall()
            for row in rows:
                print(f"ID: {row[0]}, 内容: {row[1]}")
            return rows
    finally:
        conn.close()

def update(id, new_content):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            affected = cur.execute("UPDATE test SET test = %s WHERE id = %s", (new_content, id))
            conn.commit()
            print(f"更新了 {affected} 条记录")
    finally:
        conn.close()

def delete(id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            affected = cur.execute("DELETE FROM test WHERE id = %s", (id,))
            conn.commit()
            print(f"删除了 {affected} 条记录")
    finally:
        conn.close()

if __name__ == "__main__":
    insert("第一条测试")
    insert("第二条测试")
    print("查询所有：")
    select_all()
    update(1, "修改后的内容")
    print("更新后查询：")
    select_all()
    delete(2)
    print("删除后查询：")
    select_all()