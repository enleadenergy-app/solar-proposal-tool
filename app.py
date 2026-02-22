import streamlit as st
from fpdf import FPDF
import os
import json
import datetime
from PIL import Image
import pandas as pd

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
PROFILE_FILE = "profile_config.json"
PROJECTS_FILE = "projects_tracker.json"
LOGO_FILE = "company_logo.png"
BG_FILE = "company_bg.png"

# ==========================================
# 2. DATA MANAGEMENT (WITH SECRETS SUPPORT)
# ==========================================

def load_profile():
    """Priority: 1. Secrets (Cloud), 2. Local JSON, 3. Defaults"""
    default_data = {
        "company_name": "Enlead Energy Solutions", 
        "mobile": "+91 98765 43210", 
        "email": "contact@enlead.com",
        "address": "Kerala, India", 
        "proposal_heading": "Solar Energy Proposal",
        "bank_name": "HDFC Bank", 
        "acc_name": "Enlead Energy Solutions",
        "acc_number": "50200012345678", 
        "ifsc_code": "HDFC0001234", 
        "terms_conditions": "1. Warranty: 25 Years.\n2. Validity: 15 Days."
    }

    # 1. Check Streamlit Secrets (for Cloud Deployment)
    if "company_profile" in st.secrets:
        return dict(st.secrets["company_profile"])
    
    # 2. Check Local JSON (for local editing)
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except:
            return default_data
            
    return default_data

def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def save_image(uploaded_file, destination_filename):
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            image.save(destination_filename)
            return True
        except Exception as e:
            st.error(f"Error saving image: {e}")
            return False
    return False

# ==========================================
# 3. PDF GENERATION (CRASH-PROOFED)
# ==========================================

class SolarProposalPDF(FPDF):
    def __init__(self, profile):
        super().__init__()
        self.profile = profile

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        comp_name = str(self.profile.get('company_name', 'Enlead Energy'))
        mob = str(self.profile.get('mobile', ''))
        text = f"Page {self.page_no()} | {comp_name} | {mob}"
        self.cell(0, 10, text, 0, 0, 'C')

def generate_premium_pdf(profile, customer_info, items, total_amount):
    pdf = SolarProposalPDF(profile)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    if os.path.exists(BG_FILE): pdf.image(BG_FILE, x=0, y=0, w=210, h=297)
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, x=10, y=10, w=35)
    
    pdf.set_xy(100, 15) 
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, str(profile.get('company_name', '')), 0, 1, 'R')
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, str(profile.get('address', '')), 0, 1, 'R')
    
    pdf.ln(30)
    pdf.set_font("Arial", "B", 22)
    pdf.cell(0, 10, str(profile.get('proposal_heading', 'PROPOSAL')).upper(), 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "CUSTOMER DETAILS:", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Name: {str(customer_info.get('name', 'N/A'))}", 0, 1)
    pdf.cell(0, 7, f"Contact: {str(customer_info.get('phone', 'N/A'))}", 0, 1)
    pdf.multi_cell(0, 7, f"Address: {str(customer_info.get('address', 'N/A'))}")
    pdf.cell(0, 7, f"System Size: {str(customer_info.get('system_size', 'N/A'))}", 0, 1)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 10, "Item Description", 1, 0, 'L', 1)
    pdf.cell(30, 10, "Qty", 1, 0, 'C', 1)
    pdf.cell(50, 10, "Total (INR)", 1, 1, 'R', 1)
    
    pdf.set_font("Arial", "", 10)
    for item in items:
        name = str(item.get('Item', '')) if item.get('Item') else "Component"
        qty_val = item.get('Qty', 0)
        rate_val = item.get('Rate', 0)
        try:
            line_total = float(qty_val) * float(rate_val)
        except:
            line_total = 0
        pdf.cell(100, 10, name, 1)
        pdf.cell(30, 10, str(qty_val), 1, 0, 'C')
        pdf.cell(50, 10, f"{line_total:,.0f}", 1, 1, 'R')

    pdf.set_font("Arial", "B", 11)
    pdf.cell(130, 10, "Grand Total", 1, 0, 'R')
    pdf.cell(50, 10, f"{total_amount:,.0f}", 1, 1, 'R')

    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "Bank Details:", 0, 1)
    pdf.set_font("Arial", "", 9)
    bank_info = f"Bank: {profile.get('bank_name', '')} | A/C: {profile.get('acc_number', '')} | IFSC: {profile.get('ifsc_code', '')}"
    pdf.cell(0, 6, str(bank_info), 0, 1)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "Terms & Conditions:", 0, 1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, str(profile.get('terms_conditions', '')))

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. MAIN UI
# ==========================================

def main():
    st.set_page_config(page_title="Enlead Solar Hub", layout="wide")
    
    # LOAD PROFILE USING THE SECRETS-FIRST FUNCTION
    if "profile" not in st.session_state:
        st.session_state.profile = load_profile()
    
    if "projects" not in st.session_state:
        st.session_state.projects = load_json(PROJECTS_FILE, [])

    profile = st.session_state.profile

    with st.sidebar:
        st.title("⚙️ Control Panel")
        
        # UI Hint about Secrets
        if "company_profile" in st.secrets:
            st.success("✅ Loading from Cloud Secrets")
        
        with st.expander("📝 Edit Company Profile"):
            with st.form("p_form"):
                n_name = st.text_input("Company Name", profile["company_name"])
                n_mob = st.text_input("Mobile", profile["mobile"])
                n_addr = st.text_area("Address", profile["address"])
                n_bank = st.text_input("Bank Name", profile.get("bank_name", ""))
                n_acc_n = st.text_input("Account Name", profile.get("acc_name", ""))
                n_acc = st.text_input("Account Number", profile.get("acc_number", ""))
                n_ifsc = st.text_input("IFSC", profile.get("ifsc_code", ""))
                n_terms = st.text_area("Terms", profile.get("terms_conditions", ""))
                if st.form_submit_button("Save Profile (Local Only)"):
                    new_data = {**profile, "company_name": n_name, "mobile": n_mob, "address": n_addr, "bank_name": n_bank, "acc_name": n_acc_n, "acc_number": n_acc, "ifsc_code": n_ifsc, "terms_conditions": n_terms}
                    save_json(PROFILE_FILE, new_data)
                    st.session_state.profile = new_data
                    st.rerun()

        with st.expander("🖼️ Branding"):
            u_logo = st.file_uploader("Upload Logo", type=["png", "jpg"])
            u_bg = st.file_uploader("Upload Background", type=["png", "jpg"])
            if st.button("Update Images"):
                if u_logo: save_image(u_logo, LOGO_FILE)
                if u_bg: save_image(u_bg, BG_FILE)
                st.rerun()

    st.title(f"☀️ {profile['company_name']}")
    tab1, tab2, tab3 = st.tabs(["🧮 Calculator", "📄 Proposal Generator", "📋 Project Tracker"])

    # TAB 1: CALCULATOR
    with tab1:
        st.subheader("Solar Estimator")
        bill = st.number_input("Monthly Bill (₹)", value=3000)
        size_calc = max(1.0, (bill / 7.5) / 120)
        st.metric("Recommended Size", f"{size_calc:.2f} kW")

    # TAB 2: PROPOSAL
    with tab2:
        st.subheader("Customer & Project Details")
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("Customer Name")
            c_phone = st.text_input("Customer Phone")
        with col2:
            c_addr = st.text_area("Customer Address")
            c_size = st.text_input("System Size", f"{size_calc:.2f} kW")

        items_list = st.data_editor([
            {"Item": "Solar Panels", "Qty": 10, "Rate": 18000},
            {"Item": "Inverter", "Qty": 1, "Rate": 45000}
        ], num_rows="dynamic", key="bom_editor")
        
        total_val = sum(float(i.get('Qty', 0)) * float(i.get('Rate', 0)) for i in items_list if i.get('Qty'))
        st.write(f"**Total Project Value:** ₹ {total_val:,.2f}")
        
        if st.button("📄 Generate & Download PDF", type="primary"):
            if c_name:
                c_info = {"name": c_name, "phone": c_phone, "address": c_addr, "system_size": c_size}
                pdf_bytes = generate_premium_pdf(profile, c_info, items_list, total_val)
                st.download_button("⬇️ Download PDF", data=pdf_bytes, file_name=f"Proposal_{c_name}.pdf")
            else:
                st.error("Customer Name is required!")

    # TAB 3: PROJECT TRACKER
    with tab3:
        st.subheader("Manage Active Projects")
        with st.expander("➕ Add New Project"):
            with st.form("new_p"):
                p_c = st.text_input("Customer")
                p_s = st.selectbox("Status", ["Survey", "Material Shipped", "Installation", "Completed"])
                if st.form_submit_button("Add Project"):
                    st.session_state.projects.append({"Date": str(datetime.date.today()), "Customer": p_c, "Status": p_s})
                    save_json(PROJECTS_FILE, st.session_state.projects)
                    st.rerun()

        if st.session_state.projects:
            df = pd.DataFrame(st.session_state.projects)
            updated_df = st.data_editor(df, num_rows="dynamic")
            if st.button("Save Changes"):
                save_json(PROJECTS_FILE, updated_df.to_dict('records'))
                st.success("Project Tracker Updated!")

if __name__ == "__main__":
    main()
