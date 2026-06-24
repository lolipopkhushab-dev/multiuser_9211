import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime
import threading

# Page Configuration
st.set_page_config(page_title="9211 Multi-User Automation Dashboard", layout="wide")

st.title("🚜 9211 Portal Multi-User Data Sender")
st.markdown("---")

# Global dictionary to track background job status safely across threads
if 'jobs' not in st.session_state:
    st.session_state.jobs = {}

def get_headers(bearer_token, fcm_token):
    return {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': f'Bearer {bearer_token}',
        'content-type': 'application/json',
        'fcmtoken': fcm_token,
        'origin': 'https://vax.9211.pk',
        'priority': 'u=1, i',
        'referer': 'https://vax.9211.pk/',
        'sec-ch-ua': '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; V2205 Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36'
    }

# Background Worker Function that runs even if browser disconnects
def background_uploader(user_id, df, bearer, fcm):
    st.session_state.jobs[user_id] = {"status": "Running", "progress": 0, "total": len(df), "success": 0, "failed": 0, "log": []}
    headers = get_headers(bearer, fcm)
    url = 'https://api.vax.9211.pk/api/AnimalVaccination/AddAnimalVaccinationV4'
    
    total_rows = len(df)
    
    for index, row in df.iterrows():
        try:
            # Preparing payload exactly as your original code
            payload = {
                "VaccinationId": 0,
                "AnimalId": int(row['AnimalId']),
                "TagNo": str(row['TagNo']),
                "VaccineId": int(row['VaccineId']),
                "VaccinationDate": str(row['VaccinationDate']),
                "IsVerified": True,
                "EmployeeId": int(row['EmployeeId']),
                "Latitude": float(row['Latitude']),
                "Longitude": float(row['Longitude']),
                "DynamicVaccinationFields": []
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_index == 200 or response.status_code == 201:
                st.session_state.jobs[user_id]["success"] += 1
            else:
                st.session_state.jobs[user_id]["failed"] += 1
                st.session_state.jobs[user_id]["log"].append(f"Row {index+1} (Tag: {row['TagNo']}): Error {response.status_code} - {response.text}")
                
        except Exception as e:
            st.session_state.jobs[user_id]["failed"] += 1
            st.session_state.jobs[user_id]["log"].append(f"Row {index+1}: Exception - {str(e)}")
            
        # Update progress dynamically
        st.session_state.jobs[user_id]["progress"] = index + 1
        
    st.session_state.jobs[user_id]["status"] = "Completed ✅"

# Main Layout: 20 Slots for 20 Users
num_users = st.sidebar.number_input("Kitne Users Ka Data Upload Karna Hai?", min_value=1, max_value=30, value=5)

user_data_inputs = []

st.subheader("📋 Enter Details For Each User Profile")

for i in range(int(num_users)):
    user_id = f"User_{i+1}"
    with st.expander(f"👤 USER PROFILE #{i+1} Configuration", expanded=True):
        col1, col2, col3 = st.columns([1, 2, 2])
        
        with col1:
            uploaded_file = st.file_uploader(f"Upload CSV File", type=["csv"], key=f"file_{user_id}")
        with col2:
            bearer_input = st.text_input(f"Bearer Token", placeholder="eyJhbGciOi...", key=f"bearer_{user_id}")
        with col3:
            fcm_input = st.text_input(f"FCM Token", placeholder="fL5xO-...", key=f"fcm_{user_id}")
            
        if uploaded_file and bearer_input and fcm_input:
            try:
                df = pd.read_csv(uploaded_file)
                user_data_inputs.append({
                    "id": user_id,
                    "df": df,
                    "bearer": bearer_input,
                    "fcm": fcm_input
                })
                st.success(f"✔️ Validated: Total {len(df)} records found in CSV.")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

st.markdown("---")

# Global Action Button
if len(user_data_inputs) > 0:
    if st.button("🚀 START ALL ONLINE BACKGROUND UPLOADS", type="primary", use_container_width=True):
        for data in user_data_inputs:
            # Check if job is already running to avoid double triggers
            if data["id"] not in st.session_state.jobs or st.session_state.jobs[data["id"]]["status"] != "Running":
                # Spawning independent threads for background tasks
                t = threading.Thread(
                    target=background_uploader, 
                    args=(data["id"], data["df"], data["bearer"], data["fcm"])
                )
                t.daemon = True # Allows thread to run in background independently
                t.start()
        st.success("All configured user uploads have been kicked off in the cloud backend! You can safely close your system.")

# Live Status Dashboard
if st.session_state.jobs:
    st.markdown("---")
    st.subheader("📊 Live Background Process Monitor")
    
    for user_id, info in st.session_state.jobs.items():
        with st.container():
            col_name, col_status, col_prog = st.columns([1, 1, 3])
            with col_name:
                st.write(f"**{user_id}**")
            with col_status:
                if info["status"] == "Running":
                    st.info(f"⏳ Processing ({info['success']} Sent, {info['failed']} Failed)")
                else:
                    st.success(info["status"])
            with col_prog:
                progress_percentage = min(1.0, info["progress"] / info["total"]) if info["total"] > 0 else 0.0
                st.progress(progress_percentage, text=f"{info['progress']}/{info['total']} Rows Done")
                
            # Expander for errors if any
            if info["log"]:
                with st.expander(f"⚠️ Show Error Logs for {user_id}"):
                    for log_msg in info["log"][-10:]: # Show last 10 errors
                        st.caption(log_msg)
