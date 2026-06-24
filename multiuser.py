import streamlit as st
import pandas as pd
import requests
import time
import random
import threading

# Page Configuration
st.set_page_config(page_title="9211 Multi-User Dashboard", page_icon="💉", layout="wide")

st.title("🚜 9211 Portal Multi-User Advanced Data Sender")
st.write("Har user ka apna 'Run' button hoga. Details fill karein aur us makhsoos user ki automation shuru karein.")

# --- PERSISTENT GLOBAL STORAGE ---
if "global_jobs" not in st.session_state:
    st.session_state["global_jobs"] = {}

VACCINE_LIST = (
    "Haemorrhagic Septicemia Vaccine (HS)",
    "Black Quarter Vaccine (BQV)",
    "Enterotoxaemia Vaccine (ETV)",
    "Foot and Mouth Disease (FMD - Local)",
    "Foot and Mouth Disease (FMD - Imported)",
    "Caprine Pleuro Pneumonia Vaccine (CCPV)",
    "P.P.R. Vaccine",
    "N.D Vaccine (Lasota)"
)

# --- BACKGROUND WORKER FUNCTION ---
def execution_worker(user_id, df, bearer_token, fcm_token, vaccine_option, start_row=0):
    job_state = st.session_state["global_jobs"][user_id]
    job_state["status"] = "Running ⏳"
    
    API_URL = 'https://spms9211api.punjab.gov.pk/api/Vaccination/Add'
    headers = {
        'Authorization': f"Bearer {bearer_token}",
        'fcmtoken': fcm_token,
        'HashKey': 'gwKpvUg6skx96JHp4sRvt/bGkRw=',
        'X-API-KEY': 'A06B691B-8D21-42BB-9E39-9AF570F71105-9211@AP!',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'spms9211api.punjab.gov.pk',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp/4.5.0'
    }

    for index in range(start_row, len(df)):
        # Check if user requested a stop
        if st.session_state["global_jobs"][user_id]["status"] == "Stopped 🛑":
            break
            
        row = df.iloc[index]
        csv_animal_code = str(row['animalCode']).upper().strip() if 'animalCode' in df.columns else 'C'
        
        # Exact Extraction Logic from original code
        if "HS" in vaccine_option:
            v_type = 219; s_id = 3; item_code = "04210350010"; item_abbr = "VHSOB50N"
            v_name = "Haemorrhagic Septicemia Vaccine O/B - 50ml"
            curr_bal = 64.0; sub_bal = 0.24; per_unit = 50; no_of_doses = 2.0
            if csv_animal_code == 'B':
                animal_type_str = "B, Buffalo ( 2.0 )"; a_id = 2; a_name = "Buffalo"; a_nested_id = 160
            else:
                animal_type_str = "C, Cow ( 2.0 )"; a_id = 1; a_name = "Cow"; a_nested_id = 70
        elif "BQV" in vaccine_option:
            v_type = 845; s_id = 5; item_code = "04220220429"; item_abbr = "VBQC50N"
            v_name = "Black Quarter Vaccine - 50ml (Conc.)"
            curr_bal = 64.0; sub_bal = 0.24; per_unit = 50; no_of_doses = 2.0
            if csv_animal_code == 'B':
                animal_type_str = "B, Buffalo ( 2.0 )"; a_id = 2; a_name = "Buffalo"; a_nested_id = 160
            else:
                animal_type_str = "C, Cow ( 2.0 )"; a_id = 1; a_name = "Cow"; a_nested_id = 70
        elif "ETV" in vaccine_option:
            v_type = 223; s_id = 6; item_code = "04250270014"; item_abbr = "VET50N"
            v_name = "Enterotoxaemia Vaccine - 50 ml"
            curr_bal = 64.0; sub_bal = 0.24; per_unit = 50; no_of_doses = 2.0
            if csv_animal_code == 'S':
                animal_type_str = "S, Sheep ( 1.0 )"; a_id = 7; a_name = "Sheep"; a_nested_id = 7610
            else:
                animal_type_str = "G, Goat ( 1.0 )"; a_id = 8; a_name = "Goat"; a_nested_id = 7611
        elif "Local" in vaccine_option:
            v_type = 254; s_id = 13; item_code = "04230230045"; item_abbr = "VFMDOB50N"
            v_name = "Foot and mouth disease O/B - 50 ml"
            curr_bal = 64.0; sub_bal = 0.24; per_unit = 50; no_of_doses = 2.0
            if csv_animal_code == 'B':
                animal_type_str = "B, Buffalo ( 2.0 )"; a_id = 2; a_name = "Buffalo"; a_nested_id = 160
            else:
                animal_type_str = "C, Cow ( 2.0 )"; a_id = 1; a_name = "Cow"; a_nested_id = 70
        elif "Imported" in vaccine_option:
            v_type = 1012; s_id = 13; item_code = "04230247020"; item_abbr = "VFMDI50N"
            v_name = "Foot and Mouth Disease -50ml (Imported)"
            curr_bal = 64.0; sub_bal = 0.24; per_unit = 50; no_of_doses = 2.0
            if csv_animal_code == 'B':
                animal_type_str = "B, Buffalo ( 2.0 )"; a_id = 2; a_name = "Buffalo"; a_nested_id = 160
            else:
                animal_type_str = "C, Cow ( 2.0 )"; a_id = 1; a_name = "Cow"; a_nested_id = 70
        elif "CCPV" in vaccine_option:
            v_type = 256; s_id = 11; item_code = "04270300047"; item_abbr = "VCP100N"
            v_name = "Caprine Pleuro Pneumonia Vaccine - 100 doses"
            curr_bal = 159.30; sub_bal = 0.17; per_unit = 100; no_of_doses = 1.0
            if csv_animal_code == 'S':
                animal_type_str = "S, Sheep ( 1.0 )"; a_id = 7; a_name = "Sheep"; a_nested_id = 7610
            else:
                animal_type_str = "G, Goat ( 1.0 )"; a_id = 8; a_name = "Goat"; a_nested_id = 7611
        elif "P.P.R." in vaccine_option:
            v_type = 233; s_id = 12; item_code = "04260280024"; item_abbr = "VPPR100N"
            v_name = "P.P.R. Vaccine Along with Diluent-100 doses"
            curr_bal = 159.30; sub_bal = 0.17; per_unit = 100; no_of_doses = 1.0
            if csv_animal_code == 'S':
                animal_type_str = "S, Sheep ( 1.0 )"; a_id = 7; a_name = "Sheep"; a_nested_id = 7610
            else:
                animal_type_str = "G, Goat ( 1.0 )"; a_id = 8; a_name = "Goat"; a_nested_id = 7611
        else:
            v_type = 249; s_id = 8; item_code = "04300330040"; item_abbr = "VNDL200N"
            v_name = "N.D Vaccine (Lasota) -200 doses"
            curr_bal = 159.30; sub_bal = 0.17; per_unit = 200; no_of_doses = 1.0
            animal_type_str = "P, Poultry ( 1.0 )"; a_id = 9; a_name = "Poultry"; a_nested_id = 9

        payload = {
            "MouzaCode": str(row['MouzaCode']),
            "CreatedBy": int(row['CreatedBy']),
            "districtID": int(row['districtID']),
            "divisionID": int(row['divisionID']),
            "FarmerID": int(row['FarmerID']),
            "latitude": str(row['latitude']),
            "longitude": str(row['longitude']),
            "mouzaID": int(row['mouzaID']),
            "os": 30,
            "tehsilID": int(row['tehsilID']),
            "vaccinationLists": [{
                "animalLists": [{
                    "animalType": animal_type_str,
                    "animalTypeID": a_id,
                    "lastSubtractedBalance": sub_bal,
                    "medicineTypesItem": {
                        "animals": [{"animalCode": csv_animal_code, "animalID": a_id, "id": a_nested_id, "name": a_name, "noOfDoses": no_of_doses}],
                        "currentBalance": curr_bal, "id": v_type, "isVaccine": True, "itemAbbreviation": item_abbr, "itemCode": item_code, "itemDescription": v_name, "perUnitMeasurement": per_unit
                    },
                    "noOfAnimals": int(row['noOfAnimals']) if pd.notna(row['noOfAnimals']) else 1
                }],
                "BatchNo": str(row['BatchNo']), "HospitalID": int(row['HospitalID']), "serviceID": s_id, "vaccineName": v_name, "VaccineType": v_type
            }],
            "version": "1.3.0"
        }

        try:
            r = requests.post(API_URL, json=payload, headers=headers, timeout=20)
            if r.status_code == 200 or r.status_code == 201:
                job_state["success_count"] += 1
            elif r.status_code == 401:
                job_state["status"] = "Error ❌"
                job_state["last_error"] = "Session Expired (401 Error). Naya Bearer Code dalein!"
                break
            else:
                job_state["status"] = "Error ❌"
                job_state["last_error"] = f"Row {index+1} Error {r.status_code}: {r.text[:100]}"
                break
        except Exception as e:
            job_state["status"] = "Error ❌"
            job_state["last_error"] = f"Network Timeout / Exception: {str(e)}"
            break

        # Save exact location
        job_state["current_index"] = index + 1
        
        # Random Delay: 40 to 100 seconds
        time.sleep(random.randint(40, 100))

    if job_state["current_index"] >= job_state["total_records"] and job_state["status"] == "Running ⏳":
        job_state["status"] = "Completed 🎉"

# --- SIDEBAR CONTROL ---
num_users = st.sidebar.number_input("Kitne Users Ka Data Upload Karna Hai?", min_value=1, max_value=30, value=2)

st.header("📋 User Profiles Panel")

# --- UI GENERATION LOOP ---
for i in range(int(num_users)):
    user_id = f"User_{i+1}"
    
    if user_id not in st.session_state["global_jobs"]:
        st.session_state["global_jobs"][user_id] = {
            "status": "Not Started", "current_index": 0, "total_records": 0,
            "success_count": 0, "last_error": "No error yet"
        }
    
    current_job = st.session_state["global_jobs"][user_id]
    
    with st.expander(f"👤 USER PROFILE #{i+1} - Configuration & Live Control", expanded=True):
        c1, c2, c3 = st.columns([2, 3, 3])
        with c1:
            u_file = st.file_uploader(f"Upload CSV File", type=["csv"], key=f"file_{user_id}")
        with c2:
            u_bearer = st.text_input(f"Bearer Token", key=f"bearer_{user_id}")
        with c3:
            u_fcm = st.text_input(f"FCM Token", value="fm68XvPkTJW6tliWwPa7jS...", key=f"fcm_{user_id}")
            
        u_vaccine = st.selectbox(f"Kaunsi Vaccine Chalani Hai?", VACCINE_LIST, key=f"vac_{user_id}")
        
        # --- MONITORING & INDIVIDUAL RUN BUTTONS ---
        col_status, col_percent, col_actions = st.columns([2, 3, 3])
        
        with col_status:
            st.write(f"**Status:** {current_job['status']}")
            if current_job['status'] == "Error ❌":
                st.error(f"⚠️ {current_job['last_error']}")
                
        with col_percent:
            total = current_job["total_records"]
            done = current_job["current_index"]
            pct = int((done / total) * 100) if total > 0 else 0
            st.progress(pct / 100.0, text=f"Progress: {done}/{total} ({pct}%)")
            st.write(f"Kamyab Entries: **{current_job['success_count']}**")
            
        with col_actions:
            # INDIVIDUAL RUN BUTTON FOR EACH USER 
            if u_file and u_bearer and current_job["status"] in ["Not Started", "Completed 🎉"]:
                if st.button(f"🚀 Run User {i+1} Automation", key=f"run_btn_{user_id}", type="primary", use_container_width=True):
                    df_loaded = pd.read_csv(u_file)
                    current_job["total_records"] = len(df_loaded)
                    current_job["current_index"] = 0
                    current_job["success_count"] = 0
                    
                    t = threading.Thread(target=execution_worker, args=(user_id, df_loaded, u_bearer, u_fcm, u_vaccine, 0))
                    t.daemon = True
                    t.start()
                    st.rerun()

            # Resume Button (If stopped or hit error)
            if current_job["status"] in ["Error ❌", "Stopped 🛑"] and u_file:
                if st.button(f"🔄 Resume User {i+1}", key=f"resume_btn_{user_id}", use_container_width=True):
                    df_loaded = pd.read_csv(u_file)
                    current_job["total_records"] = len(df_loaded)
                    
                    t = threading.Thread(target=execution_worker, args=(user_id, df_loaded, u_bearer, u_fcm, u_vaccine, current_job["current_index"]))
                    t.daemon = True
                    t.start()
                    st.rerun()
                    
            # Stop Button
            if current_job["status"] == "Running ⏳":
                if st.button(f"🛑 Stop User {i+1}", key=f"stop_btn_{user_id}", type="secondary", use_container_width=True):
                    current_job["status"] = "Stopped 🛑"
                    st.rerun()

st.markdown("---")
if st.button("🔄 Refresh System Dashboard Status Manually", use_container_width=True):
    st.rerun()
