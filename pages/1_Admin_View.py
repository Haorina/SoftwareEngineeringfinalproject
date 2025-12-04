# pages/1_Admin_View.py
import streamlit as st
import pandas as pd
import sys
import os

# 將上一層目錄加入系統路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_all_orders, update_order_status, add_new_product

st.set_page_config(page_title="管理員後台", page_icon="🔧", layout="wide")

# CSS 美化 (維持 Dark Mode 修復版)
st.markdown("""
<style>
    div[data-testid="stMetricValue"] { font-size: 24px; }
</style>
""", unsafe_allow_html=True)

# 初始化管理員登入狀態
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ==========================================
# 登入介面 (獨立於會員系統)
# ==========================================
def login_section():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("🔐 管理員後台登入")
        with st.container(border=True):
            # 👇 已移除「預設帳號密碼」的提示訊息
            account = st.text_input("管理員帳號", key="admin_user")
            password = st.text_input("密碼", type="password", key="admin_pwd")
            
            if st.button("登入後台", use_container_width=True):
                if account == "admin" and password == "1234":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ 帳號密碼錯誤")

# ==========================================
# 後台主功能
# ==========================================
def admin_dashboard():
    # 側邊欄顯示狀態
    with st.sidebar:
        st.success("✅ 管理員已登入")
        if st.button("登出後台"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
    st.title("🔧 營運管理儀表板")
    
    # 讀取訂單資料
    df_orders = get_all_orders()

    # 使用 Tabs 分頁管理不同功能
    tab1, tab2, tab3 = st.tabs(["📊 數據分析 (Dashboard)", "📋 訂單管理 (Orders)", "➕ 商品上架 (Product)"])
    
    # --- Tab 1: 數據分析 (BI Dashboard) ---
    with tab1:
        st.subheader("營運數據總覽")
        if df_orders.empty:
            st.info("目前沒有數據可分析")
        else:
            # 資料前處理
            df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])

            # 1. 關鍵指標 (KPIs)
            total_rev = df_orders['total_amount'].sum()
            total_orders = len(df_orders)
            avg_order = total_rev / total_orders if total_orders > 0 else 0
            
            k1, k2, k3 = st.columns(3)
            k1.metric("💰 總營收 (Revenue)", f"NT$ {total_rev:,}")
            k2.metric("📦 總訂單數 (Orders)", f"{total_orders} 筆")
            k3.metric("📈 平均客單價 (AOV)", f"NT$ {int(avg_order):,}")
            
            st.markdown("---")
            
            # 2. 圖表分析
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### 📅 每日營收趨勢")
                daily_revenue = df_orders.groupby(df_orders['order_date'].dt.date)['total_amount'].sum()
                st.line_chart(daily_revenue)
            with c2:
                st.markdown("##### 📦 訂單狀態分佈")
                status_counts = df_orders['status'].value_counts()
                st.bar_chart(status_counts)

    # --- Tab 2: 訂單管理 ---
    with tab2:
        st.subheader("詳細訂單列表")
        
        if df_orders.empty:
            st.info("目前沒有任何訂單")
        else:
            for index, row in df_orders.iterrows():
                status_icon = "🟢" if row['status'] == "已完成" else "🚚" if row['status'] == "已出貨" else "⏳"
                
                with st.expander(f"{status_icon} 訂單 #{row['id']} - {row['customer_name']} (實付: ${row['total_amount']:,})"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**購買帳號：** {row['username']}")
                        st.markdown(f"**商品內容：** {row['items_summary']}")
                        st.markdown(f"**配送地址：** {row['customer_address']}")
                        st.caption(f"下單時間：{row['order_date']}")
                        
                        if 'discount' in row and row['discount'] > 0:
                            st.info(f"💰 原始金額: ${row['original_amount']:,} | 🏷️ 折扣: -${row['discount']:,}")
                    
                    with col2:
                        current_status = row['status']
                        opts = ["處理中", "已出貨", "已完成", "取消"]
                        idx = opts.index(current_status) if current_status in opts else 0
                        
                        new_status = st.selectbox("更新狀態", opts, index=idx, key=f"s_{row['id']}")
                        if st.button("更新狀態", key=f"upd_{row['id']}"):
                            update_order_status(row['id'], new_status)
                            st.toast("✅ 狀態已更新！")
                            st.rerun()

    # --- Tab 3: 商品上架 ---
    with tab3:
        st.subheader("新增上架商品")
        with st.container(border=True):
            with st.form("add_product_form"):
                name = st.text_input("商品名稱")
                category = st.selectbox("分類", ["3C周邊", "影音設備", "辦公家具", "玩具", "其他"])
                
                c1, c2 = st.columns(2)
                with c1: price = st.number_input("價格", min_value=1, step=100)
                with c2: image = st.text_input("圖片網址", placeholder="https://...")

                submitted = st.form_submit_button("確認上架")
                
                if submitted:
                    if name and price and image:
                        if add_new_product(name, category, int(price), image):
                            st.success(f"✅ 已成功上架：{name}")
                        else:
                            st.error("上架失敗")
                    else:
                        st.warning("⚠️ 請填寫完整資訊")

# ==========================================
# 頁面邏輯入口
# ==========================================
if not st.session_state.admin_logged_in:
    login_section()
else:
    admin_dashboard()