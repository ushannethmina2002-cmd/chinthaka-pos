import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from reportlab.pdfgen import canvas
from io import BytesIO

# -------------------------
# Database
# -------------------------
conn = sqlite3.connect("chinthaka_pos.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price REAL,
    stock INTEGER
)""")

c.execute("""CREATE TABLE IF NOT EXISTS customers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS invoices(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    total REAL,
    date TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS invoice_items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price REAL
)""")

conn.commit()

# -------------------------
# Default Owner
# -------------------------
def create_owner():
    c.execute("SELECT * FROM users WHERE username='owner'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (NULL,?,?,?)",
                  ("owner","owner123","Owner"))
        conn.commit()

create_owner()

# -------------------------
# Login
# -------------------------
def login():
    st.title("Chinthaka Computers POS")
    st.subheader("Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = c.fetchone()
        if user:
            st.session_state.user = user
            st.experimental_rerun()
        else:
            st.error("Invalid login")

if "user" not in st.session_state:
    login()
    st.stop()

user = st.session_state.user
st.sidebar.success(f"Logged as {user[1]} ({user[3]})")

menu = ["Dashboard","Products","Customers","Billing","Reports","Users"]
choice = st.sidebar.selectbox("Menu", menu)

# -------------------------
# Dashboard
# -------------------------
if choice=="Dashboard":
    st.header("Dashboard")
    p = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    cu = c.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    i = c.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
    st.metric("Products", p)
    st.metric("Customers", cu)
    st.metric("Invoices", i)

# -------------------------
# Products
# -------------------------
elif choice=="Products":
    st.header("Products")
    tab = st.selectbox("Action",["View","Add","Update Stock","Delete"])

    if tab=="View":
        df = pd.read_sql("SELECT * FROM products", conn)
        st.dataframe(df)

    if tab=="Add":
        n = st.text_input("Name")
        cat = st.text_input("Category")
        pr = st.number_input("Price",0.0)
        stc = st.number_input("Stock",0)
        if st.button("Save"):
            c.execute("INSERT INTO products VALUES(NULL,?,?,?,?)",
                      (n,cat,pr,stc))
            conn.commit()
            st.success("Added")

    if tab=="Update Stock":
        df = pd.read_sql("SELECT * FROM products", conn)
        pid = st.selectbox("Product", df["id"])
        new = st.number_input("New stock",0)
        if st.button("Update"):
            c.execute("UPDATE products SET stock=? WHERE id=?", (new,pid))
            conn.commit()
            st.success("Updated")

    if tab=="Delete":
        df = pd.read_sql("SELECT * FROM products", conn)
        pid = st.selectbox("Delete product", df["id"])
        if st.button("Delete"):
            c.execute("DELETE FROM products WHERE id=?", (pid,))
            conn.commit()
            st.success("Deleted")

# -------------------------
# Customers
# -------------------------
elif choice=="Customers":
    st.header("Customers")
    t = st.selectbox("Action",["View","Add"])
    if t=="View":
        df = pd.read_sql("SELECT * FROM customers", conn)
        st.dataframe(df)
    if t=="Add":
        n = st.text_input("Name")
        ph = st.text_input("Phone")
        if st.button("Save"):
            c.execute("INSERT INTO customers VALUES(NULL,?,?)",(n,ph))
            conn.commit()
            st.success("Added")

# -------------------------
# Billing
# -------------------------
elif choice=="Billing":
    st.header("Billing")
    dfp = pd.read_sql("SELECT * FROM products", conn)
    dfc = pd.read_sql("SELECT * FROM customers", conn)

    cust = st.selectbox("Customer", dfc["id"])
    cart = []

    for i,row in dfp.iterrows():
        q = st.number_input(f"{row['name']} (Stock {row['stock']})",0)
        if q>0:
            cart.append((row["id"],row["name"],q,row["price"]))

    if st.button("Generate Invoice"):
        total = sum([x[2]*x[3] for x in cart])
        c.execute("INSERT INTO invoices VALUES(NULL,?,?,?)",
                  (cust,total,str(datetime.now())))
        inv_id = c.lastrowid

        for it in cart:
            c.execute("INSERT INTO invoice_items VALUES(NULL,?,?,?,?)",
                      (inv_id,it[0],it[2],it[3]))
            c.execute("UPDATE products SET stock=stock-? WHERE id=?",
                      (it[2],it[0]))

        conn.commit()
        st.success(f"Invoice {inv_id} Total Rs.{total}")

        # PDF
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.drawString(50,800,"Chinthaka Computers")
        pdf.drawString(50,780,f"Invoice #{inv_id}")
        y=740
        for it in cart:
            pdf.drawString(50,y,f"{it[1]} x{it[2]} = Rs.{it[2]*it[3]}")
            y-=20
        pdf.drawString(50,y-20,f"Total Rs.{total}")
        pdf.save()
        st.download_button("Download PDF", buffer.getvalue(),
                           file_name=f"invoice_{inv_id}.pdf")

# -------------------------
# Reports
# -------------------------
elif choice=="Reports":
    df = pd.read_sql("SELECT date,total FROM invoices", conn)
    if len(df)>0:
        df["date"] = pd.to_datetime(df["date"])
        daily = df.groupby(df["date"].dt.date)["total"].sum()
        st.bar_chart(daily)
    else:
        st.info("No data")

# -------------------------
# Users
# -------------------------
elif choice=="Users" and user[3]=="Owner":
    st.header("User Management")
    u = st.text_input("Username")
    p = st.text_input("Password")
    if st.button("Add Staff"):
        c.execute("INSERT INTO users VALUES(NULL,?,?,?)",(u,p,"Staff"))
        conn.commit()
        st.success("Staff added")
