from datetime import date, timedelta

import pandas as pd
import streamlit as st

from components.api import call


def render():
    st.title("🕘 Search History")
    c1, c2 = st.columns(2)
    start = c1.date_input("Dari", date.today() - timedelta(days=30))
    end = c2.date_input("Sampai", date.today())
    rows = call("GET", "/api/v1/history", params={"start": start.isoformat(), "end": end.isoformat()})
    if rows is None:
        return
    if not rows:
        st.info("Tidak ada riwayat.")
        return
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Unduh CSV", df.to_csv(index=False), "history.csv", "text/csv")
    d1, d2 = st.columns(2)
    hid = d1.number_input("ID yang dihapus", min_value=1, step=1)
    if d1.button("Hapus satu"):
        if call("DELETE", f"/api/v1/history/{int(hid)}"):
            st.rerun()
    if d2.button("Hapus semua riwayat", type="primary"):
        if call("DELETE", "/api/v1/history") is not None:
            st.rerun()
