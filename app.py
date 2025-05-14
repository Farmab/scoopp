import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

st.set_page_config(page_title="Daily Expense Tracker", layout="wide")

# Scoop Company Header
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

# Session init
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=[
        "Company", "Subject", "Quantity", "Unit",
        "Price per Unit", "Currency", "Total Price",
        "Date", "Status"
    ])
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# Add new expense
st.subheader("➕ Add New Expense")
common_units = ["kg", "L", "box", "carton", "piece"]

with st.form("add_expense", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company")
        subject = st.text_input("Subject")
        quantity = st.number_input("Quantity", min_value=0.0, format="%.2f")
        selected_unit = st.selectbox("Choose Unit", common_units)
        custom_unit = st.text_input("Or enter custom unit")
        unit = custom_unit if custom_unit else selected_unit
        price = st.number_input("Price per Unit", min_value=0.0, format="%.2f")
    with col2:
        currency = st.selectbox("Currency", ["IQD", "$"])
        date = st.date_input("Date", value=datetime.date.today())
        status = st.selectbox("Status", ["paid", "unpaid"])

    if st.form_submit_button("Add Expense"):
        total = quantity * price
        new_entry = {
            "Company": company,
            "Subject": subject,
            "Quantity": quantity,
            "Unit": unit,
            "Price per Unit": price,
            "Currency": currency,
            "Total Price": total,
            "Date": date,
            "Status": status
        }
        st.session_state.expenses = st.session_state.expenses._append(new_entry, ignore_index=True)
        st.success("✅ Added!")
        st.rerun()

# Sidebar filters
st.sidebar.header("🔍 Filter Expenses")
df = st.session_state.expenses

company_filter = st.sidebar.multiselect("Company", df["Company"].unique())
subject_filter = st.sidebar.multiselect("Subject", df["Subject"].unique())
status_filter = st.sidebar.multiselect("Status", df["Status"].unique())
currency_filter = st.sidebar.multiselect("Currency", df["Currency"].unique())
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

# Bulk unpaid to paid
st.markdown("### 🔄 Monthly Payment Update")
if not filtered_df.empty and "unpaid" in filtered_df["Status"].values:
    if st.button("✅ Mark All Filtered Unpaid as Paid"):
        mask = (st.session_state.expenses["Status"] == "unpaid") & (
            st.session_state.expenses.apply(tuple, axis=1).isin(filtered_df.apply(tuple, axis=1))
        )
        st.session_state.expenses.loc[mask, "Status"] = "paid"
        st.success(f"✅ {mask.sum()} invoices marked as paid!")
        st.rerun()
else:
    st.info("No unpaid invoices in current filter.")

# Show editable table
st.subheader("📄 All Invoices")

if not filtered_df.empty:
    edited_rows = []
    for i, row in filtered_df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
        with col1:
            st.write(f"**{row['Company']}**")
            st.write(row["Subject"])
        with col2:
            st.write(f"{row['Quantity']} {row['Unit']}")
            st.write(f"{row['Price per Unit']} {row['Currency']}")
        with col3:
            st.write(f"💰 {row['Total Price']} {row['Currency']}")
            st.write(f"{row['Date']} | {row['Status']}")
        with col4:
            if st.button("✏️ Edit", key=f"edit_{i}"):
                st.session_state.edit_index = i
        with col5:
            if st.button("🗑 Delete", key=f"delete_{i}"):
                st.session_state.expenses.drop(index=i, inplace=True)
                st.session_state.expenses.reset_index(drop=True, inplace=True)
                st.rerun()
else:
    st.info("No invoices match the current filters.")

# Edit mode form
if st.session_state.edit_index is not None:
    idx = st.session_state.edit_index
    row = st.session_state.expenses.loc[idx]
    st.markdown("### ✏️ Edit Invoice")
    with st.form("edit_invoice"):
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("Company", value=row["Company"])
            subject = st.text_input("Subject", value=row["Subject"])
            quantity = st.number_input("Quantity", value=row["Quantity"], min_value=0.0)
            unit = st.text_input("Unit", value=row["Unit"])
            price = st.number_input("Price per Unit", value=row["Price per Unit"], min_value=0.0)
        with col2:
            currency = st.selectbox("Currency", ["IQD", "$"], index=["IQD", "$"].index(row["Currency"]))
            date = st.date_input("Date", value=pd.to_datetime(row["Date"]))
            status = st.selectbox("Status", ["paid", "unpaid"], index=["paid", "unpaid"].index(row["Status"]))

        if st.form_submit_button("Update Invoice"):
            total = quantity * price
            st.session_state.expenses.loc[idx] = [
                company, subject, quantity, unit, price,
                currency, total, date, status
            ]
            st.session_state.edit_index = None
            st.success("✅ Updated!")
            st.rerun()

# Summary
col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Total Expenses", f"{filtered_df['Total Price'].sum():,.2f}")
with col2:
    unpaid = filtered_df[filtered_df["Status"] == "unpaid"]["Total Price"].sum()
    st.metric("❗ Unpaid Total", f"{unpaid:,.2f}")

# Excel export
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

excel_file = to_excel(st.session_state.expenses)
st.download_button(
    label="📥 Download All Expenses as Excel",
    data=excel_file,
    file_name="daily_expenses.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
