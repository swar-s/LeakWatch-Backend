import requests
import time
from flask import current_app
from app.utils.helpers import validate_email


# HIBP
def query_hibp(email):
    if not validate_email(email):
        return {"error": "Invalid email format"}, 400

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
    headers = {
        "hibp-api-key": current_app.config['HIBP_API_KEY'],
        "user-agent": "leakwatch-app"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return {"breaches": response.json()}, 200
    elif response.status_code == 404:
        return {"breaches": []}, 200  # No breaches found
    else:
        return {"error": f"HIBP error: {response.status_code}"}, response.status_code


# Dehashed
def query_dehashed(email):
    if not validate_email(email):
        return {"error": "Invalid email format"}, 400

    url = "https://api.dehashed.com/v2/search"
    headers = {
        "Content-Type": "application/json",
        "DeHashed-Api-Key": current_app.config["DEHASHED_API_KEY"]
    }
    payload = {
        "query": email,
        "page": 1,
        "size": 10,
        "regex": False,
        "wildcard": False,
        "de_dupe": True
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return {"results": response.json().get("entries", [])}
        elif response.status_code == 404:
            return {"results": []}
        else:
            return {"error": f"DeHashed error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"DeHashed request failed: {str(e)}"}


# IntelX
def query_intelx(email):
    if not validate_email(email):
        return {"error": "Invalid email"}

    headers = {
        "x-key": current_app.config["INTELX_API_KEY"],
        "User-Agent": "leakwatch-app",
        "Content-Type": "application/json"
    }

    search_url = "https://free.intelx.io/intelligent/search"
    result_url = "https://free.intelx.io/intelligent/search/result"

    search_payload = {
        "term": email,
        "lookuplevel": 0,
        "maxresults": 10,
        "media": 0,
        "timeout": 0,
        "buckets": [],
        "sort": 2
    }

    try:
        # STEP 1: Start the search
        search_resp = requests.post(
            search_url, headers=headers, json=search_payload)
        if search_resp.status_code != 200:
            return {"error": f"IntelX search failed: {search_resp.status_code}"}

        search_id = search_resp.json().get("id")
        if not search_id:
            return {"error": "IntelX search ID not found"}

        # STEP 2: Poll results
        for attempt in range(5):  # Try 5 times max
            result_resp = requests.get(
                f"{result_url}?id={search_id}", headers=headers)
            if result_resp.status_code != 200:
                break

            result_data = result_resp.json()
            records = result_data.get("records", [])
            if records:
                return {"intelx": records}

            status = result_data.get("status")
            if status == 1:
                break  # Search completed, no results
            elif status == 3:
                time.sleep(0.5)  # Wait and retry

        return {"intelx": []}  # No data found or timed out

    except Exception as e:
        return {"error": f"IntelX request failed: {str(e)}"}
