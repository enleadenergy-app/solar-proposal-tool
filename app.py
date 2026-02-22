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
# 2. DATA MANAGEMENT
# ==========================================

def load_profile():
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
    
    # Priority 1: Streamlit Cloud Secrets
    if "company_profile" in st.secrets:
        return dict(st.secrets["company_profile"])
    
    # Priority 2: Local File
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_profile_data(data):
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f, indent=4)
    st.session_state.profile = data

def save_image(uploaded_file, destination_filename):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(destination_filename)
        return True
    return False

# ==========================================
# 3. PDF GENERATION CLASS & FUNCTION
# ==========================================

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

def generate_premium_pdf(profile, customer_info, items, total_amount, payment_schedule):
    pdf = SolarProposalPDF(profile)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Branding
    if os.path.exists(BG_FILE): pdf.image(BG_FILE, x=0, y=0, w=210, h=297)
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, x=10, y=10, w=35)
    
    pdf.set_xy(100, 15) 
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, profile['company_name'], 0, 1, 'R')
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, profile['address'], 0, 1, 'R')
    
    # Customer Info
    pdf.ln(30)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 10, profile['proposal_heading'].upper(), 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Customer: {customer_info['name']}", 0, 1)
    pdf.cell(0, 8, f"System: {customer_info['system_size']}", 0, 1)

    # Commercials Table
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 10, "Item", 1); pdf.cell(30, 10, "Qty", 1); pdf.cell(50, 10, "Total", 1, 1)
    pdf.set_font("Arial", "", 10)
    for item in items:
        pdf.cell(100, 10, item['Item'], 1)
        pdf.cell(30, 10, str(item['Qty']), 1)
        total = float(item['Qty']) * float(item['Rate'])
        pdf.cell(50, 10, f"{total:,.0f}", 1, 1)

    # Bank Details
    pdf.ln(10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, "Bank Details:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Bank: {profile['bank_name']}", 0, 1)
    pdf.cell(0, 6, f"A/C: {profile['acc_number']}", 0, 1)
    pdf.cell(0, 6, f"IFSC: {profile['ifsc_code']}", 0, 1)

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. MAIN APPLICATION UI
# ==========================================

def main():
    st.set_page_config(page_title="Enlead Solar Tool", layout="wide")
    
    if "profile" not in st.session_state:
        st.session_state.profile = load_profile()

    profile = st.session_state.profile

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("⚙️ Settings")
        with st.expander("📝 Edit Profile"):
            with st.form("p_form"):
                n_name = st.text_input("Company Name", profile["company_name"])
                n_mob = st.text_input("Mobile", profile["mobile"])
                n_addr = st.text_area("Address", profile["address"])
                n_bank = st.text_input("Bank Name", profile["bank_name"])
                n_acc = st.text_input("Account Number", profile["acc_number"])
                n_ifsc = st.text_input("IFSC", profile["ifsc_code"])
                n_terms = st.text_area("Terms", profile["terms_conditions"])
                
                if st.form_submit_button("Save Locally"):
                    new_data = profile.copy()
                    new_data.update({"company_name": n_name, "mobile": n_mob, "address": n_addr, "bank_name": n_bank, "acc_number": n_acc, "ifsc_code": n_ifsc, "terms_conditions": n_terms})
                    save_profile_data(new_data)
                    st.rerun()

    # --- MAIN UI ---
    st.title(f"☀️ {profile['company_name']}")
    
    tab1, tab2 = st.tabs(["🧮 Calculator", "📄 Generate Proposal"])

    with tab1:
        st.subheader("Solar Estimator")
        bill = st.number_input("Monthly Bill (₹)", value=3000)
        size = max(1.0, (bill / 7.5) / 120)
        st.metric("Recommended Size", f"{size:.2f} kW")

    with tab2:
        st.subheader("Create PDF Proposal")
        c_name = st.text_input("Customer Name")
        
        # Editable Materials
        items = st.data_editor([
            {"Item": "Solar Panels", "Qty": 10, "Rate": 18000},
            {"Item": "Inverter", "Qty": 1, "Rate": 45000}
        ], num_rows="dynamic")

        total_val = sum(float(i['Qty']) * float(i['Rate']) for i in items)
        
        if st.button("Generate & Download PDF"):
            if not c_name:
                st.error("Please enter a customer name!")
            else:
                cust_info = {"name": c_name, "system_size": f"{size:.2f}kW"}
                pdf_bytes = generate_premium_pdf(profile, cust_info, items, total_val, {})
                st.download_button("Download Proposal", data=pdf_bytes, file_name="Proposal.pdf")

if __name__ == "__main__":
    main()
