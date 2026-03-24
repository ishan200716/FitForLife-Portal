"""
Fit For Life Gym Portal — app.py
Orange & Black themed Streamlit app.
Member login + Admin dashboard backed by Google Sheets.
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from PIL import Image

from utils.sheets import (
    find_member_by_phone, get_members_df, add_member,
    update_member, delete_member, get_member_row_index,
    get_fees_df, update_fees_row, seed_fees_sheet,
    get_admins,
)
from utils.auth import check_admin_login

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fit For Life Gym",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---- Fonts ---- */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* ---- Background ---- */
.stApp {
    background: #0D0D0D;
}

/* ---- Hide Streamlit chrome ---- */
#MainMenu, footer, header { visibility: hidden; }

/* ---- Orange accent headings ---- */
h1, h2, h3 { color: #FF6B00 !important; }

/* ---- Cards ---- */
.card {
    background: linear-gradient(135deg, #1a1a1a, #242424);
    border: 1px solid #FF6B00;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 18px;
    box-shadow: 0 4px 24px rgba(255,107,0,0.12);
}
.card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #FF6B00;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.card-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #fff;
}
.card-sub {
    font-size: 0.85rem;
    color: #aaa;
    margin-top: 2px;
}

/* ---- Status badges ---- */
.badge-active {
    background: #1a4a1a;
    color: #4cff7a;
    border: 1px solid #4cff7a;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
}
.badge-expired {
    background: #4a1a1a;
    color: #ff4c4c;
    border: 1px solid #ff4c4c;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
}

/* ---- Plan cards (pricing) ---- */
.plan-card {
    background: linear-gradient(145deg, #1e1e1e, #262626);
    border: 2px solid #FF6B00;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    height: 100%;
    box-shadow: 0 0 18px rgba(255,107,0,0.15);
    transition: transform 0.2s, box-shadow 0.2s;
}
.plan-card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(255,107,0,0.3); }
.plan-name { font-size: 1.4rem; font-weight: 800; color: #FF6B00; margin-bottom: 4px; }
.plan-duration { font-size: 0.8rem; color: #aaa; margin-bottom: 14px; }
.plan-total { font-size: 2.2rem; font-weight: 800; color: #fff; }
.plan-detail { font-size: 0.82rem; color: #ccc; margin-top: 6px; line-height: 1.6; }

/* ---- Member info card ---- */
.member-card {
    background: linear-gradient(135deg, #1a1a1a 0%, #242424 100%);
    border: 2px solid #FF6B00;
    border-radius: 18px;
    padding: 32px;
    margin: 0 auto;
    max-width: 600px;
    box-shadow: 0 0 40px rgba(255,107,0,0.20);
}
.member-name { font-size: 2rem; font-weight: 800; color: #FF6B00; margin-bottom: 4px; }
.member-plan { font-size: 1rem; color: #aaa; margin-bottom: 18px; }
.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #2e2e2e;
    padding: 10px 0;
    font-size: 0.95rem;
}
.info-label { color: #888; }
.info-val { color: #fff; font-weight: 600; }

/* ---- Buttons ---- */
.stButton > button {
    background: linear-gradient(90deg, #FF6B00, #ff8c00) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    padding: 10px 28px !important;
    font-size: 1rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ---- Inputs ---- */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stNumberInput > div > div > input {
    background: #1e1e1e !important;
    color: #fff !important;
    border: 1px solid #FF6B00 !important;
    border-radius: 8px !important;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1a1a;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #aaa !important;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #FF6B00 !important;
    border-radius: 8px !important;
    color: #fff !important;
}

/* ---- Divider ---- */
hr { border-color: #2e2e2e !important; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: #111 !important;
    border-right: 1px solid #2e2e2e;
}

/* ---- Top banner ---- */
.top-banner {
    background: linear-gradient(90deg, #FF6B00 0%, #cc4a00 100%);
    border-radius: 14px;
    padding: 18px 28px;
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 28px;
}
.banner-title { font-size: 2rem; font-weight: 900; color: #fff; }
.banner-sub { font-size: 0.95rem; color: rgba(255,255,255,0.8); }

/* ---- Dataframe ---- */
[data-testid="stDataFrame"] {
    border: 1px solid #FF6B00;
    border-radius: 10px;
    overflow: hidden;
}

/* ---- Metric ---- */
[data-testid="stMetric"] {
    background: #1a1a1a;
    border: 1px solid #2e2e2e;
    border-radius: 12px;
    padding: 16px !important;
}
[data-testid="stMetricValue"] { color: #FF6B00 !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

PLAN_COLORS = {
    "Basic": "#CD7F32",
    "Silver": "#C0C0C0",
    "Gold": "#FFD700",
    "Platinum": "#A8D8EA",
}

DEFAULT_FEES_INFO = {
    "Basic":    {"Duration": "1 Month",  "Admission_Fees": 1000, "Monthly_Rate": 600, "Months": 1,  "Total": 1600},
    "Silver":   {"Duration": "3 Months", "Admission_Fees": 700,  "Monthly_Rate": 600, "Months": 3,  "Total": 2500},
    "Gold":     {"Duration": "6 Months", "Admission_Fees": 0,    "Monthly_Rate": 600, "Months": 6,  "Total": 3600},
    "Platinum": {"Duration": "1 Year",   "Admission_Fees": 0,    "Monthly_Rate": 500, "Months": 12, "Total": 6000},
}


def logo_sidebar():
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, width=120)
    st.sidebar.markdown(
        "<h2 style='color:#FF6B00;margin-top:0'>Fit For Life</h2>"
        "<p style='color:#aaa;font-size:0.85rem'>Unisex Gym Portal</p>",
        unsafe_allow_html=True,
    )


def top_banner(title: str, subtitle: str = ""):
    logo_html = ""
    st.markdown(
        f"""<div class='top-banner'>
            <div>
                <div class='banner-title'>🏋️ {title}</div>
                {'<div class="banner-sub">' + subtitle + '</div>' if subtitle else ''}
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def days_remaining(expiry_str: str) -> int:
    try:
        exp = datetime.strptime(str(expiry_str).strip(), "%Y-%m-%d").date()
        return (exp - date.today()).days
    except Exception:
        return 0


def status_badge(status: str, expiry_str: str) -> str:
    days = days_remaining(expiry_str)
    if str(status).strip().lower() == "active" and days >= 0:
        return f"<span class='badge-active'>✅ ACTIVE ({days}d left)</span>"
    return "<span class='badge-expired'>❌ EXPIRED</span>"


# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "home",           # home | member | admin
        "member_data": None,
        "admin_logged_in": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
def page_home():
    top_banner("Fit For Life Gym", "Welcome to the Member & Admin Portal")

    # -- Pricing section --
    st.markdown("## 🏆 Our Membership Plans")
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        fees_df = get_fees_df()
        fees_dict = {row["Plan"]: row for _, row in fees_df.iterrows()}
    except Exception:
        fees_dict = {k: {**{"Plan": k}, **v} for k, v in DEFAULT_FEES_INFO.items()}

    cols = st.columns(4, gap="large")
    plan_order = ["Basic", "Silver", "Gold", "Platinum"]
    plan_icons = {"Basic": "🥉", "Silver": "🥈", "Gold": "🥇", "Platinum": "💎"}
    plan_admission_label = {
        "Basic":    "Admission: ₹1,000",
        "Silver":   "Admission: ₹700",
        "Gold":     "No Admission Fees",
        "Platinum": "No Admission Fees",
    }

    for col, plan in zip(cols, plan_order):
        info = fees_dict.get(plan, DEFAULT_FEES_INFO.get(plan, {}))
        admission = int(info.get("Admission_Fees", 0))
        rate = int(info.get("Monthly_Rate", 0))
        months = int(info.get("Months", 1))
        total = int(info.get("Total", 0))
        duration = info.get("Duration", "")
        adm_label = "No Admission Fees" if admission == 0 else f"Admission: ₹{admission:,}"
        with col:
            st.markdown(f"""
            <div class='plan-card'>
                <div class='plan-name'>{plan_icons[plan]} {plan}</div>
                <div class='plan-duration'>{duration}</div>
                <div class='plan-total'>₹{total:,}</div>
                <div class='plan-detail'>
                    {adm_label}<br>
                    ₹{rate}/mo × {months} months
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # -- Login section --
    st.markdown("## 🔐 Access Your Portal")
    col_m, col_a, col_empty = st.columns([1, 1, 1])

    with col_m:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### 👤 Member Login")
        st.markdown("Enter your registered phone number to view your membership details.")
        if st.button("Member Login →", key="btn_member_login", use_container_width=True):
            st.session_state["page"] = "member"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_a:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### 🛡️ Admin Login")
        st.markdown("Admin access to manage members and update membership fees.")
        if st.button("Admin Dashboard →", key="btn_admin_login", use_container_width=True):
            st.session_state["page"] = "admin"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MEMBER LOGIN & DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_member():
    logo_sidebar()
    if st.sidebar.button("← Back to Home"):
        st.session_state["page"] = "home"
        st.session_state["member_data"] = None
        st.rerun()

    top_banner("Member Portal", "Check your membership status")

    if st.session_state["member_data"] is None:
        # ---- Login form ----
        st.markdown("<br>", unsafe_allow_html=True)
        col_form, _, _ = st.columns([1.2, 0.4, 1.4])
        with col_form:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📱 Enter Your Phone Number")
            phone = st.text_input("Registered Phone Number", placeholder="e.g. 9876543210", key="member_phone")
            if st.button("View My Membership", use_container_width=True):
                if not phone.strip():
                    st.warning("Please enter your phone number.")
                else:
                    with st.spinner("Fetching your details…"):
                        member = find_member_by_phone(phone.strip())
                    if member is None:
                        st.error("❌ No member found with that phone number. Please contact the gym.")
                    else:
                        st.session_state["member_data"] = member
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # ---- Member dashboard ----
        m = st.session_state["member_data"]
        plan = str(m.get("Plan", "Basic"))
        status = str(m.get("Status", "Active"))
        expiry = str(m.get("Expiry_Date", ""))

        st.markdown("<br>", unsafe_allow_html=True)
        col_card, col_right = st.columns([1.2, 1])

        with col_card:
            st.markdown(f"""
            <div class='member-card'>
                <div class='member-name'>{m.get("Name", "N/A")}</div>
                <div class='member-plan'>🏅 {plan} Plan Member</div>
                {status_badge(status, expiry)}
                <br><br>
                <div class='info-row'>
                    <span class='info-label'>📱 Phone</span>
                    <span class='info-val'>{m.get("Phone", "—")}</span>
                </div>
                <div class='info-row'>
                    <span class='info-label'>✉️ Email</span>
                    <span class='info-val'>{m.get("Email", "—")}</span>
                </div>
                <div class='info-row'>
                    <span class='info-label'>📅 Start Date</span>
                    <span class='info-val'>{m.get("Start_Date", "—")}</span>
                </div>
                <div class='info-row'>
                    <span class='info-label'>⏳ Expiry Date</span>
                    <span class='info-val'>{expiry}</span>
                </div>
                <div class='info-row' style='border:none'>
                    <span class='info-label'>💰 Total Paid</span>
                    <span class='info-val' style='color:#FF6B00;font-size:1.2rem'>₹{int(float(m.get("Total_Paid", 0))):,}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_right:
            # Renewal info
            st.markdown("### 💡 Plan Details")
            try:
                fees_df = get_fees_df()
                plan_row = fees_df[fees_df["Plan"] == plan]
                if not plan_row.empty:
                    pr = plan_row.iloc[0]
                    adm = int(pr.get("Admission_Fees", 0))
                    rate = int(pr.get("Monthly_Rate", 0))
                    months = int(pr.get("Months", 1))
                    total = int(pr.get("Total", 0))
                    st.markdown(f"""
                    <div class='card'>
                        <div class='card-title'>Current Plan</div>
                        <div class='card-value'>{plan}</div>
                        <div class='card-sub'>{pr.get("Duration","")}</div>
                    </div>
                    <div class='card'>
                        <div class='card-title'>Renewal Cost</div>
                        <div class='card-value'>₹{total:,}</div>
                        <div class='card-sub'>{"Admission: ₹"+str(adm)+" + " if adm else "No Admission + "}₹{rate}/mo × {months}mo</div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception:
                pass

            days = days_remaining(expiry)
            if days < 7 and days >= 0:
                st.warning(f"⚠️ Your membership expires in **{days} day(s)**! Please renew soon.")
            elif days < 0:
                st.error("🔴 Your membership has **expired**. Contact the gym to renew.")

        if st.button("🔓 Logout"):
            st.session_state["member_data"] = None
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADMIN LOGIN & DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_admin():
    logo_sidebar()
    if st.sidebar.button("← Back to Home"):
        st.session_state["page"] = "home"
        st.session_state["admin_logged_in"] = False
        st.rerun()

    if not st.session_state["admin_logged_in"]:
        top_banner("Admin Login", "Restricted Access")
        st.markdown("<br>", unsafe_allow_html=True)
        col_form, _, _ = st.columns([1.2, 0.4, 1.4])
        with col_form:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🛡️ Admin Credentials")
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            if st.button("Login as Admin", use_container_width=True):
                if not username or not password:
                    st.warning("Please enter username and password.")
                else:
                    with st.spinner("Verifying…"):
                        admins = get_admins()
                    if check_admin_login(username, password, admins):
                        st.session_state["admin_logged_in"] = True
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")
            st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Admin Dashboard ────────────────────────────────────────────────────
    top_banner("Admin Dashboard", "Fit For Life Gym — Management Panel")

    # Sidebar logout
    if st.sidebar.button("🔓 Logout", key="admin_logout"):
        st.session_state["admin_logged_in"] = False
        st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.markdown("<small style='color:#888'>Logged in as Admin</small>", unsafe_allow_html=True)

    tab_overview, tab_members, tab_add, tab_fees = st.tabs([
        "📊 Overview", "👥 Members", "➕ Add Member", "💰 Edit Fees"
    ])

    # ── Tab 1: Overview ────────────────────────────────────────────────────
    with tab_overview:
        st.markdown("### Gym at a Glance")
        with st.spinner("Loading data…"):
            try:
                df = get_members_df()
            except Exception as e:
                st.error(f"Error loading members: {e}")
                df = pd.DataFrame()

        if df.empty:
            st.info("No members yet. Add your first member in the **Add Member** tab.")
        else:
            total = len(df)
            active = len(df[df["Status"].str.strip().str.lower() == "active"]) if "Status" in df.columns else 0
            expired = total - active
            total_revenue = df["Total_Paid"].astype(float).sum() if "Total_Paid" in df.columns else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Members", total)
            c2.metric("Active", active)
            c3.metric("Expired", expired)
            c4.metric("Total Revenue", f"₹{int(total_revenue):,}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Members by Plan")
            if "Plan" in df.columns:
                plan_counts = df["Plan"].value_counts().reset_index()
                plan_counts.columns = ["Plan", "Count"]
                st.dataframe(plan_counts, use_container_width=True, hide_index=True)

            st.markdown("#### Expiring Within 7 Days")
            if "Expiry_Date" in df.columns:
                def days_left(row):
                    try:
                        return (datetime.strptime(str(row["Expiry_Date"]).strip(), "%Y-%m-%d").date() - date.today()).days
                    except Exception:
                        return -999
                df["Days_Left"] = df.apply(days_left, axis=1)
                expiring_soon = df[(df["Days_Left"] >= 0) & (df["Days_Left"] <= 7)]
                if expiring_soon.empty:
                    st.success("✅ No memberships expiring within 7 days.")
                else:
                    st.dataframe(
                        expiring_soon[["Name", "Phone", "Plan", "Expiry_Date", "Days_Left"]],
                        use_container_width=True, hide_index=True
                    )

    # ── Tab 2: Manage Members ──────────────────────────────────────────────
    with tab_members:
        st.markdown("### All Members")
        with st.spinner("Loading members…"):
            try:
                df = get_members_df()
            except Exception as e:
                st.error(f"Error: {e}")
                df = pd.DataFrame()

        if df.empty:
            st.info("No members found.")
        else:
            search = st.text_input("🔍 Search by Name or Phone", placeholder="Type to filter…")
            if search:
                mask = (
                    df["Name"].astype(str).str.contains(search, case=False, na=False) |
                    df["Phone"].astype(str).str.contains(search, case=False, na=False)
                )
                display_df = df[mask]
            else:
                display_df = df

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("#### ✏️ Edit Member")
            if not df.empty:
                member_options = {
                    f"{row['Name']} ({row['Phone']})": row["ID"]
                    for _, row in df.iterrows()
                }
                selected_label = st.selectbox("Select Member to Edit", list(member_options.keys()))
                selected_id = member_options[selected_label]
                m_row = df[df["ID"].astype(str) == str(selected_id)].iloc[0]

                with st.form("edit_member_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name   = st.text_input("Name", value=str(m_row.get("Name", "")))
                        new_phone  = st.text_input("Phone", value=str(m_row.get("Phone", "")))
                        new_email  = st.text_input("Email", value=str(m_row.get("Email", "")))
                        new_plan   = st.selectbox("Plan", ["Basic", "Silver", "Gold", "Platinum"],
                                                  index=["Basic","Silver","Gold","Platinum"].index(
                                                      str(m_row.get("Plan","Basic"))) if str(m_row.get("Plan","Basic")) in ["Basic","Silver","Gold","Platinum"] else 0)
                    with col2:
                        new_start  = st.text_input("Start Date (YYYY-MM-DD)", value=str(m_row.get("Start_Date", "")))
                        new_expiry = st.text_input("Expiry Date (YYYY-MM-DD)", value=str(m_row.get("Expiry_Date", "")))
                        new_paid   = st.number_input("Total Paid (₹)", value=float(m_row.get("Total_Paid", 0)), step=100.0)
                        new_status = st.selectbox("Status", ["Active", "Expired"],
                                                  index=0 if str(m_row.get("Status","Active")).strip().lower()=="active" else 1)

                    submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
                    if submitted:
                        row_idx = get_member_row_index(selected_id)
                        if row_idx == -1:
                            st.error("Could not find member row in sheet.")
                        else:
                            update_member(row_idx, {
                                "Name": new_name, "Phone": new_phone, "Email": new_email,
                                "Plan": new_plan, "Start_Date": new_start, "Expiry_Date": new_expiry,
                                "Total_Paid": new_paid, "Status": new_status,
                            })
                            st.success(f"✅ Member **{new_name}** updated successfully!")
                            st.rerun()

                st.markdown("---")
                st.markdown("#### 🗑️ Deactivate / Delete Member")
                del_label = st.selectbox("Select Member to Remove", list(member_options.keys()), key="del_sel")
                del_id = member_options[del_label]
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    if st.button("⚠️ Mark as Expired", use_container_width=True):
                        row_idx = get_member_row_index(del_id)
                        if row_idx != -1:
                            update_member(row_idx, {"Status": "Expired"})
                            st.success("Member marked as Expired.")
                            st.rerun()
                with col_d2:
                    if st.button("🗑️ Delete Permanently", use_container_width=True):
                        row_idx = get_member_row_index(del_id)
                        if row_idx != -1:
                            delete_member(row_idx)
                            st.success("Member deleted.")
                            st.rerun()

    # ── Tab 3: Add Member ──────────────────────────────────────────────────
    with tab_add:
        st.markdown("### ➕ Register New Member")
        with st.form("add_member_form"):
            col1, col2 = st.columns(2)
            with col1:
                a_name  = st.text_input("Full Name *")
                a_phone = st.text_input("Phone Number *")
                a_email = st.text_input("Email (optional)")
                a_plan  = st.selectbox("Membership Plan *", ["Basic", "Silver", "Gold", "Platinum"])
            with col2:
                a_start  = st.date_input("Start Date *", value=date.today())
                # Auto-calculate expiry based on plan
                plan_months = {"Basic": 1, "Silver": 3, "Gold": 6, "Platinum": 12}
                auto_expiry = a_start + timedelta(days=30 * plan_months.get(a_plan, 1))
                a_expiry = st.date_input("Expiry Date *", value=auto_expiry)
                # Fetch fee total
                default_totals = {"Basic": 1600, "Silver": 2500, "Gold": 3600, "Platinum": 6000}
                a_paid = st.number_input("Total Amount Paid (₹) *",
                                         value=float(default_totals.get(a_plan, 1600)), step=100.0)
                a_status = st.selectbox("Status", ["Active", "Expired"])

            add_submitted = st.form_submit_button("✅ Add Member", use_container_width=True)
            if add_submitted:
                if not a_name.strip() or not a_phone.strip():
                    st.error("Name and Phone are required.")
                else:
                    new_id = add_member({
                        "Name": a_name.strip(),
                        "Phone": a_phone.strip(),
                        "Email": a_email.strip(),
                        "Plan": a_plan,
                        "Start_Date": str(a_start),
                        "Expiry_Date": str(a_expiry),
                        "Total_Paid": a_paid,
                        "Status": a_status,
                    })
                    st.success(f"🎉 Member **{a_name}** added with ID **{new_id}**!")

    # ── Tab 4: Edit Fees ───────────────────────────────────────────────────
    with tab_fees:
        st.markdown("### 💰 Edit Membership Fees")
        st.info("Changes here update the **Fees** tab in your Google Sheet and reflect immediately on the home page.")
        with st.spinner("Loading fees…"):
            try:
                seed_fees_sheet()   # ensure headers + data exist before reading
                fees_df = get_fees_df()
            except Exception as e:
                st.error(f"Error loading fees: {e}")
                from utils.sheets import DEFAULT_FEES
                fees_df = pd.DataFrame(DEFAULT_FEES)

        if fees_df.empty:
            st.warning("Fees sheet is empty. It will be seeded with defaults on next load.")
        else:
            plan_order = ["Basic", "Silver", "Gold", "Platinum"]
            plan_icons = {"Basic": "🥉", "Silver": "🥈", "Gold": "🥇", "Platinum": "💎"}

            for plan_name in plan_order:
                plan_rows = fees_df[fees_df["Plan"] == plan_name]
                if plan_rows.empty:
                    continue
                row_sheet_idx = fees_df.index[fees_df["Plan"] == plan_name].tolist()[0] + 2  # +2 for header + 1-based
                pr = plan_rows.iloc[0]

                with st.expander(f"{plan_icons.get(plan_name,'🏅')} **{plan_name} Plan** — Current Total: ₹{int(float(pr.get('Total',0))):,}", expanded=True):
                    fc1, fc2, fc3, fc4 = st.columns(4)
                    with fc1:
                        new_adm = st.number_input(f"Admission Fees (₹)", value=int(float(pr.get("Admission_Fees", 0))),
                                                   step=50, key=f"adm_{plan_name}")
                    with fc2:
                        new_rate = st.number_input(f"Monthly Rate (₹)", value=int(float(pr.get("Monthly_Rate", 0))),
                                                    step=50, key=f"rate_{plan_name}")
                    with fc3:
                        new_months = st.number_input(f"Months", value=int(float(pr.get("Months", 1))),
                                                      step=1, key=f"months_{plan_name}")
                    with fc4:
                        new_total = new_adm + (new_rate * new_months)
                        st.metric("New Total", f"₹{new_total:,}")

                    if st.button(f"💾 Update {plan_name} Plan", key=f"save_{plan_name}", use_container_width=True):
                        update_fees_row(row_sheet_idx, {
                            "Admission_Fees": new_adm,
                            "Monthly_Rate": new_rate,
                            "Months": new_months,
                            "Total": new_total,
                        })
                        st.success(f"✅ {plan_name} plan updated! New total: ₹{new_total:,}")
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
page = st.session_state.get("page", "home")

if page == "home":
    page_home()
elif page == "member":
    page_member()
elif page == "admin":
    page_admin()
