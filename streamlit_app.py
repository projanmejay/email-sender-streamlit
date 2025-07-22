import streamlit as st
import smtplib
import json
from email.message import EmailMessage

# ——————————————————————————————————————————
# HELPERS
# ——————————————————————————————————————————

def load_courses():
    with open('data/courses.json') as f:
        return json.load(f)

def send_email(sender_email, sender_password, course, receiver, user_name, user_roll, year):
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = receiver['email']
    msg['Subject'] = f"Course Request: {course['code']}"

    template = (
        "{0},\n\n"
        "I am {1}, {2}, a {5} year student and I have applied for your course '{3}' ({4}). "
        "I am eagerly interested in this topic and I hope you will approve my request.\n\n"
        "Thank You\n"
        "{1}\n{2}"
    )
    body = template.format(
        receiver['salutation'],
        user_name,
        user_roll,
        course['name'],
        course['code'],
        year
    )
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

# ——————————————————————————————————————————
# STATE SETUP
# ——————————————————————————————————————————

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

courses = load_courses()

# ——————————————————————————————————————————
# PAGE 1: LOGIN PAGE
# ——————————————————————————————————————————

if not st.session_state.logged_in:
    st.title("🔐 Email Sender Login")
    st.markdown("""
**Follow these steps to enable 2‑Step Verification and create a Gmail App Password:**

1. **Enable 2‑Step Verification**  
   - Go to: https://myaccount.google.com/security  
   - Scroll to **2‑Step Verification**, and turn it ON.

2. **Create an App Password**  
   - After enabling 2FA, go to: https://myaccount.google.com/apppasswords  
   - Under App name write 'Mail'.  
   - Click **Create**.

3. **Copy & Paste**  
   - Use the 16-character code here (no spaces).
""")

    with st.form("login_form"):
        email_in = st.text_input("Your Gmail Address", key="email_input")
        pwd_in   = st.text_input("16‑char App Password", type="password", key="pwd_input")
        submit   = st.form_submit_button("Login")

    if submit:
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(email_in, pwd_in)
            st.session_state.email = email_in
            st.session_state.password = pwd_in
            st.session_state.logged_in = True
            st.experimental_rerun()
            st.stop()  # stop running so the page refreshes immediately
        except Exception as e:
            st.error("❌ Login failed: Please check your email and app password.")

# ——————————————————————————————————————————
# PAGE 2: COURSE SELECTION + EMAIL SEND
# ——————————————————————————————————————————

else:
    st.title("📚 Course Request")

    # Optional logout button
    if st.button("🚪 Logout"):
        for key in ['logged_in', 'email', 'password']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("Logged out successfully.")
        st.experimental_rerun()

    st.success(f"Logged in as: {st.session_state.email}")

    # Student info
    user_name = st.text_input("Your Name", key="name")
    user_roll = st.text_input("Your Roll Number", key="roll")
    year      = st.selectbox("Year of Study", ["1st", "2nd", "3rd", "4th", "5th"], key="year")

    # Course selection
    course_map = {c['name']: c for c in courses}
    sel = st.multiselect("Select Courses", list(course_map.keys()), key="sel_courses")

    st.markdown("---")
    st.write("#### Send individual emails:")

    # Send button for each selected course's professor(s)
    for course_name in sel:
        crs = course_map[course_name]
        st.subheader(f"{crs['name']} ({crs['code']})")

        for r in crs['receivers']:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"👤 **{r['salutation']}** — {r['email']}")
            with col2:
                btn_key = f"send_{crs['code']}_{r['email']}"
                if st.button("Send", key=btn_key):
                    try:
                        send_email(
                            st.session_state.email,
                            st.session_state.password,
                            crs, r,
                            user_name, user_roll, year
                        )
                        st.success(f"✅ Sent to {r['email']}")
                    except Exception as e:
                        st.error(f"❌ Error sending to {r['email']}: {e}")

    # Batch send option
    if st.button("📨 Send All Selected at Once"):
        report = []
        for course_name in sel:
            crs = course_map[course_name]
            for r in crs['receivers']:
                try:
                    send_email(
                        st.session_state.email,
                        st.session_state.password,
                        crs, r,
                        user_name, user_roll, year
                    )
                    report.append(f"✅ {crs['code']} → {r['email']}")
                except Exception as e:
                    report.append(f"❌ {crs['code']} → {r['email']}: {e}")
        st.write("### Batch Send Report")
        for line in report:
            st.write(line)
