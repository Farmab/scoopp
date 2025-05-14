import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

st.set_page_config(page_title="Daily Expense Tracker", layout="wide")

# Load Montserrat font and style the header
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
    .montserrat-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 40px;
        color: yellow;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    <div class="montserrat-title">Scoop Company</div>
""", unsafe_allow_html=True)

st.title("📘 Daily Expense Entry Web App")

# Initialize session state to store entries
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=[
        "Company", "Subject", "Quantity", "Unit",
        "Price per Unit", "Currency", "Total Price",
        "Date", "Status"
    ])

# Add new expense entry
st.subheader("➕ Add New Expense")

common_units = ["kg", "L", "box", "carton", "piece"]

with st.form("expense_form"):
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company")
        subject = st.text_input("Subject")
        quantity = st.number_input("Quantity", min_value=0.0, format="%.2f")
        selected_unit = st.selectbox("Choose a Unit", options=common_units)
        custom_unit = st.text_input("Or enter a custom Unit")
        unit = custom_unit if custom_unit else selected_unit
        price_per_unit = st.number_input("Price per Unit", min_value=0.0, format="%.2f")
    with col2:
        currency = st.selectbox("Currency", ["IQD", "$"])
        date = st.date_input("Date", value=datetime.date.today())
        status = st.selectbox("Status", ["paid", "unpaid"])

    submitted = st.form_submit_button("Add Expense")
    if submitted:
        total_price = quantity * price_per_unit
        new_entry = {
            "Company": company,
            "Subject": subject,
            "Quantity": quantity,
            "Unit": unit,
            "Price per Unit": price_per_unit,
            "Currency": currency,
            "Total Price": total_price,
            "Date": date,
            "Status": status
        }
        st.session_state.expenses = st.session_state.expenses._append(new_entry, ignore_index=True)
        st.success("✅ Expense added successfully!")

# Filter section
st.sidebar.header("🔍 Filter Expenses")
df = st.session_state.expenses

company_filter = st.sidebar.multiselect("Company", options=df["Company"].unique())
subject_filter = st.sidebar.multiselect("Subject", options=df["Subject"].unique())
status_filter = st.sidebar.multiselect("Status", options=df["Status"].unique())
currency_filter = st.sidebar.multiselect("Currency", options=df["Currency"].unique())
date_range = st.sidebar.date_input("Date Range", [])

filtered_df = df.copy()
if company_filter:
    filtered_df = filtered_df[filtered_df["Company"].isin(company_filter)]
if subject_filter:
    filtered_df = filtered_df[filtered_df["Subject"].isin(subject_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]
if currency_filter:
    filtered_df = filtered_df[filtered_df["Currency"].isin(currency_filter)]
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
    ]

st.subheader("📄 Expense Table")
st.dataframe(filtered_df, use_container_width=True)

# Summary metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Total Expenses", f"{filtered_df['Total Price'].sum():,.2f}")
with col2:
    unpaid = filtered_df[filtered_df["Status"] == "unpaid"]["Total Price"].sum()
    st.metric("❗ Unpaid Total", f"{unpaid:,.2f}")

# Download as Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

excel_file = to_excel(df)
st.download_button(
    label="📥 Download All Expenses as Excel",
    data=excel_file,
    file_name="daily_expenses.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
