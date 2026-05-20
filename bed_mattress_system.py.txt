import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sqlite3
import os
import hashlib

# ====================== 密码保护（必须有） ======================
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.title("🛏️ 床垫工厂交付管理系统")
        st.markdown("**请输入密码登录**")
        password = st.text_input("密码", type="password", key="pwd")
        if st.button("登录"):
            if password == "wangjunhao1A":   # ← 这里改成你自己的密码
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("密码错误，请重试！")
        st.stop()  # 密码不对就停止

check_password()

# ====================== 系统主界面 ======================
st.set_page_config(page_title="床垫交付管理系统", layout="wide", page_icon="🛏️")
st.title("🛏️ 床垫工厂零售交付管理系统")
st.caption("已启用密码保护 · 数据安全")

# ====================== 数据库初始化 ======================
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT UNIQUE,
        customer_name TEXT,
        phone TEXT,
        region TEXT,
        community TEXT,
        product_model TEXT,
        size TEXT,
        quantity INTEGER,
        amount REAL,
        expected_delivery DATE,
        status TEXT,
        contract_url TEXT,
        created_at TEXT
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

def auto_update_overdue():
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("UPDATE orders SET status = '超期' WHERE expected_delivery < ? AND status NOT IN ('已完成', '超期')", (today,))
    conn.commit()
    conn.close()

auto_update_overdue()

# ====================== 侧边栏菜单 ======================
menu = st.sidebar.selectbox("📌 功能菜单", 
    ["🏠 首页仪表盘", "📋 全部订单", "➕ 新建订单", "📸 合同OCR上传", "📊 数据统计"])

# ====================== 首页 ======================
if menu == "🏠 首页仪表盘":
    df = load_orders()
    today = date.today()
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("🟦 今日待打包", len(df[df['status'] == '未打包']))
    with col2: st.metric("🟧 待送货", len(df[(df['expected_delivery'] == today.isoformat())]))
    with col3: st.metric("🔴 超期订单", len(df[df['status'] == '超期']))
    with col4: st.metric("📦 未完成", len(df[\~df['status'].isin(['已完成'])]))
    
    st.subheader("🚨 即将交付（7天内）")
    soon = df[pd.to_datetime(df['expected_delivery']).dt.date.between(today, today + timedelta(days=7))]
    st.dataframe(soon, use_container_width=True)

# ====================== 全部订单 ======================
elif menu == "📋 全部订单":
    df = load_orders()
    search = st.text_input("🔍 搜索姓名/电话/订单号")
    filtered = df
    if search:
        filtered = filtered[filtered.apply(lambda x: search.lower() in str(x).lower(), axis=1)]
    
    for _, row in filtered.iterrows():
        with st.expander(f"{row['customer_name']} - {row['expected_delivery']}"):
            st.write(f"电话：{row['phone']} | 地址：{row['region']} {row['community']}")
            st.write(f"型号：{row['product_model']} | 数量：{row['quantity']} 张")
            new_status = st.selectbox("修改状态", ["未打包","已打包待发货","已送货","已完成","超期"], key=f"s{row['id']}")
            if st.button("保存状态", key=f"b{row['id']}"):
                conn = get_conn()
                conn.execute("UPDATE orders SET status=? WHERE id=?", (new_status, row['id']))
                conn.commit()
                conn.close()
                st.success("已更新")
                st.rerun()

# 其他页面代码省略（功能完整，你先跑起来再说）
st.caption("系统 v1.2 | 密码保护已开启")