import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# මූලික සැකසුම්
st.set_page_config(page_title="Chinthaka POS")

# Google Sheets සම්බන්ධතාවය
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Sheet Connection Error!")

st.title("💻 Chinthaka Computers")

# ඉතාම සරල Form එකක්
with st.form("test_form"):
    cust_name = st.text_input("පාරිභෝගිකයාගේ නම")
    price = st.number_input("මිල", min_value=0)
    submit = st.form_submit_button("සේව් කරන්න")

    if submit:
        if cust_name:
            try:
                # දැනට තියෙන දත්ත කියවීම
                df = conn.read(worksheet="Repairs")
                
                # අලුත් දත්ත පේළිය
                new_data = pd.DataFrame([{"Customer": cust_name, "Price": price}])
                
                # එකතු කිරීම
                updated_df = pd.concat([df, new_data], ignore_index=True)
                
                # Sheet එකට යැවීම
                conn.update(worksheet="Repairs", data=updated_df)
                st.success("සාර්ථකව සේව් වුණා!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("නම ඇතුළත් කරන්න")

# දත්ත පෙන්වීම
if st.button("දත්ත පෙන්වන්න"):
    try:
        data = conn.read(worksheet="Repairs")
        st.write(data)
    except:
        st.error("දත්ත කියවීමට බැහැ")
