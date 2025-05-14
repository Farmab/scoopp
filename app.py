import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

st.set_page_config(page_title="Daily Expense Tracker", layout="wide")

st.title("📘 Daily Expense Tracker")

def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    df.columns.name = None
    return df

def download_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

uploaded_file = st.file_uploader("📤 Upload your Excel sheet", type=["xlsx"])
if uploaded_file:
    df = load_data(uploaded_file)

    st.sidebar.header("🔍 Filter Options")
    company_filter = st.sidebar.multiselect("Company", df["company name"].dropna().unique())
    subject_filter = st.sidebar.multiselect("Subject", df["subject"].dropna().unique())
    currency_filter = st.sidebar.multiselect("Currency", df["currency/ $, IQD"].dropna().unique())
    status_filter = st.sidebar.multiselect("Status", df["status/ paid,unpaid"].dropna().unique())

    filtered_df = df.copy()
    if company_filter:
        filtered_df = filtered_df[filtered_df["company name"].isin(company_filter)]
    if subject_filter:
        filtered_df = filtered_df[filtered_df["subject"].isin(subject_filter)]
    if currency_filter:
        filtered_df = filtered_df[filtered_df["currency/ $, IQD"].isin(currency_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df["status/ paid,unpaid"].isin(status_filter)]

    st.dataframe(filtered_df, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Total Expenses", f"{filtered_df['total price'].astype(float).sum():,.2f}")
    with col2:
        unpaid_total = filtered_df[filtered_df["status/ paid,unpaid"] == "unpaid"]["total price"].astype(float).sum()
        st.metric("❗ Unpaid Total", f"{unpaid_total:,.2f}")

    st.markdown("---")
    st.subheader("➕ Add New Expense")

    with st.form("new_expense_form"):
        company = st.text_input("Company Name")
        subject = st.text_input("Subject")
        quantity = st.number_input("Quantity", min_value=0.0, format="%.2f")
        unit = st.text_input("Unit (kg, box, etc.)")
        price = st.number_input("Price per Unit", min_value=0.0, format="%.2f")
        currency = st.selectbox("Currency", ["IQD", "$"])
        date = st.date_input("Date", value=datetime.date.today())
        status = st.selectbox("Status", ["paid", "unpaid"])
        submit = st.form_submit_button("Add Expense")

        if submit:
            total = quantity * price
            new_row = {
                "company name": company,
                "subject": subject,
                "quantity": quantity,
                "unit/ kg,L,catron,box": unit,
                "price per unit": price,
                "currency/ $, IQD": currency,
                "total price": total,
                "date": date.strftime("%Y-%m-%d"),
                "status/ paid,unpaid": status
            }
            df = df._append(new_row, ignore_index=True)
            st.success("✅ Expense added!")

    # Download option
    excel_data = download_excel(df)
    st.download_button(
        label="📥 Download Updated Excel",
        data=excel_data,
        file_name="updated_daily_expenses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Upload your Excel file to begin.")
