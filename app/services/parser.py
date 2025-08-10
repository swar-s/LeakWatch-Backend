def parse_hibp_response(response):
    breaches = response.get("breaches", [])
    parsed = []

    for item in breaches:
        parsed.append({
            "source": "HaveIBeenPwned",
            "name": item.get("Name"),
            "domain": item.get("Domain"),
            "breach_date": item.get("BreachDate"),
            "exposed_data": item.get("DataClasses", []),
            "description": item.get("Description")
        })
    return parsed


def parse_dehashed_response(response):
    entries = response.get("results", [])
    parsed = []

    for entry in entries:
        parsed.append({
            "source": "DeHashed",
            "email": entry.get("email"),
            "username": entry.get("username"),
            "ip_address": entry.get("ip_address"),
            "password": entry.get("password"),
            "hashed_password": entry.get("hashed_password"),
            "phone": entry.get("phone"),
            "address": entry.get("address"),
            "name": entry.get("name")
        })
    return parsed


def parse_intelx_response(response):
    results = response if isinstance(response, list) else []
    parsed = []
    for result in results:
        parsed.append({
            "source": "IntelX",
            "name": result.get("name"),
            "added": result.get("added"),
            "bucket": result.get("bucket"),
            "media": result.get("media"),
            "size": result.get("size")
        })
    return parsed
