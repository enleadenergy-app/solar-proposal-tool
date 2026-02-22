import streamlit as st
from fpdf import FPDF
import os
import json
import datetime
from PIL import Image

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
PROFILE_FILE = "profile_config.json"
LOGO_FILE = "company_logo.png"
BG_FILE = "company_bg.png"

# ==========================================
# 2. DATA MANAGEMENT (REWRITTEN FOR SECRETS)
# ==========================================

def load_profile():
    """Loads profile from Secrets (Cloud) or Local JSON file."""
    # 1. Start with Default Data
    default_data = {
        "company_name": "Enlead Energy Solutions",
        "mobile": "+91 98765 43210",
        "email": "contact@enlead.com",
        "address": "123 Solar Street, Kochi, Kerala",
        "proposal_heading": "Solar Energy Proposal",
        "sub_heading": "Powering a Sustainable Future",
        "terms_conditions": "1. Warranty: 25 Years Performance.\n2. Validity: 15 days.",
        "bank_name": "HDFC Bank",
        "acc_name": "Enlead Energy Solutions",
        "acc_number": "50200012345678",
        "ifsc_code": "HDFC0001234"
    }

    # 2. Try to load from Streamlit Cloud Secrets (Priority)
    if "company_profile" in st.secrets:
        return dict(st.secrets["company_profile"])

    # 3. Try to load from Local JSON (For local testing)
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except:
            return default_data
            
    return default_data

def save_profile_data(data):
    """Saves data locally. Note: On Streamlit Cloud, use the Secrets tab instead."""
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f, indent=4)
    # Update current session immediately
    st.session_state.profile = data

# ... [Keep your existing save_image and SolarProposalPDF class code here] ...

class SolarProposalPDF(FPDF):
    def __init__(self, profile):
        super().__init__()
        self.profile = profile

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        text = f"Page {self.page_no()} | {self.profile['company_name']} | {self.profile['mobile']}"
        self.cell(0, 10, text, 0, 0, 'C')

# ... [Keep your generate_premium_pdf function exactly as it is] ...

def generate_premium_pdf(profile, customer_info, items, total_amount, payment_schedule):
    # (Copy the entire function from your original code here)
    # I am omitting the middle for brevity, but keep yours exactly the same.
    # It will work perfectly with the new profile structure.
    pass 

# ==========================================
# 4. MAIN APPLICATION UI
# ==========================================

def main():
    st.set_page_config(page_title="Enlead Solar Tool", layout="wide")
    
    # Initialize Profile in Session State
    if "profile" not in st.session_state:
        st.session_state.profile = load_profile()

    profile = st.session_state.profile

    # --- SIDEBAR: SETTINGS ---
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Check if running on Cloud to show a helpful tip
        if "company_profile" in st.secrets:
            st.info("💡 App is using details from Cloud Secrets.")
        
        with st.expander("📝 Edit Company Profile"):
            with st.form("profile_form"):
                st.subheader("Contact Info")
                new_name = st.text_input("Company Name", profile["company_name"])
                new_mobile = st.text_input("Mobile", profile["mobile"])
                new_email = st.text_input("Email", profile["email"])
                new_addr = st.text_area("Address", profile["address"])
                new_head = st.text_input("Prop. Heading", profile["proposal_heading"])
                new_sub = st.text_input("Sub-Heading", profile["sub_heading"])
                
                st.markdown("---")
                st.subheader("Bank Details")
                b_name = st.text_input("Bank Name", profile.get("bank_name", ""))
                acc_name = st.text_input("Account Name", profile.get("acc_name", ""))
                acc_num = st.text_input("Account Number", profile.get("acc_number", ""))
                ifsc = st.text_input("IFSC / SWIFT", profile.get("ifsc_code", ""))

                st.markdown("---")
                st.subheader("Terms")
                new_terms = st.text_area("Edit Terms", value=profile.get("terms_conditions", ""), height=150)

                if st.form_submit_button("💾 Save Profile (Local Only)"):
                    updated_data = {
                        "company_name": new_name, "mobile": new_mobile,
                        "email": new_email, "address": new_addr,
                        "proposal_heading": new_head, "sub_heading": new_sub,
                        "terms_conditions": new_terms,
                        "bank_name": b_name, "acc_name": acc_name,
                        "acc_number": acc_num, "ifsc_code": ifsc
                    }
                    save_profile_data(updated_data)
                    st.success("Saved! Note: For permanent Cloud storage, update Secrets.")
                    st.rerun()

        # Branding uploads remain the same
        with st.expander("🖼️ Branding Images"):
            up_logo = st.file_uploader("Logo", type=["png","jpg"])
            up_bg = st.file_uploader("Background", type=["png","jpg"])
            if st.button("Upload Images"):
                if up_logo: save_image(up_logo, LOGO_FILE)
                if up_bg: save_image(up_bg, BG_FILE)
                st.rerun()

    # ... [Rest of your UI code: Calculator and Tab 2] ...
    # (Just use 'profile' variable as you already are)

if __name__ == "__main__":
    main()
