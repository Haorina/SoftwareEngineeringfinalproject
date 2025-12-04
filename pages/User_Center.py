# pages/2_User_Center.py
import streamlit as st
import sys
import os

# [重要] 將上一層目錄加入系統路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_user_orders

st.set_page_config(page_title="會員中心", page_icon="👤")

st.title("📦 我的訂單記錄")
st.markdown("---")

current_user = st.session_state.get('current_user')

if not current_user:
    st.warning("🔒 請先在首頁側邊欄 **登入** 才能查看訂單。")
    st.markdown("前往 **Home** 頁面進行登入。")
else:
    st.success(f"👋 歡迎回來，**{current_user}**")
    
    # 讀取該使用者的訂單
    df = get_user_orders(current_user)
    
    if not df.empty:
        st.markdown(f"您共有 **{len(df)}** 筆訂單：")
        for i, row in df.iterrows():
            # 狀態顏色
            status_map = {
                "已完成": "🟢",
                "已出貨": "🚚",
                "處理中": "⏳",
                "取消": "🔴"
            }
            icon = status_map.get(row['status'], "📦")
            
            with st.expander(f"{icon} {row['order_date']} - 總金額: ${row['total_amount']:,}"):
                st.write(f"**商品內容：** {row['items_summary']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**訂單狀態：** {row['status']}")
                    if 'discount' in row and row['discount'] > 0:
                        st.caption(f"(含折扣: -${row['discount']:,})")
                with c2:
                    st.write(f"**收件資訊：** {row['customer_name']}")
                    st.caption(row['customer_address'])
    else:
        st.info("🛒 您目前還沒有購買紀錄，快去首頁逛逛吧！")