import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import os

# Path to credentials JSON
CREDS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "Confidential Files",
    "fitforlifegym-4e763a4acd58.json"
)

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_NAME = "Gym_Database"

# Default fee data (matches the pricing chart)
DEFAULT_FEES = [
    {"Plan": "Basic",    "Duration": "1 Month",   "Admission_Fees": 1000, "Monthly_Rate": 600, "Months": 1,  "Total": 1600},
    {"Plan": "Silver",   "Duration": "3 Months",  "Admission_Fees": 700,  "Monthly_Rate": 600, "Months": 3,  "Total": 2500},
    {"Plan": "Gold",     "Duration": "6 Months",  "Admission_Fees": 0,    "Monthly_Rate": 600, "Months": 6,  "Total": 3600},
    {"Plan": "Platinum", "Duration": "1 Year",    "Admission_Fees": 0,    "Monthly_Rate": 500, "Months": 12, "Total": 6000},
]


@st.cache_resource(show_spinner=False)
def get_client():
    """Return an authenticated gspread client (cached across sessions)."""
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet():
    client = get_client()
    return client.open(SHEET_NAME)


# ── Members ──────────────────────────────────────────────────────────────────

def get_members_sheet():
    return get_spreadsheet().worksheet("Members")


def get_members_df() -> pd.DataFrame:
    ws = get_members_sheet()
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(columns=[
            "ID", "Name", "Phone", "Email", "Plan",
            "Start_Date", "Expiry_Date", "Total_Paid", "Status"
        ])
    return pd.DataFrame(data)


def find_member_by_phone(phone: str) -> dict | None:
    df = get_members_df()
    df["Phone"] = df["Phone"].astype(str).str.strip()
    match = df[df["Phone"] == str(phone).strip()]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def add_member(row: dict):
    ws = get_members_sheet()
    # Auto-generate ID
    df = get_members_df()
    new_id = int(df["ID"].max()) + 1 if not df.empty and "ID" in df.columns else 1
    row["ID"] = new_id
    ws.append_row([
        row.get("ID"), row.get("Name"), row.get("Phone"), row.get("Email", ""),
        row.get("Plan"), row.get("Start_Date"), row.get("Expiry_Date"),
        row.get("Total_Paid"), row.get("Status", "Active")
    ])
    return new_id


def update_member(row_index_1based: int, updated: dict):
    """row_index_1based: 1 = header, 2 = first data row."""
    ws = get_members_sheet()
    headers = ws.row_values(1)
    for col_idx, header in enumerate(headers, start=1):
        if header in updated:
            ws.update_cell(row_index_1based, col_idx, updated[header])


def delete_member(row_index_1based: int):
    ws = get_members_sheet()
    ws.delete_rows(row_index_1based)


def get_member_row_index(member_id) -> int:
    """Returns the 1-based sheet row for the given member ID (includes header)."""
    ws = get_members_sheet()
    ids = ws.col_values(1)  # column A = ID
    for i, val in enumerate(ids):
        if str(val) == str(member_id):
            return i + 1  # 1-based
    return -1


# ── Fees ─────────────────────────────────────────────────────────────────────

def get_fees_sheet():
    return get_spreadsheet().worksheet("Fees")


def get_fees_df() -> pd.DataFrame:
    ws = get_fees_sheet()
    data = ws.get_all_records()
    if not data:
        return pd.DataFrame(DEFAULT_FEES)
    df = pd.DataFrame(data)
    # Normalize column names: strip spaces, fix casing to match expected names
    expected = ["Plan", "Duration", "Admission_Fees", "Monthly_Rate", "Months", "Total"]
    rename_map = {col: next((e for e in expected if e.lower() == col.strip().lower()), col.strip())
                  for col in df.columns}
    df = df.rename(columns=rename_map)
    # If Plan column is still missing, fall back to defaults
    if "Plan" not in df.columns:
        return pd.DataFrame(DEFAULT_FEES)
    return df


def update_fees_row(row_index_1based: int, updated: dict):
    ws = get_fees_sheet()
    headers = ws.row_values(1)
    for col_idx, header in enumerate(headers, start=1):
        if header in updated:
            ws.update_cell(row_index_1based, col_idx, updated[header])


def seed_fees_sheet():
    """Populate the Fees sheet with default data if it is empty or missing the Plan column."""
    ws = get_fees_sheet()
    existing = ws.get_all_records()
    if existing:
        # Check if Plan column exists (case-insensitive)
        keys = list(existing[0].keys())
        if any(k.strip().lower() == "plan" for k in keys):
            return  # already properly seeded
    # Clear and rewrite with correct headers
    ws.clear()
    headers = list(DEFAULT_FEES[0].keys())
    ws.append_row(headers)
    for row in DEFAULT_FEES:
        ws.append_row(list(row.values()))


# ── Admin ─────────────────────────────────────────────────────────────────────

def get_admins_sheet():
    return get_spreadsheet().worksheet("Admin")


def get_admins() -> list[dict]:
    ws = get_admins_sheet()
    return ws.get_all_records()
