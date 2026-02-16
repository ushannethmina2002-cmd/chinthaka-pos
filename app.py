import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# පිටුවේ සැකසුම් - පෑජ් එකේ පෙනුම සකස් කිරීම
st.set_page_config(page_title="Chinthaka Computers POS", page_icon="💻", layout="centered")

# Google Sheets සම්බන්ධතාවය ස්ථාපනය කිරීම
conn = st.connection("gsheets", type=GSheetsConnection)

# ලස්සන රිසිට් එකක් ඩිසයින් කිරීම (HTML/CSS භාවිතා කර)
def generate_receipt(name, device, issue, price):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    receipt_html = f"""
    <div style="border: 2px dashed #333; padding: 20px; font-family: 'Courier New', Courier, monospace; background-color: #f9f9f9; color: #000; border-radius: 10px;">
        <h2 style="text-align: center; margin-bottom: 5px;">CHINTHAKA COMPUTERS</h2>
        <p style="text-align: center; font-size: 12px; margin-top: 0;">No. 123, Kandy Road, Sri Lanka<br>Tel: 07x-xxxxxxx</p>
        <hr>
        <p><b>Date:</b> {now}</p>
        <p><b>Customer:</b> {name}</p>
        <p><b>Device:</b> {device}</p>
        <hr>
        <table style="width:100%">
            <tr>
                <td style="text-align: left;">Description: {issue}</td>
                <td style="text-align: right;">Rs. {price:,.2f}</td>
            </tr>
        </table>
        <hr>
        <h3 style="text-align: right;">TOTAL: Rs. {price:,.2f}</h3>
        <p style="text-align: center; font-size: 14px; margin-top: 20px;">*** Thank You! Come Again! ***</p>
    </div>
    """
    return receipt_html

# පැත්තක තියෙන මෙනුව (Sidebar)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2004/2004699.png", width=100)
st.sidebar.title("Chinthaka POS")
menu = ["අලුත්වැඩියා (Repairs)", "අලෙවි වාර්තා (View Data)"]
choice = st.sidebar.selectbox("පද්ධති මෙනුව", menu)

if choice == "අලුත්වැඩියා (Repairs)":
    st.subheader("🛠️ New Repair Job & Billing")
    
    with st.form("repair_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cust_name = st.text_input("පාරිභෝගිකයාගේ නම")
            device = st.text_input("උපාංගය (Laptop/Mouse/etc)")
        with col2:
            price = st.number_input("මිල (Rs.)", min_value=0.0, step=100.0)
            status = st.selectbox("තත්ත්වය", ["Pending", "Completed"])
        
        issue = st.text_area("දෝෂය හෝ විස්තරය")
        
        submitted = st.form_submit_button("ඇතුළත් කර බිල්පත සාදන්න")
        
        if submitted:
            if cust_name and device:
                try:
                    # අලුත් දත්ත පේළිය සෑදීම
                    new_data = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Customer": cust_name,
                        "Device": device,
                        "Issue": issue,
                        "Price": price,
                        "Status": status
                    }])
                    
                    # දැනට තියෙන දත්ත කියවා අලුත් දත්ත එකතු කිරීම
                    existing_data = conn.read(worksheet="Repairs")
                    updated_df = pd.concat([existing_data, new_data], ignore_index=True)
                    
                    # Google Sheet එකට දත්ත යැවීම
                    conn.update(worksheet="Repairs", data=updated_df)
                    
                    st.success("✅ දත්ත සාර්ථකව Google Sheet එකට ඇතුළත් කළා!")
                    
                    # ලස්සන රිසිට් එක පෙන්වීම
                    st.markdown("### 📄 පාරිභෝගික රිසිට් එක")
                    st.markdown(generate_receipt(cust_name, device, issue, price), unsafe_allow_html=True)
                    st.info("💡 මෙම රිසිට් එක Screen එකෙන් Print කර පාරිභෝගිකයාට ලබාදිය හැක.")
                except Exception as e:
                    st.error(f"Error: {e}. Please check your Google Sheet connection.")
            else:
                st.warning("කරුණාකර නම සහ උපාංගය යන දෙකම ඇතුළත් කරන්න.")

elif choice == "අලෙවි වාර්තා (View Data)":
    st.subheader("📊 Past Transactions")
    try:
        data = conn.read(worksheet="Repairs")
        st.dataframe(data, use_container_width=True)
    except Exception as e:
        st.error("දත්ත කියවීමට නොහැක. ඔබගේ Google Sheet එකේ 'Repairs' නමින් ටැබ් එකක් තිබේදැයි පරීක්ෂා කරන්න.")
