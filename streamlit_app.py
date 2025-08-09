import streamlit as st
import smtplib
import json
from email.message import EmailMessage

# ——————————————————————————————————————————
# HELPERS
# ——————————————————————————————————————————

def load_courses():
    try:
        with open('data/courses.json') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Could not find data/courses.json")
        return []
    except json.JSONDecodeError:
        st.error("❌ courses.json is not valid JSON")
        return []

def send_email(sender_email, sender_password, course, receiver, user_name, user_roll, year,
               venue, whatsapp_link, group_number, contact_info):
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = receiver['email']
    msg['Subject'] = "Invitation to Buddy Interaction Event"

    html_body = f"""
    <html>
    <body style="font-family:Arial, sans-serif; font-size:14px; color:#333;">
        <p>Hello Freshers!</p>

        <p>You were wrong if you thought all the “fresher fun” was over! Once again, IWG is ecstatic to welcome you to our lively and diverse community.
        As you continue this thrilling adventure, we understand that transitioning to a new environment can be both exciting and daunting. 
        To ease this transition and help you connect with your fellow batchmates and seniors, the Institute Wellness Group has come up with yet another edition of our yearly fresher’s exclusive event called <b>Buddy Interaction</b>.</p>

        <p>Still got that “New to Campus” excitement in you? That desire to keep meeting more people, to make more friends. We’ve been there and we’ve felt it all. 
        So Institute Wellness Group is back with another edition of our yearly fresher’s exclusive event, <b>Buddy Interaction</b>. 
        It's a chance to make new friends, diversify your friend group and have a fun time interacting with your batchies. 
        So do not forget to join us at the below given time and place.</p>

        <p><b>Event Details:</b><br>
        Date: 10th of August’25<br>
        Time: 2:30 pm<br>
        Venue: {venue}<br>
        WhatsApp Group: <a href="{whatsapp_link}">{whatsapp_link}</a><br>
        Group Number: {group_number}</p>

        <p>At "Buddy Interaction," you'll have the opportunity to spend a lovely afternoon filled with lifelong memories with fellow freshers and seniors, learn about the campus, and ask any questions.
        It's a great chance to build friendships and gain valuable insights into life at IIT Kharagpur.</p>

        <p>Should you have any questions or need assistance, please feel free to contact the following individuals:<br>
        {contact_info}</p>

        <p>We look forward to meeting you at the event and helping you settle into your new home. Once again, welcome to IIT Kharagpur!</p>

        <p>Warm regards,<br>
        Institute Wellness Group</p>

        <!-- Signature Image from URL -->
        <img src="https://drive.google.com/file/d/1QFC9CCaswWw1YYAdjwushY6CM9XDhv65/view?usp=sharing" alt="Signature" style="max-width:600px; margin-top:10px;"><br>

        <!-- Signature Text -->
        <p style="margin-top:5px;">
            <b>Janmejay Bhuyan</b><br>
            Student Member<br>
            Institute Wellness Group<br>
            Technology Students' Gymkhana<br>
            Indian Institute of Technology Kharagpur<br>
            Contact No.: 9556418889<br>
            Connect: 
            <a href="https://www.linkedin.com/company/institute-wellness-group-iit-kharagpur/">LinkedIn</a> | 
            <a href="https://www.facebook.com/iwg.iitkgp?mibextid=ZbWKwL">Facebook</a> | 
            <a href="mailto:janmejay.iwg@gmail.com">Email</a> | 
            <a href="https://www.instagram.com/iwg_iitkgp?igsh=bG9saWswN201OWdq">Instagram</a>
        </p>
    </body>
    </html>
    """

    msg.set_content("Please enable HTML to view this email properly.")
    msg.add_alternative(html_body, subtype="html")

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
**How to Enable Gmail for Sending Emails:**

1. **Enable 2-Step Verification**  
   - https://myaccount.google.com/security

2. **Generate App Password**  
   - https://myaccount.google.com/apppasswords  
   - Choose 'Mail' as the app and 'Other' for the device.

3. **Copy the 16-character password without spaces**
""")

    with st.form("login_form"):
        st.text_input("Your Gmail Address", key="email_input")
        st.text_input("16-character App Password", type="password", key="pwd_input")
        submit = st.form_submit_button("Login")
        if submit:
            st.session_state.login_submitted = True

    if st.session_state.login_submitted:
        if st.session_state.email_input and st.session_state.pwd_input:
            st.session_state.email = st.session_state.email_input
            st.session_state.password = st.session_state.pwd_input
            st.session_state.logged_in = True
            st.session_state.login_submitted = False
            st.rerun()
        else:
            st.warning("Please enter both email and password.")

# ——————————————————————————————————————————
# PAGE 2: EVENT EMAIL FORM
# ——————————————————————————————————————————

else:
    st.title("📨 Buddy Interaction Email Sender")

    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🔓 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown("#### 👤 Your Details")
    user_name = st.text_input("Your Name", key="name")
    user_roll = st.text_input("Your Roll Number", key="roll")
    year = st.selectbox("Year of Study", ["1st", "2nd", "3rd", "4th", "5th"], key="year")

    st.markdown("#### 📍 Event Details")
    venue = st.text_input("Venue", key="venue")
    whatsapp_link = st.text_input("WhatsApp Group Link", key="wa_link")
    group_number = st.text_input("Group Number", key="group_no")
    contact_info = st.text_area("Contact Info (e.g., names + numbers)", key="contact_info")

    st.markdown("#### 📚 Select Courses / Professors to Send To")
    course_map = {c['name']: c for c in courses}
    sel = st.multiselect("Select Courses", list(course_map.keys()), key="sel_courses")

    st.markdown("---")
    st.write("#### Send individual emails:")

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
                            user_name, user_roll, year,
                            venue, whatsapp_link, group_number, contact_info
                        )
                        st.success(f"Sent to {r['email']}")
                    except Exception as e:
                        st.error(f"Error: {e}")

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
                        user_name, user_roll, year,
                        venue, whatsapp_link, group_number, contact_info
                    )
                    report.append(f"✅ {crs['code']} → {r['email']}")
                except Exception as e:
                    report.append(f"❌ {crs['code']} → {r['email']}: {e}")
        st.write("### Batch Send Report")
        for line in report:
            st.write(line)
