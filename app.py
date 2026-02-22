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
# 2. DATA MANAGEMENT
# ==========================================

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
        image = Image.open(uploaded_file)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(destination_filename)
        return True
    return False

# ==========================================
# 3. PDF GENERATION (PROPOSAL)
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

def generate_premium_pdf(profile, customer_info, items, total_amount):
    pdf = SolarProposalPDF(profile)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    if os.path.exists(BG_FILE): pdf.image(BG_FILE, x=0, y=0, w=210, h=297)
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, x=10, y=10, w=35)
    
    pdf.set_xy(100, 15) 
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, profile['company_name'], 0, 1, 'R')
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, profile['address'], 0, 1, 'R')
    
    pdf.ln(30)
    pdf.set_font("Arial", "B", 22)
    pdf.cell(0, 10, profile['proposal_heading'].upper(), 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "CUSTOMER DETAILS:", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Name: {customer_info['name']}", 0, 1)
    pdf.cell(0, 7, f"Contact: {customer_info['phone']}", 0, 1)
    pdf.multi_cell(0, 7, f"Address: {customer_info['address']}")
    pdf.cell(0, 7, f"System Size: {customer_info['system_size']}", 0, 1)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 10, "Item Description", 1, 0, 'L', 1)
    pdf.cell(30, 10, "Qty", 1, 0, 'C', 1)
    pdf.cell(50, 10, "Total (INR)", 1, 1, 'R', 1)
    
    pdf.set_font("Arial", "", 10)
    for item in items:
        total = float(item['Qty']) * float(item['Rate'])
        pdf.cell(100, 10, item['Item'], 1)
        pdf.cell(30, 10, str(item['Qty']), 1, 0, 'C')
        pdf.cell(50, 10, f"{total:,.0f}", 1, 1, 'R')

    pdf.set_font("Arial", "B", 11)
    pdf.cell(130, 10, "Grand Total", 1, 0, 'R')
    pdf.cell(50, 10, f"{total_amount:,.0f}", 1, 1, 'R')

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. MAIN UI
# ==========================================

def main():
    st.set_page_config(page_title="Enlead Solar Hub", layout="wide")
    
    # Load Profile
    if "profile" not in st.session_state:
        st.session_state.profile = load_json(PROFILE_FILE, {
            "company_name": "Enlead Energy Solutions", "mobile": "+91 98765 43210", 
            "address": "Kerala, India", "proposal_heading": "Solar Proposal",
            "bank_name": "", "acc_number": "", "ifsc_code": "", "terms_conditions": ""
        })
    
    # Load Projects
    if "projects" not in st.session_state:
        st.session_state.projects = load_json(PROJECTS_FILE, [])

    profile = st.session_state.profile

    with st.sidebar:
        st.title("⚙️ Control Panel")
        with st.expander("📝 Edit Company Profile"):
            with st.form("p_form"):
                n_name = st.text_input("Company Name", profile["company_name"])
                n_mob = st.text_input("Mobile", profile["mobile"])
                n_addr = st.text_area("Address", profile["address"])
                n_bank = st.text_input("Bank Name", profile.get("bank_name", ""))
                n_acc = st.text_input("Account Number", profile.get("acc_number", ""))
                n_ifsc = st.text_input("IFSC", profile.get("ifsc_code", ""))
                n_terms = st.text_area("Terms", profile.get("terms_conditions", ""))
                if st.form_submit_button("Save Profile"):
                    new_data = {**profile, "company_name": n_name, "mobile": n_mob, "address": n_addr, "bank_name": n_bank, "acc_number": n_acc, "ifsc_code": n_ifsc, "terms_conditions": n_terms}
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

    # CALCULATOR
    with tab1:
        st.subheader("Quick Estimator")
        bill = st.number_input("Monthly Bill (₹)", value=3000)
        size = max(1.0, (bill / 7.5) / 120)
        st.metric("Recommended Size", f"{size:.2f} kW")

    # PROPOSAL
    with tab2:
        st.subheader("Create Proposal")
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("Customer Name")
            c_phone = st.text_input("Customer Phone")
        with col2:
            c_addr = st.text_area("Customer Address")
            c_size = st.text_input("System Size", f"{size:.2f} kW")

        items = st.data_editor([
            {"Item": "Solar Panels", "Qty": 10, "Rate": 18000},
            {"Item": "Inverter", "Qty": 1, "Rate": 45000}
        ], num_rows="dynamic")
        
        total_val = sum(float(i['Qty']) * float(i['Rate']) for i in items)
        
        if st.button("Generate & Download PDF"):
            if c_name:
                c_info = {"name": c_name, "phone": c_phone, "address": c_addr, "system_size": c_size}
                pdf_bytes = generate_premium_pdf(profile, c_info, items, total_val)
                st.download_button("Download PDF", data=pdf_bytes, file_name=f"Proposal_{c_name}.pdf")
            else:
                st.error("Enter customer name")

    # PROJECT TRACKER
    with tab3:
        st.subheader("Manage Active Projects")
        
        # Form to add new project
        with st.expander("➕ Add New Project"):
            with st.form("new_project"):
                p_cust = st.text_input("Customer Name")
                p_size = st.text_input("Capacity (kW)")
                p_status = st.selectbox("Current Status", ["Survey Pending", "Material Ordered", "Installation Ongoing", "Net Metering", "Completed"])
                if st.form_submit_button("Add to List"):
                    st.session_state.projects.append({"Date": str(datetime.date.today()), "Customer": p_cust, "Size": p_size, "Status": p_status})
                    save_json(PROJECTS_FILE, st.session_state.projects)
                    st.rerun()

        # Display Table
        if st.session_state.projects:
            df = pd.DataFrame(st.session_state.projects)
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            if st.button("Update Tracker"):
                st.session_state.projects = edited_df.to_dict('records')
                save_json(PROJECTS_FILE, st.session_state.projects)
                st.success("Tracker updated!")
        else:
            st.info("No projects added yet.")

if __name__ == "__main__":
    main()
