import pandas as pd
import streamlit as st

from components.api import call


def render():
    st.title("🌐 OSINT Search")
    st.caption("Hanya tautan ke sumber publik yang sah. Gunakan dengan dasar hukum/otorisasi yang jelas.")
    num = st.text_input("Nomor telepon", placeholder="+6281234567890")
    check = st.checkbox("Periksa ketersediaan sumber (HTTP HEAD)")
    if st.button("Cari") and num:
        r = call("POST", f"/api/v1/osint/search?check={str(check).lower()}", json={"phone_number": num})
        if r:
            st.write(f"Nomor: **{r['phone_number']}** · riwayat #{r['history_id']}")
            df = pd.DataFrame(r["sources"])
            st.dataframe(df, use_container_width=True, hide_index=True,
                         column_config={"source_url": st.column_config.LinkColumn("source_url")})
