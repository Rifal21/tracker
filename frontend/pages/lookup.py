import streamlit as st

from components.api import call


def render():
    st.title("🔎 Phone Number Lookup")
    with st.form("f"):
        num = st.text_input("Nomor telepon", placeholder="+6281234567890 atau 081234567890")
        region = st.text_input("Kode negara default (ISO, mis. ID)", value="ID", max_chars=2)
        ok = st.form_submit_button("Analisis")
    if not ok or not num:
        return
    r = call("POST", "/api/v1/phone/lookup", json={"phone_number": num, "default_region": region or None})
    if not r:
        return
    if r.get("error"):
        st.error(r["error"])
        return
    (st.success if r["valid"] else st.warning)("Nomor valid" if r["valid"] else "Nomor tidak valid")
    a, b = st.columns(2)
    a.write({k: r[k] for k in ("phone_number", "international", "national", "country", "country_code",
                               "calling_code", "prefix")})
    b.write({k: r[k] for k in ("valid", "possible", "number_type", "carrier", "region", "timezones")})
    st.caption(r["carrier_note"])
    st.caption(r["location_note"])
