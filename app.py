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

# Ensure FPDF is available
try:
    from fpdf import FPDF
except ImportError:
    st.error("Library 'fpdf' not found. Please run: pip install fpdf")
    st.stop()

# ==========================================
# 2. DATA MANAGEMENT (PERSISTENCE)
# ==========================================

def load_profile():
    """Loads saved company details or returns defaults."""
    default_data = {
        "company_name": "Enlead Energy Solutions",
        "mobile": "+91 98765 43210",
        "email": "contact@enlead.com",
        "address": "123 Solar Street, Kochi, Kerala",
        "proposal_heading": "Solar Energy Proposal",
        "sub_heading": "Powering a Sustainable Future",
        "terms_conditions": "1. Warranty: As per manufacturer standards (25 Years Performance on Panels).\n2. Installation: Standard structure installation included.\n3. Validity: This quote is valid for 15 days.",
        # Bank Defaults
        "bank_name": "HDFC Bank",
        "acc_name": "Enlead Energy Solutions",
        "acc_number": "50200012345678",
        "ifsc_code": "HDFC0001234"
    }
    
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                saved_data = json.load(f)
                # Merge defaults to ensure new fields (like bank details) exist
                for key, value in default_data.items():
                    if key not in saved_data:
                        saved_data[key] = value
                return saved_data
        except:
            return default_data
    return default_data

def save_profile_data(data):
    with open(PROFILE_FILE, "w") as f:
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

def reset_defaults():
    if os.path.exists(PROFILE_FILE): os.remove(PROFILE_FILE)
    if os.path.exists(LOGO_FILE): os.remove(LOGO_FILE)
    if os.path.exists(BG_FILE): os.remove(BG_FILE)

# ==========================================
# 3. ADVANCED PDF GENERATOR CLASS
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

    # --- PAGE 1: COVER ---
    pdf.add_page()
    
    if os.path.exists(BG_FILE):
        pdf.image(BG_FILE, x=0, y=0, w=210, h=297)

    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=10, y=10, w=35)
    
    pdf.set_xy(100, 15) 
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 8, profile['company_name'], 0, 1, 'R')
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, profile['address'], 0, 1, 'R')
    pdf.cell(0, 5, f"{profile['mobile']} | {profile['email']}", 0, 1, 'R')

    pdf.ln(40)
    pdf.set_font("Arial", "B", 26)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, profile['proposal_heading'].upper(), 0, 1, 'C')
    pdf.set_font("Arial", "", 16)
    pdf.cell(0, 10, profile['sub_heading'], 0, 1, 'C')
    
    pdf.ln(20)
    
    # Customer Info Box
    pdf.set_fill_color(245, 245, 245) 
    pdf.rect(15, 110, 180, 60, 'F')
    
    pdf.set_y(115)
    pdf.set_left_margin(20) 
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "PREPARED FOR:", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Name: {customer_info['name']}", 0, 1)
    pdf.cell(0, 8, f"Location: {customer_info['location']}", 0, 1)
    pdf.cell(0, 8, f"System Type: {customer_info['system_type']}", 0, 1)
    pdf.cell(0, 8, f"Date: {customer_info['date']}", 0, 1)
    
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 8, f"Valid Until: {customer_info['valid_until']}", 0, 1)
    pdf.set_text_color(0, 0, 0) 

    pdf.set_left_margin(10) # Reset margin
    
    # --- PAGE 2: COMMERCIALS ---
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Bill of Materials & Commercials ({customer_info['system_size']})", 0, 1, 'L')
    pdf.ln(5)

    # BOM Table
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(230, 240, 255) 
    pdf.cell(15, 10, "#", 1, 0, 'C', 1)
    pdf.cell(90, 10, "Item Description", 1, 0, 'C', 1)
    pdf.cell(20, 10, "Qty", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Price", 1, 0, 'C', 1)
    pdf.cell(35, 10, "Total", 1, 1, 'C', 1)

    # Rows
    pdf.set_font("Arial", "", 10)
    for idx, item in enumerate(items):
        try:
            qty = float(item['Qty'])
            rate = float(item['Rate'])
            line_total = qty * rate
            
            pdf.cell(15, 10, str(idx+1), 1)
            pdf.cell(90, 10, str(item['Item']), 1)
            pdf.cell(20, 10, str(item['Qty']), 1, 0, 'C')
            pdf.cell(30, 10, f"{rate:,.0f}", 1, 0, 'R')
            pdf.cell(35, 10, f"{line_total:,.0f}", 1, 1, 'R')
        except:
            continue 

    # Grand Total
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(155, 10, "GRAND TOTAL (INR)", 1, 0, 'R')
    pdf.cell(35, 10, f"{total_amount:,.0f}", 1, 1, 'R')
    
    pdf.ln(10)

    # --- PAYMENT TERMS SECTION ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Payment Schedule", 0, 1, 'L')

    # Payment Header
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 8, "Stage", 1, 0, 'L', 1)
    pdf.cell(30, 8, "%", 1, 0, 'C', 1)
    pdf.cell(60, 8, "Amount (INR)", 1, 1, 'R', 1)

    # Payment Rows
    pdf.set_font("Arial", "", 10)
    
    # 1. Advance
    pdf.cell(100, 8, "Advance Payment (Booking)", 1)
    pdf.cell(30, 8, f"{payment_schedule['p_adv']}%", 1, 0, 'C')
    pdf.cell(60, 8, f"{payment_schedule['amt_adv']:,.2f}", 1, 1, 'R')
    
    # 2. Installation
    pdf.cell(100, 8, "On Completion of Structure Installation", 1)
    pdf.cell(30, 8, f"{payment_schedule['p_inst']}%", 1, 0, 'C')
    pdf.cell(60, 8, f"{payment_schedule['amt_inst']:,.2f}", 1, 1, 'R')
    
    # 3. Commissioning
    pdf.cell(100, 8, "On Final Commissioning / Net Metering", 1)
    pdf.cell(30, 8, f"{payment_schedule['p_comm']}%", 1, 0, 'C')
    pdf.cell(60, 8, f"{payment_schedule['amt_comm']:,.2f}", 1, 1, 'R')

    pdf.ln(8)

    # --- BANK DETAILS SECTION (New) ---
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "Bank Account Details for Payment:", 0, 1)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(40, 6, "Bank Name:", 0, 0)
    pdf.cell(0, 6, profile.get('bank_name', ''), 0, 1)
    
    pdf.cell(40, 6, "Account Name:", 0, 0)
    pdf.cell(0, 6, profile.get('acc_name', ''), 0, 1)
    
    pdf.cell(40, 6, "Account Number:", 0, 0)
    pdf.cell(0, 6, profile.get('acc_number', ''), 0, 1)
    
    pdf.cell(40, 6, "IFSC Code:", 0, 0)
    pdf.cell(0, 6, profile.get('ifsc_code', ''), 0, 1)
    
    pdf.ln(8)

    # --- GENERAL TERMS ---
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "General Terms & Conditions:", 0, 1)
    
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, profile.get('terms_conditions', ''))

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. MAIN APPLICATION UI
# ==========================================

def main():
    st.set_page_config(page_title="Enlead Solar Tool", layout="wide")
    
    profile = load_profile()

    # --- SIDEBAR: SETTINGS ---
    with st.sidebar:
        st.title("⚙️ Settings")
        
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

                st.markdown("---")
                st.caption("Upload Branding")
                up_logo = st.file_uploader("Logo (Top Left)", type=["png","jpg"])
                up_bg = st.file_uploader("Cover Bg (A4)", type=["png","jpg"])
                
                if st.form_submit_button("💾 Save Profile"):
                    updated_data = {
                        "company_name": new_name, "mobile": new_mobile,
                        "email": new_email, "address": new_addr,
                        "proposal_heading": new_head, "sub_heading": new_sub,
                        "terms_conditions": new_terms,
                        "bank_name": b_name, "acc_name": acc_name,
                        "acc_number": acc_num, "ifsc_code": ifsc
                    }
                    save_profile_data(updated_data)
                    if up_logo: save_image(up_logo, LOGO_FILE)
                    if up_bg: save_image(up_bg, BG_FILE)
                    st.success("Settings Saved!")
                    st.rerun()

        with st.expander("🗑️ Reset All"):
            if st.button("🔴 Reset to Defaults"):
                reset_defaults()
                st.rerun()

    # --- MAIN CONTENT ---
    c1, c2 = st.columns([1, 5])
    with c1:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=100)
    with c2:
        st.title(profile["company_name"])
        st.write(f"📍 {profile['address']} | 📞 {profile['mobile']}")

    st.markdown("---")

    tab1, tab2 = st.tabs(["🧮 Quick Calculator", "📄 Detailed Proposal (PDF)"])

    # --- TAB 1: CALCULATOR ---
    with tab1:
        st.subheader("☀️ Solar System Estimator")
        colA, colB = st.columns(2)
        with colA:
            monthly_bill = st.number_input("Monthly Bill (Rs)", value=3000, step=500)
            unit_rate = st.number_input("Rate per Unit (Rs)", value=7.5)
        with colB:
            cost_kw = st.number_input("Avg Cost/kW (Rs)", value=65000)
        
        units = monthly_bill / unit_rate
        req_kw = units / 120
        rec_size = max(1, round(req_kw * 2) / 2)
        est_cost = rec_size * cost_kw
        
        subsidy = 0
        if rec_size == 1: subsidy = 30000
        elif rec_size == 2: subsidy = 60000
        elif rec_size >= 3: subsidy = 78000
        
        st.info(f"Based on a bill of ₹{monthly_bill}, you consume approx {int(units)} units/month.")
        m1, m2, m3 = st.columns(3)
        m1.metric("Recommended Size", f"{rec_size} kW")
        m2.metric("Est. Cost", f"₹ {est_cost:,.0f}")
        m3.metric("Net Cost", f"₹ {(est_cost - subsidy):,.0f}", delta=f"Subsidy: ₹{subsidy}")
        st.caption("👉 Go to the **'Detailed Proposal'** tab to generate the PDF.")

    # --- TAB 2: PROPOSAL GENERATOR ---
    with tab2:
        st.subheader("📝 Create Proposal")
        
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            cust_name = st.text_input("Customer Name", placeholder="Enter Name")
            cust_loc = st.text_input("Location", "Kerala, India")
            prop_date = st.date_input("Date", datetime.date.today())
        with c_col2:
            sys_type = st.selectbox("System Type", ["On-Grid (Net Metered)", "Hybrid (Battery)", "Off-Grid"])
            sys_size_input = st.text_input("System Capacity", f"{rec_size} kW")
            valid_until = st.date_input("Valid Until", datetime.date.today() + datetime.timedelta(days=15))

        st.markdown("### Bill of Materials (Editable)")
        default_items = [
            {"Item": "Solar PV Modules (Mono PERC)", "Qty": 10, "Rate": 18000},
            {"Item": "Solar Inverter", "Qty": 1, "Rate": 45000},
            {"Item": "Structure & Installation Kit", "Qty": 1, "Rate": 25000},
            {"Item": "Net Metering & Liaisoning", "Qty": 1, "Rate": 15000},
        ]
        
        edited_items = st.data_editor(default_items, num_rows="dynamic", use_container_width=True)
        
        # Calculate Total
        total_project_value = 0
        for item in edited_items:
            try:
                total_project_value += float(item['Qty']) * float(item['Rate'])
            except:
                pass

        st.metric("Total Project Value", f"₹ {total_project_value:,.2f}")

        st.markdown("---")
        st.markdown("### Payment Terms (Define Percentages)")
        
        # --- PAYMENT INPUTS ---
        pay_col1, pay_col2, pay_col3 = st.columns(3)
        
        with pay_col1:
            p_adv = st.number_input("Advance (%)", min_value=0, max_value=100, value=70)
        with pay_col2:
            p_inst = st.number_input("On Installation (%)", min_value=0, max_value=100, value=25)
        with pay_col3:
            p_comm = st.number_input("On Commissioning (%)", min_value=0, max_value=100, value=5)
            
        total_percent = p_adv + p_inst + p_comm
        
        # Live calculation
        amt_adv = total_project_value * (p_adv / 100)
        amt_inst = total_project_value * (p_inst / 100)
        amt_comm = total_project_value * (p_comm / 100)
        
        if total_percent != 100:
            st.error(f"⚠️ Total percentage is {total_percent}%. It must be exactly 100%.")
        else:
            st.success("✅ Payment terms total 100%.")
            with st.expander("View Payment Schedule & Bank Info"):
                st.write(f"1. Advance ({p_adv}%): ₹ {amt_adv:,.2f}")
                st.write(f"2. Installation ({p_inst}%): ₹ {amt_inst:,.2f}")
                st.write(f"3. Commissioning ({p_comm}%): ₹ {amt_comm:,.2f}")
                st.markdown("---")
                st.write(f"**Bank:** {profile.get('bank_name')} | **IFSC:** {profile.get('ifsc_code')}")

        st.markdown("---")
        
        if cust_name and total_percent == 100:
            if st.button("📄 Generate PDF Proposal", type="primary"):
                customer_info = {
                    "name": cust_name, "location": cust_loc, 
                    "date": prop_date, "valid_until": valid_until,
                    "system_type": sys_type, "system_size": sys_size_input
                }
                
                # Bundle payment data
                payment_schedule = {
                    "p_adv": p_adv, "amt_adv": amt_adv,
                    "p_inst": p_inst, "amt_inst": amt_inst,
                    "p_comm": p_comm, "amt_comm": amt_comm
                }
                
                pdf_data = generate_premium_pdf(profile, customer_info, edited_items, total_project_value, payment_schedule)
                
                st.success("Proposal Ready!")
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_data,
                    file_name=f"Proposal_{cust_name}.pdf",
                    mime="application/pdf"
                )
        elif not cust_name:
            st.warning("Please enter a **Customer Name**.")
        elif total_percent != 100:
            st.warning("Please fix the **Payment Percentages**.")

if __name__ == "__main__":
    main()
