# database.py
import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "shop.db"

# ==========================================
# 資料庫初始化
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. 使用者資料表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            email TEXT,
            real_name TEXT,
            address TEXT
        )
    ''')
    
    # 2. 訂單資料表 (已新增 original_amount, discount)
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT, username TEXT, customer_name TEXT,
            customer_email TEXT, customer_address TEXT,
            total_amount INTEGER, 
            original_amount INTEGER,  -- 新增：原始金額
            discount INTEGER,         -- 新增：折扣金額
            items_summary TEXT, status TEXT
        )
    ''')

    # 3. 商品資料表
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            price INTEGER,
            image TEXT
        )
    ''')

    # 4. 檢查商品表是否為空，如果是空的就寫入預設資料 (初始化)
    c.execute('SELECT count(*) FROM products')
    if c.fetchone()[0] == 0:
        initial_products = [
            (1, "高階機械鍵盤", "3C周邊", 3500, "https://dlcdnwebimgs.asus.com/gain/848074E4-FB9F-414D-BFCA-70DB410AD363/fwebp"),
            (2, "電競無線滑鼠", "3C周邊", 1800, "https://blog.shopping.gamania.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F3wl0vtkq%2Fproduction%2Fc27c7cb593c30cb7e67a49a8df41cb3e3d3804ab-1200x720.png&w=3840&q=75"),
            (3, "降噪耳機", "影音設備", 5200, "https://helios-i.mashable.com/imagery/comparisons/27.fill.size_1200x675.v1751067039.jpg"),
            (4, "人體工學椅", "辦公家具", 8000, "https://piinterior-net.sfo3.digitaloceanspaces.com/wp-content/uploads/2024/12/scimgFhtCHm.webp"),
            (5, "Type-C集線器", "3C周邊", 900, "https://i0.wp.com/lpcomment.com/wp-content/uploads/2017/04/%E6%83%85%E5%A2%83%E5%9C%967.jpg?fit=760%2C438&ssl=1"),
            (6, "4K螢幕", "影音設備", 12000, "https://attach.mobile01.com/attach/202411/mobile01-457221a9759255cc1832ddffa7d8e2f9.jpg"),
            (7, "音響", "影音設備", 6000, "https://attach.mobile01.com/attach/202411/mobile01-457221a9759255cc1832ddffa7d8e2f9.jpg"),
            (8, "麥克風", "影音設備", 3000, "https://attach.mobile01.com/attach/202411/mobile01-457221a9759255cc1832ddffa7d8e2f9.jpg"),
            (9, "派大星", "玩具", 300, "https://images.seeklogo.com/logo-png/32/1/patrick-star-logo-png_seeklogo-320105.png"),
        ]
        c.executemany('INSERT INTO products (id, name, category, price, image) VALUES (?,?,?,?,?)', initial_products)
        print("初始化商品資料成功！")

    conn.commit()
    conn.close()

# ==========================================
# 使用者相關功能
# ==========================================
def register_user(username, password, email, real_name, address):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', 
                  (username, password, email, real_name, address))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def check_login(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def get_user_info(username):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM users WHERE username = ?", conn, params=(username,))
    conn.close()
    if not df.empty:
        return df.iloc[0].to_dict()
    return None

# ==========================================
# 商品讀取與管理功能
# ==========================================
def get_all_products():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return df

def add_new_product(name, category, price, image_url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO products (name, category, price, image) VALUES (?, ?, ?, ?)', 
                  (name, category, price, image_url))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        conn.close()

# ==========================================
# 訂單相關功能 (更新版)
# ==========================================
def save_order_to_db(username, name, email, address, total, original, discount, items):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 這裡的欄位順序要跟 INSERT 對應
    c.execute('''INSERT INTO orders (order_date, username, customer_name, customer_email, 
                 customer_address, total_amount, original_amount, discount, items_summary, status) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (date, username, name, email, address, total, original, discount, items, "處理中"))
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    conn.close()
    return df

def get_user_orders(username):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM orders WHERE username = ? ORDER BY id DESC", conn, params=(username,))
    conn.close()
    return df

def update_order_status(order_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()