import streamlit as st
import pandas as pd
import requests
import time
import random

# Page Configuration
st.set_page_config(page_title="9211 Stable Dashboard", page_icon="🚜", layout="wide")

st.title("🚜 9211 Portal Multi-User Non-Stop Data Sender")
st.write("Is version mein page baar-baar refresh nahi hoga. Data sukoon se row-by-row upload hoga.")

# --- INITIALIZE PERSISTENT STORAGE ---
if "user_files" not in st.session_state:
    st.session_state["user_files"] = {}

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

# --- CORE SENDING FUNCTION ---
def send_row(row, bearer_token, fcm_token, vaccine_option, df_columns):
    API_URL = 'https://spms9211api.punjab.gov.pk/api/Vaccination/Add'
    headers = {
        'Authorization': f"Bearer {bearer_token.strip()}",
        'fcmtoken': fcm_token.strip(),
        'HashKey': 'gwKpvUg6skx96JHp4sRvt/bGkRw=',
        'X-API-KEY': 'A06B691B-8D21-42BB-9E39-9AF570F71105-9211@AP!',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'spms9211api.punjab.gov.pk',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp/4.5.0'
    }

    csv_animal_code = str(row['animalCode']).upper().strip() if 'animalCode' in df_columns else 'C'
    
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
        return r.status_code, r.text
    except Exception as e:
        return 999, str(e)

# --- SIDEBAR CONTROL ---
num_users = st.sidebar.number_input("Kitne Users Ka Data Upload Karna Hai?", min_value=1, max_value=30, value=3)

# --- UI GENERATION LOOP ---
for i in range(int(num_users)):
    user_id = f"User_{i+1}"
    
    with st.expander(f"👤 USER PROFILE #{i+1} - Panel Manager", expanded=True):
        c1, c2, c3 = st.columns([2, 3, 3])
        with c1:
            u_file = st.file_uploader(f"Upload CSV File", type=["csv"], key=f"file_{user_id}")
            if u_file is not None:
                st.session_state["user_files"][user_id] = pd.read_csv(u_file)
        with c2:
            u_bearer = st.text_input(f"Bearer Token", key=f"bearer_{user_id}")
        with c3:
            u_fcm = st.text_input(f"FCM Token", value="fm68XvPkTJW6tliWwPa7jS...", key=f"fcm_{user_id}")
            
        u_vaccine = st.selectbox(f"Kaunsi Vaccine Chalani Hai?", VACCINE_LIST, key=f"vac_{user_id}")
        
        has_data = user_id in st.session_state["user_files"]
        
        # Live UI Containers placeholders
        status_box = st.empty()
        progress_box = st.empty()
        log_box = st.empty()
        
        # Initial View Setup
        status_box.markdown("**Status:** Idle ⚪")
        progress_box.progress(0.0, text="Progress: 0%")
        log_box.text_area("Live Logs:", value="Awaiting Execution...", height=100, key=f"init_log_{user_id}", disabled=True)
        
        if has_data and u_bearer:
            if st.button(f"🚀 Run User {i+1} Live", key=f"run_btn_{user_id}", type="primary", use_container_width=True):
                df = st.session_state["user_files"][user_id]
                total_records = len(df)
                
                status_box.markdown("**Status:** Processing... ⚡")
                local_logs = ["Starting upload script..."]
                log_box.text_area("Live Logs:", value="\n".join(local_logs), height=100, key=f"run_log_{user_id}", disabled=True)
                
                success_count = 0
                failed_count = 0
                
                for idx, row in df.iterrows():
                    status_code, response_text = send_row(row, u_bearer, u_fcm, u_vaccine, df.columns)
                    
                    if status_code in [200, 201]:
                        success_count += 1
                        log_msg = f"🟢 Row {idx+1} [Farmer: {row.get('FarmerID','N/A')}]: 200 - OK"
                    else:
                        failed_count += 1
                        log_msg = f"❌ Row {idx+1} Failed: {status_code} - {response_text[:60]}"
                        
                    local_logs.append(log_msg)
                    
                    # Update placeholders WITHOUT st.rerun()
                    status_box.markdown(f"**Status:** Processing... ⚡ | Kamyab: **{success_count}** | Failed: **{failed_count}**")
                    pct = int(((idx + 1) / total_records) * 100)
                    progress_box.progress((idx + 1) / total_records, text=f"Progress: {idx+1}/{total_records} ({pct}%)")
                    log_box.text_area("Live Logs:", value="\n".join(local_logs[-5:]), height=100, key=f"loop_log_{user_id}_{idx}", disabled=True)
                    
                    if status_code == 401:
                        status_box.error("❌ Session Expired (401)! Naya Token lagayein.")
                        break
                        
                    # Delay 40-100 seconds
                    time.sleep(random.randint(40, 100))
                    
                if failed_count == 0:
                    status_box.success("🎉 Completed Successfully!")
