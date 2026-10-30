import pandas as pd
import plotly.express as px
import streamlit as st

from components.api import call


def render():
    st.title("📊 Dashboard")
    s = call("GET", "/api/v1/history/stats")
    if not s:
        return
    c1, c2, c3 = st.columns(3)
    c1.metric("Total pencarian", s["total"])
    c2.metric("Nomor valid", s["valid"])
    c3.metric("Nomor tidak valid", s["invalid"])
    left, right = st.columns(2)
    if s["per_day"]:
        df = pd.DataFrame({"tanggal": list(s["per_day"]), "pencarian": list(s["per_day"].values())})
        left.plotly_chart(px.bar(df, x="tanggal", y="pencarian", title="Pencarian per hari"), use_container_width=True)
    if s["total"]:
        pie = pd.DataFrame({"status": ["Valid", "Tidak valid"], "jumlah": [s["valid"], s["invalid"]]})
        right.plotly_chart(px.pie(pie, names="status", values="jumlah", title="Validitas"), use_container_width=True)
    st.subheader("Aktivitas terbaru")
    if s["recent"]:
        st.dataframe(pd.DataFrame(s["recent"]), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada aktivitas.")
