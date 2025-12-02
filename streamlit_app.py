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

if 'email_input' not in st.session_state:
    st.session_state.email_input = ""

if 'pwd_input' not in st.session_state:
    st.session_state.pwd_input = ""

if 'login_submitted' not in st.session_state:
    st.session_state.login_submitted = False

courses = load_courses()

# ——————————————————————————————————————————
# PAGE 1: LOGIN
# ——————————————————————————————————————————

if not st.session_state.logged_in:
    st.title("🔐 Email Sender Login")
    st.markdown("""
**Follow these steps to enable 2-Step Verification and create a Gmail App Password:**

1. **Enable 2-Step Verification**  
   - Go to: https://myaccount.google.com/security  
   - Scroll to **2-Step Verification**, and turn it ON.

2. **Create an App Password**  
   - After enabling 2FA, return to: https://myaccount.google.com/apppasswords    
   - You may be asked to sign in your account.  
   - Under App name write 'Mail'.    
   - Click **Create**.

3. **Copy & Paste**  
   - Google will display a **16-character password**.  
   - **Write the 16 digit code in the app password (with no spaces in between them)**  
   - Even if you paste with spaces, the app will remove them.
""")

    with st.form("login_form"):
        st.text_input("Your Gmail Address", key="email_input")
        st.text_input("16-char App Password", type="password", key="pwd_input")
        submit = st.form_submit_button("Login")
        if submit:
            st.session_state.login_submitted = True

    # Do the actual login OUTSIDE the form after submit
    if st.session_state.login_submitted:
        if st.session_state.email_input != "" and st.session_state.pwd_input != "":

            # ✅ REMOVE ALL SPACES from password (leading, trailing, and in between)
            cleaned_password = st.session_state.pwd_input.replace(" ", "")

            # (Optional) you can also strip outer spaces from email
            st.session_state.email = st.session_state.email_input.strip()
            st.session_state.password = cleaned_password

            st.session_state.logged_in = True
            st.session_state.login_submitted = False  # Reset for safety
            st.rerun()
        else:
            st.warning("Please fill in both email and password!")

# ——————————————————————————————————————————
# PAGE 2: COURSE FORM & SEND BUTTONS
# ——————————————————————————————————————————

else:
    st.title("📚 Course Request")

    # Logout button
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.session_state.password = ""
            st.session_state.email_input = ""
            st.session_state.pwd_input = ""
            st.rerun()

    # Student info
    user_name = st.text_input("Your Name", key="name")
    user_roll = st.text_input("Your Roll Number", key="roll")
    year = st.selectbox("Year of Study", ["1st", "2nd", "3rd", "4th", "5th"], key="year")

    # Course selection
    course_map = {c['name']: c for c in courses}
    sel = st.multiselect("Select Courses", list(course_map.keys()), key="sel_courses")

    st.markdown("---")
    st.write("#### Send individual emails:")

    # For each selected course, show prof + send button
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
                        st.success(f"Sent to {r['email']}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Optional “Send All” master button
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
