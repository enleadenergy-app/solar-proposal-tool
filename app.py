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
        "sub_heading": "Powering a Sustainable Future"
    }
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_profile_data(data):
    """Saves company details to JSON."""
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_image(uploaded_file, destination_filename):
    """Saves uploaded images to disk."""
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
    """Clears all saved data."""
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

def generate_premium_pdf(profile, customer_info, items, total_amount):
    pdf = SolarProposalPDF(profile)
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- PAGE 1: COVER ---
    pdf.add_page()
    
    # 1. Background Image (Full Page)
    if os.path.exists(BG_FILE):
        # A4 size in mm: 210 x 297
        pdf.image(BG_FILE, x=0, y=0, w=210, h=297)

    # 2. Logo (Top Left)
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=10, y=10, w=35)
    
    # 3. Company Header (Top Right)
    pdf.set_xy(100, 15) # Move to right side
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 8, profile['company_name'], 0, 1, 'R')
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, profile['address'], 0, 1, 'R')
    pdf.cell(0, 5, f"{profile['mobile']} | {profile['email']}", 0, 1, 'R')

    # 4. Big Title
    pdf.ln(40)
    pdf.set_font("Arial", "B", 26)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, profile['proposal_heading'].upper(), 0, 1, 'C')
    pdf.set_font("Arial", "", 16)
    pdf.cell(0, 10, profile['sub_heading'], 0, 1, 'C')
    
    pdf.ln(20)
    
    # 5. Customer Info Box
    # Draw a light gray rectangle
    pdf.set_fill_color(245, 245, 245) 
    pdf.rect(15, 110, 180, 60, 'F')
    
    pdf.set_y(115)
    pdf.set_left_margin(20) # Indent text inside box
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "PREPARED FOR:", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Name: {customer_info['name']}", 0, 1)
    pdf.cell(0, 8, f"Location: {customer_info['location']}", 0, 1)
    pdf.cell(0, 8, f"System Type: {customer_info['system_type']}", 0, 1)
    pdf.cell(0, 8, f"Date: {customer_info['date']}", 0, 1)
    
    # Valid Until (Red)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 8, f"Valid Until: {customer_info['valid_until']}", 0, 1)
    pdf.set_text_color(0, 0, 0) # Reset color

    pdf.set_left_margin(10) # Reset margin
    
    # --- PAGE 2: COMMERCIALS ---
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Bill of Materials & Commercials ({customer_info['system_size']})", 0, 1, 'L')
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(230, 240, 255) # Light Blue
    pdf.cell(15, 10, "#", 1, 0, 'C', 1)
    pdf.cell(90, 10, "Item Description", 1, 0, 'C', 1)
    pdf.cell(20, 10, "Qty", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Price", 1, 0, 'C', 1)
    pdf.cell(35, 10, "Total", 1, 1, 'C', 1)

    # Table Rows
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
            continue # Skip invalid rows

    # Grand Total
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(155, 10, "GRAND TOTAL (INR)", 1, 0, 'R')
    pdf.cell(35, 10, f"{total_amount:,.0f}", 1, 1, 'R')
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "Terms & Conditions:", 0, 1)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 6, "1. Payment: 70% Advance, 30% upon completion.\n2. Delivery: Within 2 weeks of advance payment.\n3. Warranty: As per manufacturer standards (25 Years Performance on Panels).")

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. MAIN APPLICATION UI
# ==========================================

def main():
    st.set_page_config(page_title="Enlead Solar Tool", layout="wide")
    
    # Load Persistent Profile
    profile = load_profile()

    # --- SIDEBAR: SETTINGS ---
    with st.sidebar:
        st.title("⚙️ Settings")
        
        with st.expander("📝 Edit Company Profile"):
            with st.form("profile_form"):
                new_name = st.text_input("Company Name", profile["company_name"])
                new_mobile = st.text_input("Mobile", profile["mobile"])
                new_email = st.text_input("Email", profile["email"])
                new_addr = st.text_area("Address", profile["address"])
                new_head = st.text_input("Prop. Heading", profile["proposal_heading"])
                new_sub = st.text_input("Sub-Heading", profile["sub_heading"])
                
                st.markdown("---")
                st.caption("Upload Branding (Saved Permanently)")
                up_logo = st.file_uploader("Logo (Top Left)", type=["png","jpg"])
                up_bg = st.file_uploader("Cover Bg (A4)", type=["png","jpg"])
                
                if st.form_submit_button("💾 Save Profile"):
                    updated_data = {
                        "company_name": new_name, "mobile": new_mobile,
                        "email": new_email, "address": new_addr,
                        "proposal_heading": new_head, "sub_heading": new_sub
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

    # --- MAIN CONTENT AREA ---
    
    # Header
    c1, c2 = st.columns([1, 5])
    with c1:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=100)
    with c2:
        st.title(profile["company_name"])
        st.write(f"📍 {profile['address']} | 📞 {profile['mobile']}")

    st.markdown("---")

    # TABS
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
        
        # Logic
        units = monthly_bill / unit_rate
        req_kw = units / 120
        rec_size = max(1, round(req_kw * 2) / 2) # Round to nearest 0.5
        est_cost = rec_size * cost_kw
        
        # Subsidy Logic
        subsidy = 0
        if rec_size == 1: subsidy = 30000
        elif rec_size == 2: subsidy = 60000
        elif rec_size >= 3: subsidy = 78000
        
        st.info(f"Based on a bill of ₹{monthly_bill}, you consume approx {int(units)} units/month.")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Recommended Size", f"{rec_size} kW")
        m2.metric("Est. Cost", f"₹ {est_cost:,.0f}")
        m3.metric("Net Cost (After Subsidy)", f"₹ {(est_cost - subsidy):,.0f}", delta=f"Subsidy: ₹{subsidy}")
        
        st.caption("👉 Go to the **'Detailed Proposal'** tab to generate the official PDF quotation.")

    # --- TAB 2: PROPOSAL GENERATOR ---
    with tab2:
        st.subheader("📝 Create Proposal")
        
        # 1. Customer Info
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            cust_name = st.text_input("Customer Name", placeholder="Enter Name")
            cust_loc = st.text_input("Location", "Kerala, India")
            prop_date = st.date_input("Date", datetime.date.today())
        with c_col2:
            sys_type = st.selectbox("System Type", ["On-Grid (Net Metered)", "Hybrid (Battery)", "Off-Grid"])
            # Default the system size to the calculation from Tab 1
            sys_size_input = st.text_input("System Capacity", f"{rec_size} kW")
            valid_until = st.date_input("Valid Until", datetime.date.today() + datetime.timedelta(days=15))

        st.markdown("### Bill of Materials (Editable)")
        
        # 2. Editable BOM Table
        # Default items based on the calculated size
        default_items = [
            {"Item": "Solar PV Modules (Mono PERC)", "Qty": 10, "Rate": 18000},
            {"Item": "Solar Inverter", "Qty": 1, "Rate": 45000},
            {"Item": "Structure & Installation Kit", "Qty": 1, "Rate": 25000},
            {"Item": "Net Metering & Liaisoning", "Qty": 1, "Rate": 15000},
        ]
        
        edited_items = st.data_editor(default_items, num_rows="dynamic", use_container_width=True)
        
        # Calculate Live Total from Table
        total_project_value = 0
        for item in edited_items:
            try:
                total_project_value += float(item['Qty']) * float(item['Rate'])
            except:
                pass

        st.metric("Total Project Value", f"₹ {total_project_value:,.2f}")

        st.markdown("---")
        
        # 3. Generate Button
        if cust_name:
            if st.button("📄 Generate PDF Proposal", type="primary"):
                # Pack data
                customer_info = {
                    "name": cust_name, "location": cust_loc, 
                    "date": prop_date, "valid_until": valid_until,
                    "system_type": sys_type, "system_size": sys_size_input
                }
                
                pdf_data = generate_premium_pdf(profile, customer_info, edited_items, total_project_value)
                
                st.success("Proposal Ready!")
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_data,
                    file_name=f"Proposal_{cust_name}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Please enter a **Customer Name** to enable PDF generation.")

if __name__ == "__main__":
    main()
