import streamlit as st
import pandas as pd
import os
import time
import re

LOG_FILE = "logs.txt"
REFRESH_INTERVAL = 10  # seconds

st.set_page_config(page_title="NetPulse Dashboard", layout="wide")

st.title("📡 NetPulse: Network Monitor Dashboard")
st.caption(f"🔄 Auto-refreshes every {REFRESH_INTERVAL} seconds")

# Auto-refresh every N seconds
st.experimental_rerun_delay = REFRESH_INTERVAL  # hidden Streamlit prop (will trigger rerun)

# Load and parse logs
if not os.path.exists(LOG_FILE):
    st.warning("⚠️ Log file not found. Please run `main.py` first.")
else:
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        st.info("🕒 No data logged yet.")
    else:
        records = []
        for line in lines:
            if "|" not in line:
                continue
            parts = line.strip().split(" | ")
            if len(parts) != 2:
                continue
            time_status, latency_raw = parts
            match = re.match(r"\[(.*?)\] (.*?) is (\w+)", time_status)
            if match:
                timestamp, ip, status = match.groups()
                latency = latency_raw.replace("Latency: ", "")
                records.append({
                    "Timestamp": timestamp,
                    "IP": ip,
                    "Status": status,
                    "Latency": latency
                })

        df = pd.DataFrame(records)

        # Display recent data
        st.subheader("📋 Last 30 Pings")
        st.dataframe(df.tail(30), use_container_width=True)

        # 📈 Latency Trend Graph
        st.subheader("📈 Latency Trend")
        latency_df = df[(df["Latency"] != "N/A ms") & (df["Status"] == "UP")].copy()
        if not latency_df.empty:
            latency_df["Timestamp"] = pd.to_datetime(latency_df["Timestamp"])
            latency_df["Latency (ms)"] = latency_df["Latency"].str.extract(r'([\d.]+)').astype(float)
            chart = latency_df.pivot_table(index="Timestamp", columns="IP", values="Latency (ms)")
            st.line_chart(chart)
        else:
            st.info("No valid latency data available yet.")

        # 🟢 Uptime % per device
        st.subheader("🟢 Uptime % Per Device")
        uptime_summary = df.groupby("IP")["Status"].value_counts().unstack().fillna(0)
        uptime_summary["Uptime %"] = (uptime_summary.get("UP", 0) / uptime_summary.sum(axis=1)) * 100
        uptime_display = uptime_summary[["Uptime %"]].round(2).sort_values(by="Uptime %", ascending=False)
        st.dataframe(uptime_display)

        # Metric: Overall Average Latency
        avg_latency = latency_df["Latency (ms)"].mean() if not latency_df.empty else None
        if avg_latency:
            st.metric(label="🌐 Average Latency (UP Hosts)", value=f"{avg_latency:.2f} ms")

        # 🔄 Auto-refresh notice
        st.empty()  # allows time-based rerun
        time.sleep(REFRESH_INTERVAL)
        st.experimental_rerun()
# 📁 Export to CSV
st.subheader("📤 Export Logs")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download logs as CSV",
    data=csv,
    file_name='netpulse_logs.csv',
    mime='text/csv'
)
