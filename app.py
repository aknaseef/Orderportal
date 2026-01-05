import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- CONFIGURATION LOADER ---
# This function tries to load settings from an external file.
# If the file is missing, it uses safe "Demo" defaults.
def load_config():
    config_path = 'config.json'
    defaults = {
        "app_name": "Open Source Pharmacy Portal",
        "admin_password": "admin",
        "stock_file": "stock.csv",
        "orders_file": "orders.csv",
        "currency": "AED",
        "branches": {
            "Demo Branch": "0000"
        }
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception:
            st.error("Error reading config.json. Using defaults.")
            return defaults
    else:
        # If running on GitHub for the first time without a config, show warning
        return defaults

config = load_config()

# --- CONSTANTS ---
APP_TITLE = config.get("app_name", "Pharmacy Portal")
ADMIN_PASS = config.get("admin_password", "admin")
STOCK_FILE = config.get("stock_file", "stock.csv")
ORDERS_FILE = config.get("orders_file", "orders.csv")
BRANCH_CREDENTIALS = config.get("branches", {})

st.set_page_config(page_title=APP_TITLE, layout="wide", page_icon="💊")

# --- HELPER FUNCTIONS ---
def save_order(branch_name, order_data):
    order_data['Branch'] = branch_name
    order_data['Order Time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cols = ['Branch', 'Order Time', 'Product Name', 'Expiry', 'Order Qty']
    
    # Ensure all columns exist
    for c in cols:
        if c not in order_data.columns: order_data[c] = ''
    
    # Select only relevant columns
    final_data = order_data[cols]
    
    if not os.path.exists(ORDERS_FILE):
        final_data.to_csv(ORDERS_FILE, index=False)
    else:
        final_data.to_csv(ORDERS_FILE, mode='a', header=False, index=False)

# --- SIDEBAR ---
st.sidebar.title(APP_TITLE)
app_mode = st.sidebar.radio("Menu", ["Branch Order", "Admin Panel"])
st.sidebar.divider()

# Show warning if using default config (Safety Feature)
if "Demo Branch" in BRANCH_CREDENTIALS:
    st.sidebar.warning("⚠️ Running in Demo Mode. Please create config.json to add real branches.")

# --- PAGE 1: BRANCH ORDERING ---
if app_mode == "Branch Order":
    st.title("🛒 New Stock Request")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_branch = st.selectbox("Select Branch", list(BRANCH_CREDENTIALS.keys()))
    with col2:
        pin = st.text_input("Enter PIN", type="password")

    # Verify PIN
    if pin == BRANCH_CREDENTIALS.get(selected_branch):
        st.success(f"Logged in: **{selected_branch}**")
        st.divider()
        
        if os.path.exists(STOCK_FILE):
            try:
                df = pd.read_csv(STOCK_FILE)
                if 'Order Qty' not in df.columns: df['Order Qty'] = 0
                
                # Search Bar
                search_term = st.text_input("🔍 Search Item", placeholder="Type name or expiry year...")
                
                if search_term:
                    # Smart search across all text columns
                    mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                    df_display = df[mask].copy()
                else:
                    df_display = df.copy()

                # Ordering Grid
                edited_df = st.data_editor(
                    df_display,
                    column_config={
                        "Order Qty": st.column_config.NumberColumn(min_value=0, step=1, required=True)
                    },
                    disabled=[c for c in df.columns if c != 'Order Qty'], # Lock everything else
                    hide_index=True,
                    use_container_width=True,
                    key="order_grid"
                )

                if st.button("Submit Order", type="primary", use_container_width=True):
                    orders = edited_df[edited_df['Order Qty'] > 0]
                    if not orders.empty:
                        save_order(selected_branch, orders)
                        st.balloons()
                        st.success(f"✅ Order submitted for {len(orders)} items!")
                    else:
                        st.warning("⚠️ No quantities entered.")
            except Exception as e:
                st.error(f"Error reading stock file: {e}")
        else:
            st.info("👋 Waiting for Admin to upload today's stock list.")
    elif pin:
        st.error("❌ Incorrect PIN")

# --- PAGE 2: ADMIN PANEL ---
elif app_mode == "Admin Panel":
    st.title("🔧 Admin Dashboard")
    password = st.text_input("Admin Password", type="password")
    
    if password == ADMIN_PASS: 
        st.divider()
        st.subheader("1. Import Stock List")
        st.write("Upload any Excel or CSV export from your POS.")
        
        uploaded_file = st.file_uploader("Drag & Drop File", type=['xlsx', 'csv', 'xls'])
        
        if uploaded_file:
            try:
                # Load file
                if uploaded_file.name.endswith('.csv'):
                    raw_df = pd.read_csv(uploaded_file)
                else:
                    raw_df = pd.read_excel(uploaded_file)
                
                st.write("### Map Columns")
                cols = list(raw_df.columns)
                
                # Auto-matcher helper
                def get_idx(options, keys):
                    for i, o in enumerate(options):
                        if any(k in o.lower() for k in keys): return i
                    return 0

                c1, c2, c3 = st.columns(3)
                with c1: name_col = st.selectbox("Product Name Column", cols, index=get_idx(cols, ['name','desc','item','prod']))
                with c2: exp_col = st.selectbox("Expiry Date Column", cols, index=get_idx(cols, ['exp','date','validity']))
                with c3: qty_col = st.selectbox("Quantity Column", cols, index=get_idx(cols, ['qty','stk','bal','hand']))
                
                if st.button("Save & Update Stock"):
                    clean_stock = pd.DataFrame({
                        "Product Name": raw_df[name_col],
                        "Expiry": raw_df[exp_col],
                        "Available Qty": raw_df[qty_col],
                        "Order Qty": 0
                    })
                    clean_stock.to_csv(STOCK_FILE, index=False)
                    st.success(f"✅ Success! Updated {len(clean_stock)} items.")
            except Exception as e:
                st.error(f"Error processing file: {e}")

        st.divider()
        st.subheader("2. Download Orders")
        if os.path.exists(ORDERS_FILE):
            orders_df = pd.read_csv(ORDERS_FILE)
            st.dataframe(orders_df, use_container_width=True)
            
            csv = orders_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "consolidated_orders.csv", "text/csv")
            
            if st.button("🗑️ Clear Order History"):
                os.remove(ORDERS_FILE)
                st.rerun()
        else:
            st.info("No orders received yet.")
