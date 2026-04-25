import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def skapa_faktura_i_bokio(data_lista):
    if not data_lista:
        print("Ingen data att fakturera.", file=sys.stderr)
        return

    # --- VARNINGSLOGIK FÖR STAVNING ---
    unika_projekt = set([rad['Ämne'].strip() for rad in data_lista])
    lowercase_grupper = {}
    for proj in unika_projekt:
        proj_lower = proj.lower()
        if proj_lower not in lowercase_grupper: lowercase_grupper[proj_lower] = []
        lowercase_grupper[proj_lower].append(proj)
        
    for proj_lower, varianter in lowercase_grupper.items():
        if len(varianter) > 1:
            print(f"⚠️ VARNING: Flera varianter av '{proj_lower}': {varianter}", file=sys.stderr)

    # --- SUMMERING OCH API ---
    BOKIO_API_TOKEN = os.getenv("BOKIO_API_TOKEN")
    COMPANY_ID = os.getenv("COMPANY_ID")
    CUSTOMER_ID = os.getenv("CUSTOMER_ID")
    TIMPRIS = int(os.getenv("TIMPRIS", 1200))

    projekt_summering = {}
    for rad in data_lista:
        p = rad['Ämne'].strip()
        if p.lower() == 'friskvård': continue
        projekt_summering[p] = projekt_summering.get(p, 0) + rad['Duration_decimal']

    line_items = []
    for p, tid in projekt_summering.items():
        line_items.append({
            "description": f"Konsulttjänster: {p}",
            "quantity": round(tid, 2),
            "unit": "h",
            "price": TIMPRIS,
            "taxRate": 25
        })

    payload = {
        "customerId": CUSTOMER_ID,
        "invoiceDate": datetime.now().strftime('%Y-%m-%d'),
        "deliveryTerms": "Enligt ök.",
        "rows": line_items,
        "footerText": "Tack för förtroendet! Innehar F-skattsedel."
    }

    url = f"https://api.bokio.se/v1/companies/{COMPANY_ID}/invoices"
    headers = {"Authorization": f"Bearer {BOKIO_API_TOKEN}", "Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        print(f"✅ Fakturautkast skapat i Bokio!")
    else:
        print(f"❌ Fel: {response.text}", file=sys.stderr)

if __name__ == "__main__":
    input_text = sys.stdin.read()
    if input_text:
        skapa_faktura_i_bokio(json.loads(input_text))
