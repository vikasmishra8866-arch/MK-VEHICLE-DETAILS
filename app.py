import streamlit as st
import requests
import uuid

st.set_page_config(page_title="Vehicle RC Finder", page_icon="🚗", layout="centered")

st.title("🚗 Vehicle RC Detail Finder")
st.write("गाड़ी का नंबर दर्ज करके तुरंत वाहन की जानकारी प्राप्त करें।")

# यूजर इनपुट
rc_number = st.text_input("गाड़ी नंबर दर्ज करें (जैसे: MH04AB1234)").strip().upper()

if st.button("डेटा देखें", type="primary"):
    if not rc_number:
        st.warning("कृपया पहले गाड़ी का नंबर दर्ज करें!")
    else:
        with st.spinner("डेटा फेच किया जा रहा है..."):
            session_id = f"{uuid.uuid4()}-{uuid.uuid4()}"
            url = "https://api1.91wheels.com/api/v1/third/rc-detail"

            payload = {
                "regNo": rc_number,
                "sessionid": session_id
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://www.91wheels.com",
                "Referer": "https://www.91wheels.com/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile Safari/537.36)"
            }

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=20)
                result = response.json()
                
                st.success("सफलतापूर्वक जानकारी मिल गई!")
                st.json(result)
                
            except Exception as e:
                st.error(f"कनेक्शन एरर: {str(e)}")
