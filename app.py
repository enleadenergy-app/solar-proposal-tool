import streamlit as st
from fpdf import FPDF
import base64
import os
import json
from PIL import Image

# ==========================================
# 1. CONFIGURATION & CONSTANTS
# ==========================================
PROFILE_FILE = "profile_config.json"
LOGO_FILE = "company_logo.png"
BG_FILE = "company_bg.png"

# ==========================================
# 2. HELPER FUNCTIONS (DATA MANAGEMENT)
# ==========================================

def load_profile():
    """Loads profile data from JSON, or returns Enlead defaults if file is missing."""
    default_data = {
        "company_name": "Enlead Energy Solutions",
        "mobile": "+91 98765 43210",
        "email": "contact@enlead.com",
        "address": "123 Solar Street, Kochi, Kerala, India",
        "proposal_heading": "Premium Solar Proposal",
        "sub_heading": "Sustainable Energy for Your Future"
    }
    
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_profile_data(data):
    """Saves text data to JSON."""
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_image(uploaded_file, destination_filename):
    """Saves uploaded images locally."""
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            # Convert to RGB to ensure compatibility (removes alpha channel if present)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            image.save(destination_filename)
            return True
        except Exception as e:
            st.error(f"Error saving image: {e}")
            return False
    return False

def reset_to_defaults():
    """Deletes all saved files to restore defaults."""
    if os.path.exists(PROFILE_FILE): os.remove(PROFILE_FILE)
    if os.path.exists(LOGO_FILE): os.remove(LOGO_FILE)
    if os.path.exists(BG_FILE): os.remove(BG_FILE)

# ==========================================
# 3. PDF GENERATION LOGIC
# ==========================================

def create_pdf(profile, customer_name, monthly_bill, system_size, total_cost, subsidy, net_cost):
    pdf = FPDF()
    pdf.add_page()
    
    # --- A. BACKGROUND IMAGE ---
    # Must be added first to sit behind text
    if os.path.exists(BG_FILE):
        # x=0, y=0, w=210, h=297 (A4 dimensions in mm)
        pdf.image(BG_FILE, x=0, y=0, w=210, h=297)
    
    # --- B. HEADER & LOGO ---
    # Add Logo if exists
    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=10, y=8, w=30)
    
    # Company Details (Top Right)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, profile["company_name"], ln=True, align='R')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, profile["address"], ln=True, align='R')
    pdf.cell(0, 5, f"Ph: {profile['mobile']} | Email: {profile['email']}", ln=True, align='R')
    
    pdf.ln(20) # Space after header
    
    # --- C. PROPOSAL BODY ---
    
    # Title
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, profile["proposal_heading"], ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, profile["sub_heading"], ln=True, align='C')
    
    pdf.ln(10)
    
    # Customer Details Box
    pdf.set_fill_color(240, 240, 240) # Light gray background
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Prepared for: {customer_name}", ln=True, align='L', fill=True)
    
    pdf.ln(10)
    
    # Technical Specs
    pdf.set_font("Arial", '', 12)
    pdf.cell(100, 10, f"Average Monthly Bill:", border=1)
    pdf.cell(0, 10, f"Rs. {monthly_bill}", border=1, ln=True)
    
    pdf.cell(100, 10, f"Recommended System Size:", border=1)
    pdf.cell(0, 10, f"{system_size} kW", border=1, ln=True)
    
    pdf.ln(5)
    
    # Financials
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"Total Project Cost:", border=1)
    pdf.cell(0, 10, f"Rs. {total_cost:,.2f}", border=1, ln=True)
    
    pdf.set_text_color(0, 150, 0) # Green color for subsidy
    pdf.cell(100, 10, f"Estimated Subsidy:", border=1)
    pdf.cell(0, 10, f"- Rs. {subsidy:,.2f}", border=1, ln=True)
    
    pdf.set_text_color(0, 0, 0) # Reset to black
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(100, 12, f"Net Investment:", border=1)
    pdf.cell(0, 12, f"Rs. {net_cost:,.2f}", border=1, ln=True)
    
    # --- D. FOOTER ---
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "This proposal is an estimate. Final pricing subject to site visit.", align='C')

    # Return PDF as string/bytes
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. MAIN STREAMLIT APPLICATION
# ==========================================

def main():
    st.set_page_config(page_title="Solar Proposal Generator", layout="wide")

    # --- LOAD DATA ---
    profile = load_profile()

    # --- SIDEBAR: SETTINGS & EDITING ---
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # TAB 1: EDIT PROFILE
        with st.expander("📝 Edit Company Profile", expanded=False):
            with st.form("profile_form"):
                st.subheader("Text Details")
                new_name = st.text_input("Company Name", value=profile["company_name"])
                new_mobile = st.text_input("Mobile Number", value=profile["mobile"])
                new_email = st.text_input("Email ID", value=profile["email"])
                new_address = st.text_area("Address", value=profile["address"])
                new_heading = st.text_input("Proposal Heading", value=profile["proposal_heading"])
                new_sub_heading = st.text_input("Sub-Heading", value=profile["sub_heading"])
                
                st.markdown("---")
                st.subheader("Images")
                uploaded_logo = st.file_uploader("Logo (Top Left)", type=["png", "jpg", "jpeg"])
                uploaded_bg = st.file_uploader("PDF Background (A4)", type=["png", "jpg", "jpeg"])

                submitted = st.form_submit_button("💾 Save Changes")
                if submitted:
                    # Save Text
                    updated_data = {
                        "company_name": new_name,
                        "mobile": new_mobile,
                        "email": new_email,
                        "address": new_address,
                        "proposal_heading": new_heading,
                        "sub_heading": new_sub_heading
                    }
                    save_profile_data(updated_data)
                    
                    # Save Images
                    if uploaded_logo: save_image(uploaded_logo, LOGO_FILE)
                    if uploaded_bg: save_image(uploaded_bg, BG_FILE)
                    
                    st.success("Profile Updated!")
                    st.rerun()

        # TAB 2: RESET
        with st.expander("🗑️ Reset Settings", expanded=False):
            st.warning("Delete all saved data and restore defaults?")
            if st.button("🔴 Reset to Default"):
                reset_to_defaults()
                st.rerun()

    # --- MAIN DISPLAY AREA ---
    
    # Header Section (Dynamic)
    col_logo, col_info = st.columns([1, 5])
    with col_logo:
        if os.path.exists(LOGO_FILE):
            st.image(LOGO_FILE, width=120)
        else:
            st.info("No Logo")
            
    with col_info:
        st.title(profile["company_name"])
        st.write(f"📍 {profile['address']}")
        st.write(f"📞 {profile['mobile']} | ✉️ {profile['email']}")

    st.markdown("---")

    # --- CALCULATOR SECTION ---
    
    st.subheader("☀️ Solar System Calculator")
    
    c1, c2 = st.columns(2)
    
    with c1:
        customer_name = st.text_input("Customer Name")
        monthly_bill = st.number_input("Monthly Electricity Bill (Rs)", min_value=0, value=3000)
        
    with c2:
        cost_per_kw = st.number_input("Installation Cost per kW (Rs)", value=65000)
        unit_rate = st.number_input("Electricity Rate (Rs/Unit)", value=7.5)

    # --- CALCULATIONS ---
    # Assumptions: 1kW generates ~120 units/month in Kerala
    units_consumed = monthly_bill / unit_rate
    needed_kw = units_consumed / 120
    
    # Rounding up to nearest 0.5 kW
    system_size = round(needed_kw * 2) / 2
    if system_size < 1: system_size = 1 # Minimum 1kW
    
    # Financials
    total_cost = system_size * cost_per_kw
    
    # Basic Subsidy Logic (Example: 30k for 1kW, 60k for 2kw, 78k for 3kw+)
    subsidy = 0
    if system_size == 1: subsidy = 30000
    elif system_size == 2: subsidy = 60000
    elif system_size >= 3: subsidy = 78000
    
    net_cost = total_cost - subsidy

    # --- RESULTS DISPLAY ---
    st.markdown("### 📊 Proposal Preview")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Recommended Size", f"{system_size} kW")
    res_col2.metric("Total Cost", f"₹ {total_cost:,.0f}")
    res_col3.metric("Net Cost (After Subsidy)", f"₹ {net_cost:,.0f}", delta=f"Subsidy: ₹{subsidy}")

    # --- PDF DOWNLOAD ---
    st.markdown("---")
    if st.button("📄 Generate PDF Proposal"):
        if customer_name:
            pdf_bytes = create_pdf(profile, customer_name, monthly_bill, system_size, total_cost, subsidy, net_cost)
            
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"Proposal_{customer_name}.pdf",
                mime="application/pdf"
            )
            st.success("PDF Generated Successfully!")
        else:
            st.error("Please enter a Customer Name first.")

if __name__ == "__main__":
    main()
