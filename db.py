import sqlite3
from datetime import datetime

DB_NAME = "mercadinho.db"

def now():
    return datetime.now().isoformat(timespec="seconds")

class DB:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_NAME
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON;")

    def close(self):
        self.conn.close()

    def exec(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def one(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        return cur.fetchone()

    def all(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        return cur.fetchall()

    def init_schema(self):
        self.exec("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY,
          username TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """)

        self.exec("""
        CREATE TABLE IF NOT EXISTS customers (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          phone TEXT,
          created_at TEXT NOT NULL
        );
        """)

        self.exec("""
        CREATE TABLE IF NOT EXISTS products (
          id INTEGER PRIMARY KEY,
          sku TEXT UNIQUE,
          name TEXT NOT NULL,
          cost REAL NOT NULL DEFAULT 0,
          price REAL NOT NULL DEFAULT 0,
          stock INTEGER NOT NULL DEFAULT 0,
          min_stock INTEGER NOT NULL DEFAULT 0,
          active INTEGER NOT NULL DEFAULT 1
        );
        """)

        self.exec("""
        CREATE TABLE IF NOT EXISTS stock_movements (
          id INTEGER PRIMARY KEY,
          product_id INTEGER NOT NULL,
          type TEXT NOT NULL CHECK(type IN ('IN','OUT')),
          qty INTEGER NOT NULL,
          unit_cost REAL,
          reason TEXT NOT NULL, -- PURCHASE, SALE, TAB, ADJUST
          ref_table TEXT,
          ref_id INTEGER,
          note TEXT,
          created_at TEXT NOT NULL,
          FOREIGN KEY(product_id) REFERENCES products(id)
        );
        """)

        self.exec("""
        CREATE TABLE IF NOT EXISTS tabs (
          id INTEGER PRIMARY KEY,
          customer_id INTEGER NOT NULL,
          status TEXT NOT NULL CHECK(status IN ('OPEN','CLOSED')),
          opened_at TEXT NOT NULL,
          closed_at TEXT,
          FOREIGN KEY(customer_id) REFERENCES customers(id)
        );
        """)

        self.exec("""
        CREATE TABLE IF NOT EXISTS tab_items (
          id INTEGER PRIMARY KEY,
          tab_id INTEGER NOT NULL,
          product_id INTEGER NOT NULL,
          qty INTEGER NOT NULL,
          unit_price REAL NOT NULL,
          created_at TEXT NOT NULL,
          FOREIGN KEY(tab_id) REFERENCES tabs(id),
          FOREIGN KEY(product_id) REFERENCES products(id)
        );
        """)

        self.exec("""
        CREATE TABLE IF NOT EXISTS sales (
          id INTEGER PRIMARY KEY,
          total REAL NOT NULL,
          discount REAL NOT NULL DEFAULT 0,
          payment_method TEXT,
          created_at TEXT NOT NULL
        );
        """)

        self.exec("""
        CREATE TABLE IF NOT EXISTS sale_items (
          id INTEGER PRIMARY KEY,
          sale_id INTEGER NOT NULL,
          product_id INTEGER NOT NULL,
          qty INTEGER NOT NULL,
          unit_price REAL NOT NULL,
          unit_cost REAL NOT NULL,
          FOREIGN KEY(sale_id) REFERENCES sales(id),
          FOREIGN KEY(product_id) REFERENCES products(id)
        );
        """)

        self.exec("""
        CREATE TABLE IF NOT EXISTS cash_movements (
          id INTEGER PRIMARY KEY,
          type TEXT NOT NULL CHECK(type IN ('IN','OUT')),
          category TEXT NOT NULL, -- SALE, TAB_PAYMENT, PURCHASE, WITHDRAW, OTHER
          amount REAL NOT NULL,
          note TEXT,
          created_at TEXT NOT NULL
        );
        """)

    # ====== Users ======
    def has_any_user(self):
        row = self.one("SELECT COUNT(*) AS c FROM users;")
        return row["c"] > 0

    def create_user(self, username, password_hash):
        self.exec(
            "INSERT INTO users(username, password_hash, created_at) VALUES(?,?,?);",
            (username, password_hash, now())
        )

    def get_user_by_username(self, username):
        return self.one("SELECT * FROM users WHERE username=?;", (username,))

    # ====== Products ======
    def search_products(self, q=""):
        q = (q or "").strip()
        if not q:
            return self.all("SELECT * FROM products WHERE active=1 ORDER BY name;")
        like = f"%{q}%"
        return self.all("""
            SELECT * FROM products
            WHERE active=1 AND (name LIKE ? OR sku LIKE ?)
            ORDER BY name;
        """, (like, like))

    def create_product(self, sku, name, cost, price, stock, min_stock):
        self.exec("""
          INSERT INTO products(sku, name, cost, price, stock, min_stock)
          VALUES(?,?,?,?,?,?);
        """, (sku or None, name, cost, price, stock, min_stock))

    def update_stock(self, product_id, delta):
        self.exec("UPDATE products SET stock = stock + ? WHERE id=?;", (delta, product_id))

    def add_stock_movement(self, product_id, mtype, qty, unit_cost, reason, ref_table=None, ref_id=None, note=None):
        self.exec("""
          INSERT INTO stock_movements(product_id,type,qty,unit_cost,reason,ref_table,ref_id,note,created_at)
          VALUES(?,?,?,?,?,?,?,?,?);
        """, (product_id, mtype, qty, unit_cost, reason, ref_table, ref_id, note, now()))

    # ====== Customers / Tabs ======
    def create_customer(self, name, phone=None):
        self.exec("INSERT INTO customers(name, phone, created_at) VALUES(?,?,?);", (name, phone, now()))

    def search_customers(self, q=""):
        q = (q or "").strip()
        if not q:
            return self.all("SELECT * FROM customers ORDER BY name;")
        like = f"%{q}%"
        return self.all("SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name;", (like, like))

    def get_open_tab(self, customer_id):
        return self.one("SELECT * FROM tabs WHERE customer_id=? AND status='OPEN';", (customer_id,))

    def open_tab(self, customer_id):
        self.exec("INSERT INTO tabs(customer_id,status,opened_at) VALUES(?,?,?);", (customer_id, "OPEN", now()))
        return self.one("SELECT * FROM tabs WHERE rowid = last_insert_rowid();")

    def add_tab_item(self, tab_id, product_id, qty, unit_price):
        self.exec("""
          INSERT INTO tab_items(tab_id,product_id,qty,unit_price,created_at)
          VALUES(?,?,?,?,?);
        """, (tab_id, product_id, qty, unit_price, now()))

    def tab_total(self, tab_id):
        row = self.one("SELECT COALESCE(SUM(qty * unit_price),0) AS t FROM tab_items WHERE tab_id=?;", (tab_id,))
        return float(row["t"])

    def tab_items(self, tab_id):
        return self.all("""
          SELECT ti.*, p.name AS product_name
          FROM tab_items ti
          JOIN products p ON p.id = ti.product_id
          WHERE ti.tab_id=?
          ORDER BY ti.id DESC;
        """, (tab_id,))

    def close_tab(self, tab_id):
        self.exec("UPDATE tabs SET status='CLOSED', closed_at=? WHERE id=?;", (now(), tab_id))

    # ====== Sales / Cash ======
    def create_sale(self, total, discount, method):
        self.exec("INSERT INTO sales(total,discount,payment_method,created_at) VALUES(?,?,?,?);",
                  (total, discount, method, now()))
        return self.one("SELECT * FROM sales WHERE rowid=last_insert_rowid();")

    def add_sale_item(self, sale_id, product_id, qty, unit_price, unit_cost):
        self.exec("""
          INSERT INTO sale_items(sale_id,product_id,qty,unit_price,unit_cost)
          VALUES(?,?,?,?,?);
        """, (sale_id, product_id, qty, unit_price, unit_cost))

    def cash_in(self, category, amount, note=None):
        self.exec("""
          INSERT INTO cash_movements(type,category,amount,note,created_at)
          VALUES('IN',?,?,?,?);
        """, (category, amount, note, now()))

    def cash_out(self, category, amount, note=None):
        self.exec("""
          INSERT INTO cash_movements(type,category,amount,note,created_at)
          VALUES('OUT',?,?,?,?);
        """, (category, amount, note, now()))

    def cash_balance(self):
        row = self.one("""
          SELECT
            COALESCE(SUM(CASE WHEN type='IN' THEN amount ELSE 0 END),0) -
            COALESCE(SUM(CASE WHEN type='OUT' THEN amount ELSE 0 END),0) AS b
          FROM cash_movements;
        """)
        return float(row["b"])