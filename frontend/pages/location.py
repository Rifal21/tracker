import folium
import streamlit as st
from streamlit_folium import st_folium

from components.api import call


def render():
    st.title("📍 Location Sharing")
    st.info("Berbasis persetujuan: pemilik perangkat membuka tautan, menyetujui, lalu mengizinkan GPS di browser. "
            "Tidak ada pelacakan hanya dari nomor HP.")
    ttl = st.number_input("Masa berlaku tautan (menit)", 1, 1440, 60)
    if st.button("Buat tautan berbagi"):
        r = call("POST", "/api/v1/location/share", json={"ttl_minutes": int(ttl)})
        if r:
            st.session_state["share"] = r
    s = st.session_state.get("share")
    if s:
        st.code(s["share_url"])
        st.caption(f"Berlaku hingga {s['expires_at']}. Token hanya ditampilkan sekali; hash-nya yang disimpan.")
        if st.button("Periksa status"):
            v = call("POST", "/api/v1/location/view", json={"token": s["token"]})
            if v:
                st.write(f"Status: **{v['status']}**")
                if v["latitude"] is not None:
                    m = folium.Map([v["latitude"], v["longitude"]], zoom_start=15)
                    folium.Marker([v["latitude"], v["longitude"]]).add_to(m)
                    st_folium(m, height=400, use_container_width=True)
        if st.button("Cabut tautan"):
            if call("POST", "/api/v1/location/revoke", json={"token": s["token"]}):
                st.success("Dicabut; koordinat dihapus.")
