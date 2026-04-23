import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_knowledge():
    with open(os.path.join(BASE_DIR, "service_hive_meta.json")) as f:
        return json.load(f)


import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "service_hive_meta.json")

def retrieve_context(query):
    try:
        print(" QUERY:", query)
        print(" FILE PATH:", FILE_PATH)

        if not os.path.exists(FILE_PATH):
            print(" FILE NOT FOUND")
            return ""

        with open(FILE_PATH, "r") as f:
            data = json.load(f)

        print(" DATA:", data)

        pricing = data.get("pricing", {})
        basic = pricing.get("basic", {})
        pro = pricing.get("pro", {})

        query = (query or "").lower()

        if "pro" in query:
            print(" MATCH: PRO")
            return f"Pro Plan: {pro.get('price')} - {', '.join(pro.get('features', []))}"

        if "basic" in query:
            print(" MATCH: BASIC")
            return f"Basic Plan: {basic.get('price')} - {', '.join(basic.get('features', []))}"

        if any(word in query for word in ["price", "pricing", "cost", "plan"]):
            print(" MATCH: PRICING")
            return f"""
Basic Plan: {basic.get('price')} - {', '.join(basic.get('features', []))}
Pro Plan: {pro.get('price')} - {', '.join(pro.get('features', []))}
"""

        print(" NO MATCH")
        return ""

    except Exception as e:
        print(" ERROR:", e)
        return ""