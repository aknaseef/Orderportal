import streamlit as st
import pandas as pd
import os
import json
import io
from datetime import datetime

# --- CONFIGURATION LOADER ---
def load_config():
    config_path = 'config.json'
    defaults = {
        "app_name": "Pharmacy Portal V2",
        "admin_password": "admin",
        "stock_file": "stock.csv",
        "orders_file": "orders.csv",
        "branches": {"Demo Branch": "0000"}
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f: return json.load(f)
        except: return defaults
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
    
    # Ensure columns match standard format
    cols = ['Branch', 'Order Time', 'Product Name', 'Expiry', 'Available Qty', 'Order Qty', 'Type']
    for c in cols:
        if c not in order_data.columns: order_data[c] = ''
            
    final_data = order_data[cols]
    
    if not os.path.exists(ORDERS_FILE):
        final_data.to_csv(ORDERS_FILE, index=False)
    else:
        final_data.to_csv(ORDERS_FILE, mode='a', header=False, index=False)

# --- SIDEBAR ---
st.sidebar.title(APP_TITLE)
app_mode = st.sidebar.radio("Menu", ["Branch Order", "Admin Panel"])
st.sidebar.divider()

if "Demo Branch" in BRANCH_CREDENTIALS:
    st.sidebar.warning("⚠️ Running in Demo Mode.")

# --- PAGE 1: BRANCH ORDERING ---
if app_mode == "Branch Order":
    st.title("🛒 Stock Request")
    
    if "Demo Branch" in BRANCH_CREDENTIALS:
        st.info("ℹ️ **Demo Access:** Select 'Demo Branch' -> PIN: `0000`")

    col1, col2 = st.columns([1, 1])
    with col1:
        selected_branch = st.selectbox("Select Branch", list(BRANCH_CREDENTIALS.keys()))
    with col2:
        pin = st.text_input("Enter PIN", type="password")

    if pin == BRANCH_CREDENTIALS.get(selected_branch):
        st.success(f"Logged in: **{selected_branch}**")
        
        # --- TAB SELECTION FOR TYPES OF ORDERS ---
        tab1, tab2 = st.tabs(["📋 Standard Stock", "🆕 Request New Item"])

        # --- TAB 1: EXISTING STOCK ---
        with tab1:
            if os.path.exists(STOCK_FILE):
                try:
                    df = pd.read_csv(STOCK_FILE)
                    # Clean data to ensure numbers are numbers
                    if 'Available Qty' in df.columns:
                        df['Available Qty'] = pd.to_numeric(df['Available Qty'], errors='coerce').fillna(0)
                    if 'Order Qty' not in df.columns: df['Order Qty'] = 0
                    
                    search_term = st.text_input("🔍 Search Stock", placeholder="Type name...")
                    if search_term:
                        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                        df_display = df[mask].copy()
                    else:
                        df_display = df.copy()

                    edited_df = st.data_editor(
                        df_display,
                        column_config={
                            "Order Qty": st.column_config.NumberColumn(min_value=0, step=1),
                            "Available Qty": st.column_config.NumberColumn(disabled=True)
                        },
                        disabled=[c for c in df.columns if c != 'Order Qty'],
                        hide_index=True,
                        use_container_width=True,
                        key="order_grid"
                    )

                    if st.button("Submit Standard Order", type="primary"):
                        orders = edited_df[edited_df['Order Qty'] > 0].copy()
                        
                        # VALIDATION: Check if Order > Available
                        over_ordered = orders[orders['Order Qty'] > orders['Available Qty']]
                        
                        if not over_ordered.empty:
                            st.error("🛑 Error: You ordered more than available for these items:")
                            st.dataframe(over_ordered[['Product Name', 'Available Qty', 'Order Qty']])
                        elif not orders.empty:
                            orders['Type'] = 'Stock'
                            save_order(selected_branch, orders)
                            st.balloons()
                            st.success("✅ Order Sent!")
                        else:
                            st.warning("⚠️ Cart is empty.")
                except Exception as e:
                    st.error(f"Error reading stock: {e}")
            else:
                st.info("Waiting for Admin stock upload.")

        # --- TAB 2: SPECIAL REQUESTS ---
        with tab2:
            st.write("Item not in the list? Request it here.")
            with st.form("special_request_form"):
                new_item = st.text_input("Product Name (e.g., New Panadol 500mg)")
                new_qty = st.number_input("Quantity Needed", min_value=1, step=1)
                submitted = st.form_submit_button("Request Special Item")
                
                if submitted and new_item:
                    # Create a mini dataframe for this custom item
                    special_order = pd.DataFrame([{
                        "Product Name": new_item,
                        "Expiry": "New Request",
                        "Available Qty": 0,
                        "Order Qty": new_qty,
                        "Type": "Special Request"
                    }])
                    save_order(selected_branch, special_order)
                    st.success(f"✅ Request for '{new_item}' sent!")

    elif pin:
        st.error("❌ Incorrect PIN")

# --- PAGE 2: ADMIN PANEL ---
elif app_mode == "Admin Panel":
    st.title("🔧 Admin Dashboard")
    password = st.text_input("Admin Password", type="password")
    
    if password == ADMIN_PASS: 
        st.divider()
        st.subheader("1. Update Stock")
        uploaded_file = st.file_uploader("Upload Excel/CSV", type=['xlsx', 'csv'])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'): raw_df = pd.read_csv(uploaded_file)
                else: raw_df = pd.read_excel(uploaded_file)
                
                cols = list(raw_df.columns)
                c1, c2, c3 = st.columns(3)
                with c1: name_col = st.selectbox("Name Column", cols)
                with c2: exp_col = st.selectbox("Expiry Column", cols)
                with c3: qty_col = st.selectbox("Qty Column", cols)
                
                if st.button("Save Stock"):
                    clean_stock = pd.DataFrame({
                        "Product Name": raw_df[name_col],
                        "Expiry": raw_df[exp_col],
                        "Available Qty": raw_df[qty_col],
                        "Order Qty": 0
                    })
                    clean_stock.to_csv(STOCK_FILE, index=False)
                    st.success("✅ Stock Updated!")
            except Exception as e: st.error(f"Error: {e}")

        st.divider()
        st.subheader("2. Download Orders (Separated by Branch)")
        
        if os.path.exists(ORDERS_FILE):
            orders_df = pd.read_csv(ORDERS_FILE)
            st.dataframe(orders_df, use_container_width=True)
            
            # --- EXCEL GENERATION LOGIC ---
            # Create an in-memory Excel file
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Sheet 1: All Orders (Master)
                orders_df.to_excel(writer, sheet_name='MASTER_ALL', index=False)
                
                # Sheet 2...N: Separate Sheet for every Branch
                unique_branches = orders_df['Branch'].unique()
                for branch in unique_branches:
                    # Filter data for this branch
                    branch_data = orders_df[orders_df['Branch'] == branch]
                    # Sanitize branch name for Excel tab (max 31 chars)
                    safe_name = str(branch)[:30].replace(":", "").replace("/", "")
                    branch_data.to_excel(writer, sheet_name=safe_name, index=False)
            
            output.seek(0)
            
            st.download_button(
                label="📥 Download Excel (with Separate Tabs)",
                data=output,
                file_name=f"orders_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            if st.button("🗑️ Clear History"):
                os.remove(ORDERS_FILE)
                st.rerun()
        else:
            st.info("No orders yet.")
