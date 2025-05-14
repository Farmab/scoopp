import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io
import plotly.express as px

# ---------------------- Constants ----------------------
DATA_FILE = "invoices.csv"
USER_CREDENTIALS = {"ferman": "mypassword123"}
CURRENCY_SYMBOLS = {"IQD": "د.ع", "USD": "$"}

# ------------------ Session State ----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --------------------- Login UI ------------------------
def login():
    st.markdown("""
        <h1 style='text-align: center; background: linear-gradient(to right, #4facfe, #00f2fe); 
        -webkit-background-clip: text; color: transparent;'>🔐 Secure Login</h1>
    """, unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if USER_CREDENTIALS.get(username) == password:
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.error("❌ Invalid username or password")

if not st.session_state.logged_in:
    login()
    st.stop()

# -------------------- Load Data ------------------------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
else:
    df = pd.DataFrame(columns=["Date", "Company", "Item ID", "Item Name", "Quantity", "Unit", "Price per Unit", "Total Price", "Currency"])

# -------------------- Sidebar Form ----------------------
st.sidebar.header("➕ Add New Invoice")
with st.sidebar.form("entry_form"):
    date = st.date_input("Invoice Date", datetime.today())
    company = st.text_input("Company Name")
    item_id = st.text_input("Item ID")
    item_name = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
    unit = st.selectbox("Unit", ["Carton", "Box", "Kilogram", "Liter", "Piece"])
    price_per_unit = st.number_input("Price per Unit", min_value=0.0, step=0.1)
    currency = st.radio("Currency", ["IQD", "USD"], horizontal=True)
    submitted = st.form_submit_button("Submit")

    if submitted:
        symbol = CURRENCY_SYMBOLS[currency]
        total = quantity * price_per_unit
        new_row = {
            "Date": pd.to_datetime(date),
            "Company": company,
            "Item ID": item_id,
            "Item Name": item_name,
            "Quantity": quantity,
            "Unit": unit,
            "Price per Unit": f"{price_per_unit:,.2f} {symbol}",
            "Total Price": f"{total:,.2f} {symbol}",
            "Currency": currency
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("✅ Invoice added successfully!")

# -------------------- Main UI --------------------------
st.image("english logo.png", width=150)
st.markdown("""
    <h1 style='text-align: center; background: linear-gradient(to right, #667eea, #764ba2); 
    -webkit-background-clip: text; color: transparent;'>📆 Business Invoice Manager</h1>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("🕛 Start Date", df["Date"].min() if not df.empty else datetime.today())
    search_company = st.text_input("👤 Search by Company")
with col2:
    end_date = st.date_input("🕒 End Date", df["Date"].max() if not df.empty else datetime.today())
    search_item = st.text_input("🏪 Search by Item Name")

# -------------------- Filtering ------------------------
filtered_df = df[(df["Date"] >= pd.to_datetime(start_date)) &
                 (df["Date"] <= pd.to_datetime(end_date)) &
                 (df["Company"].str.contains(search_company, case=False, na=False)) &
                 (df["Item Name"].str.contains(search_item, case=False, na=False))]

st.markdown("### 📄 Filtered Invoices")
st.dataframe(filtered_df, height=600, use_container_width=True)

# -------------------- Summary + Charts --------------------------
if not filtered_df.empty:
    temp_df = filtered_df.copy()
    if "Currency" in temp_df.columns:
        temp_df["Numeric Total"] = temp_df["Total Price"].astype(str).str.extract(r"([0-9,.]+)")[0].replace({',': ''}, regex=True).astype(float)
        summary = temp_df.groupby(["Company", "Currency"])["Numeric Total"].sum().reset_index()
        summary["Total Owed"] = summary.apply(lambda row: f"{row['Numeric Total']:,.2f} {CURRENCY_SYMBOLS.get(row['Currency'], '')}" , axis=1)
        summary_display = summary[["Company", "Total Owed"]]

        st.markdown("### 📊 Summary by Company")
        st.dataframe(summary_display, height=400, use_container_width=True)

        # Chart
        st.markdown("### 📈 Visual Summary")
        chart = px.bar(summary, x="Company", y="Numeric Total", color="Currency",
                      title="Total Purchases per Company",
                      labels={"Numeric Total": "Total Amount"},
                      color_discrete_sequence=px.colors.sequential.Bluered)
        st.plotly_chart(chart, use_container_width=True)

        # ----------------- Excel Export -------------------
        invoice_buffer = io.BytesIO()
        summary_buffer = io.BytesIO()
        with pd.ExcelWriter(invoice_buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Invoices')
        with pd.ExcelWriter(summary_buffer, engine='openpyxl') as writer:
            summary_display.to_excel(writer, index=False, sheet_name='Summary')
        invoice_buffer.seek(0)
        summary_buffer.seek(0)

        st.markdown("### 📂 Download Reports")
        col3, col4 = st.columns(2)
        with col3:
            st.download_button("Download Invoices (Excel)", data=invoice_buffer, file_name="invoices.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col4:
            st.download_button("Download Summary (Excel)", data=summary_buffer, file_name="summary.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("Missing 'Currency' column in data. Please recheck invoice entries.")
else:
    st.info("No matching invoices found. Try adjusting your filters.")
