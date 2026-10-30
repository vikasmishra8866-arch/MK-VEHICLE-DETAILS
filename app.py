import time
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="VahanVerify Pro - Vehicle Information Portal",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Premium Dark Theme Styling
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0b132b;
            color: #f3f4f6;
        }
        .main-card {
            background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
        }
        .info-box {
            background-color: #1c2541;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .label-text {
            color: #94a3b8;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
        }
        .val-text {
            color: #f8fafc;
            font-size: 0.9rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }
        .badge {
            background-color: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        /* Hide Streamlit default hamburger menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize Session State for Cooldown
if "last_search_time" not in st.session_state:
    st.session_state.last_search_time = 0.0

# Header Section
st.markdown(
    """
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: white; font-size: 2.2rem; font-weight: 800; margin-bottom: 5px;">VahanVerify <span style="color: #3b82f6; font-size: 1rem; background: rgba(59, 130, 246, 0.1); padding: 4px 10px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.2);">PRO</span></h1>
        <p style="color: #94a3b8; font-size: 0.85rem;">Official Vehicle Information & History Gateway</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Search Input Form
with st.form(key="search_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        reg_input = st.text_input(
            "Enter Registration Number",
            value="",
            placeholder="e.g. GJ39CD0387",
            label_visibility="collapsed",
        )
    with col2:
        submit_btn = st.form_submit_button(
            "Search Vehicle", use_container_width=True
        )

# Helper function to validate non-null values
val = lambda x: x if x is not None and str(x).strip().lower() not in ["", "null", "none", "na", "n/a", "0"] else None

if submit_btn:
    clean_reg = "".join(ch for ch in reg_input if ch.isalnum()).upper().strip()

    if not clean_reg:
        st.warning("⚠️ Please enter a valid vehicle registration number.")
    else:
        current_time = time.time()
        time_diff = current_time - st.session_state.last_search_time
        cooldown_period = 10.0

        if time_diff < cooldown_period:
            remaining = int(cooldown_period - time_diff) + 1
            st.error(f"⏳ Please wait {remaining} seconds before making another search (Cooldown Active).")
        else:
            st.session_state.last_search_time = time.time()

            # API Request Execution with Spinner
            api_url = f"https://hideme.eu.org/lookup?api=mvahan&key=mk-4px4ohkcxybb&number={clean_reg}"
            
            with st.spinner("🔄 Fetching vehicle records from RTO Database..."):
                try:
                    response = requests.get(api_url, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data and data.get("success") is True and "vehicle" in data:
                            v = data["vehicle"]
                            
                            st.success("✅ Vehicle Records Fetched Successfully!")
                            
                            # Top Banner Card
                            full_model = " ".join([m for m in [v.get("make"), v.get("model"), v.get("variant")] if val(m)])
                            
                            st.markdown(
                                f"""
                                <div class="main-card">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
                                        <div>
                                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 800; color: white;">{v.get('registration_no', clean_reg)}</span>
                                            <p style="color: #cbd5e1; font-size: 1rem; margin-top: 5px; font-weight: 600;">{full_model if full_model else 'Vehicle Details'}</p>
                                        </div>
                                        <div>
                                            <span class="badge">ACTIVE</span>
                                        </div>
                                    </div>
                                    <div style="display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap;">
                                        {f'<span style="background: rgba(59, 130, 246, 0.1); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-family: monospace;">FUEL: {v.get("fuel").upper()}</span>' if val(v.get('fuel')) else ''}
                                        {f'<span style="background: rgba(59, 130, 246, 0.1); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-family: monospace;">CLASS: {v.get("vehicle_class")}</span>' if val(v.get('vehicle_class')) else ''}
                                    </div>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                            # Detailed Grid Layout
                            c1, c2 = st.columns(2)

                            with c1:
                                st.markdown("### 👤 Owner Details")
                                if val(v.get("owner")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Owner Name</div><div class="val-text">{v.get("owner")}</div></div>', unsafe_allow_html=True)
                                if val(data.get("mobile")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Mobile Number</div><div class="val-text" style="color: #34d399;">{data.get("mobile")}</div></div>', unsafe_allow_html=True)
                                if val(v.get("father_name")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Father\'s Name</div><div class="val-text">{v.get("father_name")}</div></div>', unsafe_allow_html=True)
                                if val(v.get("city")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">City / RTO Region</div><div class="val-text">{v.get("city")}</div></div>', unsafe_allow_html=True)

                                st.markdown("### 🛡️ Insurance Info")
                                if val(v.get("insurance_company")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Insurance Company</div><div class="val-text">{v.get("insurance_company")}</div></div>', unsafe_allow_html=True)
                                if val(v.get("insurance_upto")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Insurance Expiry</div><div class="val-text">{v.get("insurance_upto")}</div></div>', unsafe_allow_html=True)

                            with c2:
                                st.markdown("### ⚙️ Technical Specs")
                                if val(v.get("chassis")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Chassis Number</div><div class="val-text">{v.get("chassis")}</div></div>', unsafe_allow_html=True)
                                if val(data.get("chassis_last5")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Chassis (Last 5)</div><div class="val-text">{data.get("chassis_last5")}</div></div>', unsafe_allow_html=True)
                                if val(v.get("engine")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Engine Number</div><div class="val-text">{v.get("engine")}</div></div>', unsafe_allow_html=True)
                                if val(v.get("color")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Color</div><div class="val-text">{v.get("color")}</div></div>', unsafe_allow_html=True)
                                if val(v.get("body_type")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Body Type</div><div class="val-text">{v.get("body_type")}</div></div>', unsafe_allow_html=True)

                                st.markdown("### 📋 RC & Compliance")
                                if val(v.get("rto")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">RTO Authority</div><div class="val-text">{v.get("rto")}</div></div>', unsafe_allow_html=True)
                                if val(v.get("registration_date")):
                                    st.markdown(f'<div class="info-box"><div class="label-text">Registration Date</div><div class="val-text">{v.get("registration_date")}</div></div>', unsafe_allow_html=True)

                            # Address Card (Full Width)
                            if val(v.get("address")):
                                st.markdown("### 📍 Registered Address")
                                st.markdown(f'<div class="info-box"><div class="val-text" style="font-family: Inter, sans-serif; font-size: 0.85rem; font-weight: 500; line-height: 1.5;">{v.get("address")}</div></div>', unsafe_allow_html=True)

                        else:
                            st.error("❌ Details not found. Please check the vehicle registration number and try again.")
                    else:
                        st.error("⚠️ Network error or API gateway timeout. Please try again after some time.")
                except Exception as e:
                    st.error(f"⚠️ An error occurred while connecting to the server: {e}")

# Footer
st.markdown(
    """
    <div style="text-align: center; padding: 30px 0; color: #64748b; font-size: 0.75rem;">
        <p>&copy; 2026 VahanVerify Pro. Secured & Optimized for Streamlit Cloud.</p>
    </div>
""",
    unsafe_allow_html=True,
)
