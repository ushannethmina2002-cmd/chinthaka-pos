import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# පිටුවේ සැකසුම්
st.set_page_config(page_title="Chinthaka POS", layout="centered")

st.title("💻 Chinthaka Computers")

# Google Sheet සම්බන්ධතාවය පරීක්ෂා කිරීම
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # පාරිභෝගික දත්ත ඇතුළත් කිරීමේ පෝරමය
    with st.form("repair_form", clear_on_submit=True):
        st.subheader("🛠️ නව අලුත්වැඩියාවක් ඇතුළත් කරන්න")
        name = st.text_input("පාරිභෝගිකයාගේ නම")
        device = st.text_input("උපාංගය")
        issue = st.text_area("දෝෂය")
        price = st.number_input("මිල (Rs.)", min_value=0)
        
        submit = st.form_submit_button("සේව් කර බිල්පත පෙන්වන්න")

    if submit:
        if name and device:
            # අලුත් දත්ත පේළියක් සෑදීම
            new_data = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Customer": name,
                "Device": device,
                "Issue": issue,
                "Price": price
            }])
            
            # පවතින දත්ත කියවා අලුත් දත්ත එකතු කිරීම
            df = conn.read(worksheet="Repairs")
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(worksheet="Repairs", data=updated_df)
            
            st.success("✅ දත්ත සාර්ථකව සේව් වුණා!")
            
            # --- ලස්සන රිසිට් එක ---
            st.markdown(f"""
            <div style="border: 2px dashed #000; padding: 20px; background-color: #fff; color: #000; font-family: monospace; border-radius: 10px;">
                <h2 style="text-align: center;">CHINTHAKA COMPUTERS</h2>
                <p style="text-align: center;">Kandy Road, Sri Lanka</p>
                <hr>
                <p><b>Date:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                <p><b>Customer:</b> {name}</p>
                <p><b>Device:</b> {device}</p>
                <p><b>Issue:</b> {issue}</p>
                <hr>
                <h3 style="text-align: right;">Total: Rs. {price:,.2f}</h3>
                <p style="text-align: center;">*** Thank You! ***</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("කරුණාකර නම සහ උපාංගය ඇතුළත් කරන්න.")

except Exception as e:
    st.error(f"⚠️ ප්‍රශ්නයක් තිබේ: {e}")
    st.info("ඔබේ Secrets වල Google Sheet Link එක නිවැරදිදැයි පරීක්ෂා කරන්න.")
