import streamlit as st
import pandas as pd

# Fungsi untuk melakukan analisis rekonsiliasi
def perform_analysis(finpayKolaka, mutasi_kolaka_sebulan):
    # Rename the columns of finpayKolaka to match the expected column names
    finpayKolaka.columns = [
        'No', 'Transaction Date', 'Transaction ID', 'Saldo Awal', 'Kredit', 
        'Debet', 'Saldo Akhir', 'Transaction Type', 'Transaction', 'Remarks'
    ]

    # Rename the columns of mutasi_kolaka_sebulan to match the expected column names
    mutasi_kolaka_sebulan.columns = [
        'Receipt No.', 'Completion Time', 'Initiation Time', 'Details',
        'Transaction Status', 'Currency', 'Paid In', 'Withdrawn', 'Balance',
        'Reason Type', 'Opposite Party', 'Linked Transaction ID'
    ]

    # Convert 'Receipt No.' column to string in mutasi_kolaka_sebulan
    mutasi_kolaka_sebulan['Receipt No.'] = mutasi_kolaka_sebulan['Receipt No.'].astype(str)

    # Convert 'Transaction ID' column to string in finpayKolaka and remove 'F_' prefix
    finpayKolaka['Transaction ID'] = finpayKolaka['Transaction ID'].astype(str).str.replace('F_', '')

    # Add leading zeros to 'Receipt No.' to match the length of 'Transaction ID'
    mutasi_kolaka_sebulan['Receipt No.'] = mutasi_kolaka_sebulan['Receipt No.'].apply(lambda x: x.zfill(20))

    # Join the two tables
    merged_data = pd.merge(
        finpayKolaka, 
        mutasi_kolaka_sebulan, 
        left_on='Transaction ID', 
        right_on='Receipt No.', 
        how='inner'
    )

    # Process the data to match the SELECT statement
    result = pd.DataFrame({
        '*Customer': merged_data['Opposite Party'],
        'Email': '',
        'BillingAddress': '',
        'ShippingAddress': '',
        '*InvoiceDate': merged_data['Transaction Date'],
        '*DueDate': merged_data['Completion Time'],
        'ShippingDate': '',
        'ShipVia': '',
        'TrackingNo': '',
        'CustomerRefNo': '',
        '*InvoiceNumber': merged_data['Receipt No.'],
        'Message': '',
        'Memo': '',
        '*ProductName': merged_data['Details'],
        'Description': '',
        '*Quantity': (merged_data['Withdrawn'].abs() / 1000).round(),
        'Unit': '',
        '*UnitPrice': (merged_data['Kredit'] / (merged_data['Withdrawn'].abs() / 1000)).apply(lambda x: f"{x:,.6f}".replace('.', ',')),
        'kredit': merged_data['Kredit'],
        'debet': merged_data['Debet'],
        'ProductDiscountRate(%)': '',
        'InvoiceDiscountRate(%)': '',
        'TaxName': 'PPN',
        'TaxRate(%)': '11%',
        'ShippingFee': '',
        'WitholdingAccountCode': '',
        'WitholdingAmount(value or %)': '',
        '#paid?(yes/no)': 'YES',
        '#PaymentMethod': 'TRANSFER',
        '#PaidToAccountCode': '1-110005',
        'Tags (use': 'Finpay, Kolaka',
        'WarehouseName': 'Kolaka',
        '#currency code(example: IDR, USD, CAD)': ''
    })

    result = result.head(1000)

    # For the second query
    left_joined_data = pd.merge(
        mutasi_kolaka_sebulan, 
        finpayKolaka, 
        left_on='Receipt No.', 
        right_on='Transaction ID', 
        how='left'
    )

    left_joined_data_filtered = left_joined_data[left_joined_data['Transaction ID'].isna()]

    # Process the data to match the SELECT statement
    result_left_join = pd.DataFrame({
        '*Customer': left_joined_data_filtered['Opposite Party'],
        'Email': '',
        'BillingAddress': '',
        'ShippingAddress': '',
        '*InvoiceDate': left_joined_data_filtered['Transaction Date'],
        '*DueDate': left_joined_data_filtered['Completion Time'],
        'ShippingDate': '',
        'ShipVia': '',
        'TrackingNo': '',
        'CustomerRefNo': '',
        '*InvoiceNumber': left_joined_data_filtered['Receipt No.'],
        'Message': '',
        'Memo': '',
        '*ProductName': left_joined_data_filtered['Details'],
        'Description': '',
        '*Quantity': (left_joined_data_filtered['Withdrawn'].abs() / 1000).round(),
        'Unit': '',
        '*UnitPrice': (left_joined_data_filtered['Kredit'] / (left_joined_data_filtered['Withdrawn'].abs() / 1000)).apply(lambda x: f"{x:,.6f}".replace('.', ',')),
        'ProductDiscountRate(%)': '',
        'InvoiceDiscountRate(%)': '',
        'TaxName': 'PPN',
        'TaxRate(%)': '11%',
        'ShippingFee': '',
        'WitholdingAccountCode': '',
        'WitholdingAmount(value or %)': '',
        '#paid?(yes/no)': 'YES',
        '#PaymentMethod': 'TRANSFER',
        '#PaidToAccountCode': '1-110005',
        'Tags (use': 'Finpay, Kolaka',
        'WarehouseName': 'Kolaka',
        '#currency code(example: IDR, USD, CAD)': ''
    })

    result_left_join = result_left_join.head(1000)

    return result, result_left_join

# Streamlit app
st.title("Data Reconciliation Analysis")

if 'finished' not in st.session_state:
    st.session_state.finished = False

if not st.session_state.finished:
    uploaded_file1 = st.file_uploader("Upload Finpay Riwayat Saldo file", type=["xlsx"])
    uploaded_file2 = st.file_uploader("Upload Mutasi Bulk NGRS Mitra file", type=["xlsx"])

    if uploaded_file1 and uploaded_file2:
        finpayKolaka = pd.read_excel(uploaded_file1, skiprows=2)
        mutasi_kolaka_sebulan = pd.read_excel(uploaded_file2)

        result_query1, result_query2 = perform_analysis(finpayKolaka, mutasi_kolaka_sebulan)
        
        st.write("### Result Query 1")
        st.dataframe(result_query1)
        
        st.write("### Result Query 2")
        st.dataframe(result_query2)
        
        # Save the results to CSV with the new filenames
        result_query1.to_csv('Join Mutasi Dan Finpay.csv', index=False)
        result_query2.to_csv('Left Join Mutasi Dan Finpay.csv', index=False)
        
        # Provide download links with the new filenames
        st.download_button(
            label="Download Join Mutasi Dan Finpay as CSV",
            data=result_query1.to_csv(index=False),
            file_name='Join Mutasi Dan Finpay.csv',
            mime='text/csv',
        )
        
        st.download_button(
            label="Download Left Join Mutasi Dan Finpay as CSV",
            data=result_query2.to_csv(index=False),
            file_name='Left Join Mutasi Dan Finpay.csv',
            mime='text/csv',
        )
        
        if st.button("Selesai"):
            st.session_state.finished = True
else:
    if st.button("Mulai Lagi"):
        st.session_state.finished = False
        st.experimental_rerun()
