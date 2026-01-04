import streamlit as st
from fpdf import FPDF
import base64

# --- 1. SETUP THE PDF CLASS ---
class SolarProposal(FPDF):
    def __init__(self, company_name, phone, email, logo_path=None):
        super().__init__()
        self.company_name = company_name
        self.phone = phone
        self.email = email
        self.logo_path = logo_path

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        footer_text = f"Page {self.page_no()} | {self.company_name} | {self.phone} | {self.email}"
        self.cell(0, 10, footer_text, 0, 0, 'C')

def create_pdf(company_info, customer_info, items, total_amount, bg_image):
    pdf = SolarProposal(company_info['name'], company_info['phone'], company_info['email'])
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- PAGE 1: COVER ---
    pdf.add_page()
    
    # Background Image (The Kerala Doodle)
    if bg_image:
        # Saving temp file to use in PDF
        with open("temp_bg.jpg", "wb") as f:
            f.write(bg_image.getbuffer())
        # Place image at bottom (x=0, y=120, width=210)
        pdf.image("temp_bg.jpg", x=0, y=120, w=210)

    # Header Info
    pdf.set_font("Arial", "B", 24)
    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "SOLAR POWER SYSTEM", 0, 1, 'C')
    pdf.set_font("Arial", "", 18)
    pdf.cell(0, 10, "PROJECT PROPOSAL", 0, 1, 'C')
    
    pdf.ln(20)
    
    # Customer Details Box
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, 70, 190, 50, 'F')
    
    pdf.set_y(75)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(15)
    pdf.cell(0, 10, "PREPARED FOR:", 0, 1)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(15)
    pdf.cell(0, 8, f"Name: {customer_info['name']}", 0, 1)
    pdf.cell(15)
    pdf.cell(0, 8, f"Location: {customer_info['address']}", 0, 1)
    pdf.cell(15)
    pdf.cell(0, 8, f"Date: {customer_info['date']}", 0, 1)

    # Company Branding (Top Left)
    pdf.set_xy(10, 10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, company_info['name'], 0, 1)

    # --- PAGE 2: COMMERCIALS ---
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"System Specification: {customer_info['system_size']}", 0, 1, 'L')
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(230, 240, 255) # Light Solar Blue
    pdf.cell(15, 10, "#", 1, 0, 'C', 1)
    pdf.cell(90, 10, "Item Description", 1, 0, 'C', 1)
    pdf.cell(20, 10, "Qty", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Price", 1, 0, 'C', 1)
    pdf.cell(35, 10, "Total", 1, 1, 'C', 1)

    # Table Rows
    pdf.set_font("Arial", "", 10)
    fill = False
    for idx, item in enumerate(items):
        qty = float(item['Qty'])
        rate = float(item['Rate'])
        line_total = qty * rate
        
        pdf.cell(15, 10, str(idx+1), 1)
        pdf.cell(90, 10, item['Item'], 1)
        pdf.cell(20, 10, str(item['Qty']), 1, 0, 'C')
        pdf.cell(30, 10, f"{rate:,.0f}", 1, 0, 'R')
        pdf.cell(35, 10, f"{line_total:,.0f}", 1, 1, 'R')

    # Grand Total
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(155, 10, "GRAND TOTAL (INR)", 1, 0, 'R')
    pdf.cell(35, 10, f"{total_amount:,.0f}", 1, 1, 'R')
    
    pdf.ln(15)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "Terms & Conditions:", 0, 1)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 6, "1. Payment: 70% Advance, 30% upon completion.\n2. Delivery: Within 2 weeks of advance payment.\n3. Warranty: As per manufacturer standards (25 Years Performance on Panels).")

    return pdf.output(dest='S').encode('latin-1')

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="Solar Proposal Generator", page_icon="☀️")

st.title("☀️ Solar Proposal Generator")
st.markdown("Generate a PDF proposal with a Kerala-themed design.")

# SIDEBAR: Company Info
st.sidebar.header("Your Company Details")
co_name = st.sidebar.text_input("Company Name", "Solar Tech Kerala")
co_phone = st.sidebar.text_input("Phone", "+91-9876543210")
co_email = st.sidebar.text_input("Email", "info@solartechkerala.com")
bg_image = st.sidebar.file_uploader("Upload Cover Image (Jpg/Png)", type=['jpg', 'png', 'jpeg'])

# MAIN AREA: Customer Info
col1, col2 = st.columns(2)
with col1:
    cust_name = st.text_input("Customer Name", "Mr. John Doe")
    cust_addr = st.text_input("Location/Address", "Kochi, Kerala")
with col2:
    sys_size = st.text_input("System Size", "5kW On-Grid System")
    prop_date = st.date_input("Date")

# BILL OF MATERIALS (Editable Table)
st.subheader("Bill of Materials & Pricing")

# Default Data
default_items = [
    {"Item": "Solar PV Modules (Mono PERC Half Cut)", "Qty": 10, "Rate": 18000},
    {"Item": "Solar Inverter (On-Grid)", "Qty": 1, "Rate": 45000},
    {"Item": "Mounting Structure (HDG)", "Qty": 1, "Rate": 15000},
    {"Item": "AC/DC Cables & Earthing Kit", "Qty": 1, "Rate": 12000},
    {"Item": "Installation & Liaisoning Charges", "Qty": 1, "Rate": 20000},
]

# The Editable Table
edited_data = st.data_editor(default_items, num_rows="dynamic")

# Calculate Total Live
total_val = sum([float(item['Qty']) * float(item['Rate']) for item in edited_data])
st.metric(label="Total Project Value", value=f"₹ {total_val:,.2f}")

# GENERATE BUTTON
if st.button("Generate PDF Proposal"):
    company_info = {'name': co_name, 'phone': co_phone, 'email': co_email}
    customer_info = {'name': cust_name, 'address': cust_addr, 'date': prop_date, 'system_size': sys_size}
    
    # Generate PDF
    pdf_bytes = create_pdf(company_info, customer_info, edited_data, total_val, bg_image)
    
    st.success("PDF Generated! Click below to download.")
    st.download_button(
        label="Download Proposal PDF",
        data=pdf_bytes,
        file_name=f"Proposal_{cust_name.replace(' ', '_')}.pdf",
        mime='application/pdf'
    )
