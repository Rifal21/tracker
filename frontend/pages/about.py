import streamlit as st


def render():
    st.title("ℹ️ About Application")
    st.markdown("""
**FKPhone Tracker v1.0.0** — FKStudio IT Solution · https://fkstudio.id

Tools Phone Number Intelligence & OSINT berbasis sumber legal.

**Batasan:** tidak ada penyadapan, tidak ada pelacakan GPS dari nomor HP, dan informasi geografis/operator
hanyalah metadata penomoran (portabilitas dapat mengubah operator aktual). Lokasi GPS hanya dibagikan
atas persetujuan eksplisit pemilik perangkat.
""")
