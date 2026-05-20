import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sqlite3

# ====================== 密码保护 ======================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.title("🛏️ 床垫工厂交付管理系统")
        st.markdown("**请输入密码登录**")
        password = st.text_input("输入密码", type="password", key="pwd")
        if st.button("登录"):
            if password == "BedFactory2026":   # ←←← 这里改成你自己的密码
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("密码错误！")
        st.stop()

check_password()

# ====================== 主界面 ======================
st.set_page_config(page_title="床垫交付管理系统", layout="wide", page_icon="🛏️")
st.title("🛏️ 床垫工厂零售交付管理系统")
st.caption("已启用密码保护")

# 数据库
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT,
        customer_name TEXT,
        phone TEXT,
        region TEXT,
        community TEXT,
        product_model TEXT,
        quantity INTEGER,
        amount REAL,
        expected_delivery TEXT,
        status TEXT DEFAULT '未打包',
        contract_url TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def get_conn():
    return sqlite3.connect('orders.db')

def load_orders():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY expected_delivery ASC, id DESC", conn)
    conn.close()
    return df

# 自动标记超期
def auto_update_overdue():
    conn = get_conn()
    today = date.today().isoformat()
    c = conn.cursor()
    c.execute("UPDATE orders SET status = '超期' WHERE expected_delivery < ? AND status NOT IN ('已完成', '超期')", (today,))
    conn.commit()
    conn.close()

auto_update_overdue()

menu = st.sidebar.selectbox("功能菜单", ["🏠 首页", "📋 全部订单", "➕ 新建订单", "📸 合同上传"])

# 首页
if menu == "🏠 首页":
    df = load_orders()
    today = date.today()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("今日待打包", len(df[df['status'] == '未打包']))
    with col2:
        st.metric("待送货", len(df[df['expected_delivery'] == str(today)]))
    with col3:
        st.metric("超期订单", len(df[df['status'] == '超期']))
    with col4:
        st.metric("未完成订单", len(df[~df['status'].isin(['已完成'])]))

    st.subheader("即将交付客户")
    st.dataframe(df.head(10), use_container_width=True)

# 其他页面简化版（先跑起来）
elif menu == "📋 全部订单":
    df = load_orders()
    st.dataframe(df, use_container_width=True)

elif menu == "➕ 新建订单":
    st.info("新建订单功能开发中...")

elif menu == "📸 合同上传":
    st.info("合同上传功能开发中...")

st.caption("系统 v1.3 | 如需修改密码，请联系我")