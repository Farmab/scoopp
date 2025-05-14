import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

# --- Set page config ---
st.set_page_config(page_title="OneProAgency Manager", layout="centered")

# --- Display saved logo if exists ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)

# --- Upload logo (only once) ---
st.sidebar.header("🖼️ Upload Logo")
logo_file = st.sidebar.file_uploader("Upload your company logo", type=["png", "jpg", "jpeg"])
if logo_file:
    with open("logo.png", "wb") as f:
        f.write(logo_file.getbuffer())
    st.sidebar.success("Logo uploaded successfully!")
    st.experimental_rerun()

# --- Tabs for Invoices and Expenses ---
tab1, tab2 = st.tabs(["🧾 Invoices", "💰 Daily Expenses"])

# --- Invoice Management ---
with tab1:
    st.header("🧾 Invoice Management")

    if not os.path.exists("data"):
        os.makedirs("data")

    invoice_file = "data/invoices.csv"

    with st.form("invoice_form"):
        customer = st.text_input("Customer Name")
        invoice_no = st.text_input("Invoice Number")
        invoice_amount = st.number_input("Amount ($)", min_value=0.0)
        submitted = st.form_submit_button("Add Invoice")

        if submitted:
            new_invoice = pd.DataFrame([[date.today(), customer, invoice_no, invoice_amount]],
                                       columns=["Date", "Customer", "Invoice No", "Amount"])
            if os.path.exists(invoice_file):
                old = pd.read_csv(invoice_file)
                new_invoice = pd.concat([old, new_invoice], ignore_index=True)
            new_invoice.to_csv(invoice_file, index=False)
            st.success("Invoice added successfully!")

    if os.path.exists(invoice_file):
        st.subheader("📄 All Invoices")
        df_invoices = pd.read_csv(invoice_file)
        st.dataframe(df_invoices)
        st.metric("Total Invoices", f"${df_invoices['Amount'].sum():.2f}")
        
        # Export to Excel
        st.download_button(
            label="Download Invoices as Excel",
            data=df_invoices.to_excel(index=False, engine='openpyxl'),
            file_name="invoices.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- Daily Expense Tracker ---
with tab2:
    st.header("💰 Daily Expense Tracker")

    expense_file = "data/expenses.csv"

    with st.form("expense_form"):
        exp_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", ["Food", "Transport", "Utilities", "Shopping", "Other"])
        description = st.text_input("Description")
        method = st.selectbox("Payment Method", ["Cash", "Card", "Transfer", "Other"])
        exp_amount = st.number_input("Amount ($)", min_value=0.0)
        exp_submit = st.form_submit_button("Add Expense")

        if exp_submit:
            new_expense = pd.DataFrame([[exp_date, category, description, method, exp_amount]],
                                       columns=["Date", "Category", "Description", "Payment Method", "Amount"])
            if os.path.exists(expense_file):
                old_expenses = pd.read_csv(expense_file)
                new_expense = pd.concat([old_expenses, new_expense], ignore_index=True)
            new_expense.to_csv(expense_file, index=False)
            st.success("Expense recorded!")

    if os.path.exists(expense_file):
        st.subheader("📊 All Expenses")
        df_exp = pd.read_csv(expense_file)
        st.dataframe(df_exp)
        st.metric("Total Expenses", f"${df_exp['Amount'].sum():.2f}")

        # Export to Excel
        st.download_button(
            label="Download Expenses as Excel",
            data=df_exp.to_excel(index=False, engine='openpyxl'),
            file_name="expenses.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Pie chart of categories
        st.subheader("📈 Expense by Category")
        cat_summary = df_exp.groupby("Category")["Amount"].sum().reset_index()
        fig = px.pie(cat_summary, names="Category", values="Amount", title="Spending Breakdown")
        st.plotly_chart(fig)

        # Bar chart by date
        st.subheader("📊 Daily Spending")
        df_exp["Date"] = pd.to_datetime(df_exp["Date"])
        daily_summary = df_exp.groupby("Date")["Amount"].sum().reset_index()
        fig2 = px.bar(daily_summary, x="Date", y="Amount", title="Daily Expenses")
        st.plotly_chart(fig2)
