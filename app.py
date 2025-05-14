import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Constants
DATA_FILE = "invoices.csv"
USER_CREDENTIALS = {"admin": "1234"}  # simple login system (for demo)

# Session management
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if USER_CREDENTIALS.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("❌ Invalid username or password")

if not st.session_state.logged_in:
    login()
    st.stop()


# Load or initialize data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
else:
    df = pd.DataFrame(columns=["Date", "Company", "Item ID", "Item Name", "Quantity", "Unit", "Price per Unit", "Total Price"])

# Sidebar form
st.sidebar.header("➕ Add New Invoice")
with st.sidebar.form("entry_form"):
    date = st.date_input("Invoice Date", datetime.today())
    company = st.text_input("Company Name")
    item_id = st.text_input("Item ID")
    item_name = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
    unit = st.selectbox("Unit", ["Carton", "Box", "Kilogram", "Liter", "Piece"])
    price_per_unit = st.number_input("Price per Unit", min_value=0.0, step=0.1)
    submitted = st.form_submit_button("Add Invoice")

    if submitted:
        total_price = quantity * price_per_unit
        new_row = {
            "Date": pd.to_datetime(date),
            "Company": company,
            "Item ID": item_id,
            "Item Name": item_name,
            "Quantity": quantity,
            "Unit": unit,
            "Price per Unit": price_per_unit,
            "Total Price": total_price
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("✅ Invoice added successfully!")

# Main display
st.title("📦 Business Invoice Manager")

# Filters
st.subheader("🔍 Filter Invoices")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", df["Date"].min() if not df.empty else datetime.today())
    end_date = st.date_input("End Date", df["Date"].max() if not df.empty else datetime.today())
with col2:
    search_company = st.text_input("Search by Company")
    search_item = st.text_input("Search by Item Name")

filtered_df = df[
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date)) &
    (df["Company"].str.contains(search_company, case=False, na=False)) &
    (df["Item Name"].str.contains(search_item, case=False, na=False))
]

st.dataframe(filtered_df)

# Summary
if not filtered_df.empty:
    st.subheader("📊 Summary by Company")
    summary = filtered_df.groupby("Company")["Total Price"].sum().reset_index()
    summary.columns = ["Company", "Total Owed"]
    st.dataframe(summary)

    import io

# Create Excel buffer in memory
invoice_buffer = io.BytesIO()
summary_buffer = io.BytesIO()

# Write dataframes to Excel files in memory
with pd.ExcelWriter(invoice_buffer, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='Invoices')
invoice_buffer.seek(0)

with pd.ExcelWriter(summary_buffer, engine='openpyxl') as writer:
    summary.to_excel(writer, index=False, sheet_name='Summary')
summary_buffer.seek(0)

# Streamlit download buttons
st.download_button(
    label="Download Invoices (Excel)",
    data=invoice_buffer,
    file_name="invoices.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.download_button(
    label="Download Summary (Excel)",
    data=summary_buffer,
    file_name="summary.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

