import streamlit as st
import pandas as pd

# ==========================================
# 系統初始化與架構設定
# ==========================================
st.set_page_config(
    page_title="期末專題",
    page_icon="🌿",
    layout="wide"
)

# 初始化 Session State
if 'cart' not in st.session_state:
    st.session_state.cart = {}

if 'orders' not in st.session_state:
    st.session_state.orders = []

# ---------------------------------------------------------
# 美化區塊 (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 1. 全局字體與設定 */
    h1, h2, h3, h4, span, p, div {
        font-family: 'Helvetica Neue', sans-serif;
    }
    img {
        border-radius: 8px;
    }

    /* 2. 一般按鈕 (維持原樣) */
    .stButton > button {
        background-color: #7D9BA1;
        color: white !important;
        border-radius: 20px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #5D7B81;
        transform: translateY(-2px);
        color: white !important;
    }

    /* ============================================================
       3. [終極修正] 側邊欄購物車佈局
       目標： - 靠最左， + 靠最右，數字居中
    ============================================================ */
    
    /* (A) 移除水平區塊間距 */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"] {
        padding: 0 !important;
        min-width: 0 !important;
    }

    /* (B) 共通按鈕樣式 (去背、字體大) */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--text-color) !important;
        height: 40px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        font-size: 24px !important;
        font-weight: bold !important;
        padding: 0 !important;
        margin: 0 !important;
        padding-top: 3px !important;
    }

    /* (C) [關鍵] 分別指定對齊方向 */
    
    /* 第一欄 (減號) -> 靠左對齊 (Flex-start) */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-of-type(1) .stButton > button {
        justify-content: flex-start !important; /* 靠左 */
    }

    /* 第三欄 (加號) -> 靠右對齊 (Flex-end) */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-of-type(3) .stButton > button {
        justify-content: flex-end !important; /* 靠右 */
    }

    /* Hover 效果 */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button:hover {
        color: #7D9BA1 !important;
        transform: scale(1.2);
    }
    
    /* 其他互動效果 */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button:active {
        color: var(--text-color) !important;
        transform: scale(0.9);
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button:focus {
        outline: none !important;
        box-shadow: none !important;
        color: var(--text-color) !important;
    }

    /* 4. 側邊欄背景設定 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--secondary-background-color); 
        border-radius: 15px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px !important;
    }
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
        border-right: 1px solid rgba(128, 128, 128, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 資料讀取
# ==========================================
def load_data():
    data = [
        {"id": 1, "name": "高階機械鍵盤", "category": "3C周邊", "price": 3500, "image": "https://dlcdnwebimgs.asus.com/gain/848074E4-FB9F-414D-BFCA-70DB410AD363/fwebp"},
        {"id": 2, "name": "電競無線滑鼠", "category": "3C周邊", "price": 1800, "image": "https://blog.shopping.gamania.com/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2F3wl0vtkq%2Fproduction%2Fc27c7cb593c30cb7e67a49a8df41cb3e3d3804ab-1200x720.png&w=3840&q=75"},
        {"id": 3, "name": "降噪耳機", "category": "影音設備", "price": 5200, "image": "https://helios-i.mashable.com/imagery/comparisons/27.fill.size_1200x675.v1751067039.jpg"},
        {"id": 4, "name": "人體工學椅", "category": "辦公家具", "price": 8000, "image": "https://piinterior-net.sfo3.digitaloceanspaces.com/wp-content/uploads/2024/12/scimgFhtCHm.webp"},
        {"id": 5, "name": "Type-C集線器", "category": "3C周邊", "price": 900, "image": "https://i0.wp.com/lpcomment.com/wp-content/uploads/2017/04/%E6%83%85%E5%A2%83%E5%9C%967.jpg?fit=760%2C438&ssl=1"},
        {"id": 6, "name": "4K螢幕", "category": "影音設備", "price": 12000, "image": "https://attach.mobile01.com/attach/202411/mobile01-457221a9759255cc1832ddffa7d8e2f9.jpg"},
        {"id": 7, "name": "音響", "category": "影音設備", "price": 6000, "image": "https://attach.mobile01.com/attach/202411/mobile01-457221a9759255cc1832ddffa7d8e2f9.jpg"},
        {"id": 8, "name": "麥克風", "category": "影音設備", "price": 3000, "image": "https://attach.mobile01.com/attach/202411/mobile01-457221a9759255cc1832ddffa7d8e2f9.jpg"},
    ]
    return pd.DataFrame(data)

def add_to_cart_callback(item):
    item_id = item['id']
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]['quantity'] += 1
        st.toast(f"✅ {item['name']} 數量增加！")
    else:
        new_item = item.to_dict() if isinstance(item, pd.Series) else item
        new_item['quantity'] = 1
        st.session_state.cart[item_id] = new_item
        st.toast(f"✅ 已將 {item['name']} 加入購物車！")

def update_quantity(item_id, change):
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]['quantity'] += change
        if st.session_state.cart[item_id]['quantity'] <= 0:
            del st.session_state.cart[item_id]

def display_products(df):
    st.title("🌿 Shop") 
    st.markdown("---")
    
    categories = ["全部"] + list(df['category'].unique())
    selected_cat = st.radio("分類篩選 (Category)", categories, horizontal=True)
    
    if selected_cat != "全部":
        df = df[df['category'] == selected_cat]

    st.markdown("<br>", unsafe_allow_html=True) 

    cols = st.columns(3)
    for i, (index, row) in enumerate(df.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                st.image(row['image'], use_container_width=True)
                st.subheader(row['name'])
                
                c1, c2 = st.columns([1,1])
                c1.caption(row['category'])
                c2.markdown(f"**NT$ {row['price']:,}**")
                
                st.button(
                    "加入購物車 (Add)", 
                    key=f"add_{row['id']}", 
                    on_click=add_to_cart_callback,
                    args=(row,)
                )

# ==========================================
# 購物車與側邊欄邏輯
# ==========================================
def display_cart():
    st.sidebar.title("🛒 Your Cart")
    st.sidebar.markdown("---")
    
    if not st.session_state.cart:
        st.sidebar.info("購物車目前是空的")
        return

    total_price = 0
    
    for item_id, item in list(st.session_state.cart.items()):
        with st.sidebar.container(border=True):
            st.markdown(f"**{item['name']}**")
            
            # [修改重點] 改為 [1, 2, 1] 比例，讓中間數字寬一點，把按鈕推向兩邊
            c1, c2, c3 = st.columns([1, 6, 1])
            
            with c1:
                st.button("－", key=f"dec_{item_id}", on_click=update_quantity, args=(item_id, -1))
            
            with c2:
                # 數字區塊
                st.markdown(
                    f"""
                    <div style='
                        width: 100%;
                        height: 40px; 
                        display: flex; 
                        justify-content: center; 
                        align-items: center; 
                        font-size: 18px; 
                        font-weight: bold;
                        margin: 0; 
                        padding: 0;'>
                        {item['quantity']}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            with c3:
                st.button("＋", key=f"inc_{item_id}", on_click=update_quantity, args=(item_id, 1))
            
            item_total = item['price'] * item['quantity']
            st.markdown(f"<div style='text-align: right; color: gray; font-size: 0.9em; margin-top: -10px;'>${item_total:,}</div>", unsafe_allow_html=True)
            
            total_price += item_total
    
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"Total: NT$ {total_price:,}")
    
    if st.sidebar.button("🗑️ 清空購物車", use_container_width=True):
        st.session_state.cart = {}
        st.rerun()

# ==========================================
# 結帳與後台
# ==========================================
def checkout_section():
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.cart:
        with st.sidebar.expander("💳 前往結帳 (Checkout)", expanded=True):
            with st.form("checkout_form"):
                name = st.text_input("收件人姓名")
                email = st.text_input("Email")
                address = st.text_input("收件地址")
                submitted = st.form_submit_button("確認下單")
                
                if submitted:
                    if name and address:
                        current_total = sum(item['price'] * item['quantity'] for item in st.session_state.cart.values())
                        total_items = sum(item['quantity'] for item in st.session_state.cart.values())
                        
                        order_info = {
                            "Name": name,
                            "Email": email,
                            "Total": current_total,
                            "Items_Count": total_items,
                            "Order_Details": str([f"{v['name']} x{v['quantity']}" for v in st.session_state.cart.values()])
                        }
                        st.session_state.orders.append(order_info)
                        st.session_state.cart = {}
                        st.success("🎉 訂單已送出！")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("請填寫完整資訊")

def admin_view():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    if st.checkbox("🔧 管理員後台 (Admin View)"):
        st.subheader("📦 訂單紀錄")
        if st.session_state.orders:
            order_df = pd.DataFrame(st.session_state.orders)
            st.dataframe(order_df, use_container_width=True)
        else:
            st.info("目前尚無訂單")

def main():
    df = load_data()
    display_cart()
    checkout_section()
    
    if not df.empty:
        display_products(df)
    
    admin_view()

if __name__ == "__main__":
    main()