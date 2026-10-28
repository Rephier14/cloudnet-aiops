import streamlit as st
import pandas as pd
import re
from groq import Groq

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="NetAIOps Copilot", layout="wide")
st.title("🌐 NetAIOps: Smart NOC & Telemetry Analyzer")
st.caption("Cloud-Native Architecture Ready (Amazon Bedrock / Groq API)")

# 2. Sidebar untuk Input API Key & Simulasi FinOps AWS
with st.sidebar:
    st.header("⚙️ Konfigurasi AI")
    api_key = st.text_input("Masukkan Groq API Key:", type="password")
    st.markdown("[Dapatkan API Key Gratis di sini](https://console.groq.com/keys)")
    
    st.divider()
    st.subheader("🛡️ AI Guardrails (PII/IP Masking)")
    enable_guardrails = st.toggle("Sensor IP Publik Otomatis", value=True)

# 3. Data Simulasi Topologi & Syslog Jaringan
TOPOLOGY = """
[Core-Router-JKT] ---> [Distribution-SW-01] ---> [OLT-Telkom-BDG] ---> [ODP-04-Cakung]
"""

SAMPLE_LOGS = """Oct 28 10:01:02 OLT-Telkom-BDG %OPTIC-3-LOS: Loss of Signal on PON 0/1/4 (ODP-04-Cakung)
Oct 28 10:01:03 OLT-Telkom-BDG %GPON-4-ONU_DYING_GASP: ONU 0/1/4:12 power off or fiber cut
Oct 28 10:01:05 Distribution-SW-01 %OSPF-5-ADJCHG: Process 1, Nbr 103.45.67.89 on Vlan20 from FULL to DOWN
Oct 28 10:01:06 Core-Router-JKT %BGP-5-ADJCHANGE: neighbor 103.45.67.89 Down (Interface flap)"""

# 4. Tampilan Utama (2 Kolom)
col1, col2 = st.columns(2)

with col1:
    st.subheader("📡 Input Syslog & Topologi")
    st.code(TOPOLOGY, language="text")
    raw_logs = st.text_area("Data Log Jaringan (Bisa diedit):", value=SAMPLE_LOGS, height=180)

    # Fungsi Guardrails sederhana (Sensor IP Publik)
    processed_logs = raw_logs
    if enable_guardrails:
        processed_logs = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[REDACTED_IP]', raw_logs)
        st.info("🔒 **Guardrails Aktif:** IP Address berhasil disensor sebelum dikirim ke LLM.")

    analyze_btn = st.button("🚀 Analisis Root Cause dengan AI", type="primary")

with col2:
    st.subheader("🧠 Hasil Diagnosis AI & Rekomendasi CLI")
    if analyze_btn:
        if not api_key:
            st.error("⚠️ **API Key Kosong!** Masukkan Groq API Key kamu di kolom menu sebelah kiri terlebih dahulu.")
        else:
            try:
                with st.spinner("Menghubungkan ke Groq API & menganalisis log..."):
                    # Inisialisasi client Groq dengan API Key dari input user
                    client = Groq(api_key=api_key.strip())
                    
                    prompt = f"""
                    Kamu adalah Senior Network & Optical Engineer.
                    Topologi: {TOPOLOGY}
                    Log Insiden:
                    {processed_logs}
                    
                    Tugas:
                    1. Tentukan 1 Root Cause utama (apakah masalah optik/fisik atau routing?).
                    2. Jelaskan kenapa alert lainnya hanya dampak turunan (symptomatic).
                    3. Berikan langkah troubleshooting (misal: cek OTDR atau command CLI).
                    """
                    
                    response = client.chat.completions.create(
                        model="llama-3.1-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2
                    )
                    
                    ai_output = response.choices[0].message.content
                    tokens_used = response.usage.total_tokens
                    
                    st.success("Analisis Selesai!")
                    st.markdown(ai_output)
                    
                    # Simulasi Perhitungan Biaya AWS Bedrock (FinOps)
                    bedrock_cost = (tokens_used / 1000) * 0.000035
                    st.divider()
                    st.caption(f"📊 **FinOps Metric:** Total Token: `{tokens_used}` | Estimasi Biaya jika di **AWS Bedrock (Nova Micro)**: `${bedrock_cost:.6f}` (~Rp {bedrock_cost*16000:.2f})")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat memanggil Groq API. Pastikan API Key benar dan aktif.\n\nDetail Error: `{e}`")
