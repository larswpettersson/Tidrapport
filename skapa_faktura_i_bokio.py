import os
import sys
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

# --- KONSTANTER ---
KOLUMN_BREDD = 30  # Ändra detta värde för att justera bredden på aktivitet-kolumnen
# -----------------

load_dotenv()

def get_week_dates(year, week):
    monday = datetime.strptime(f'{year}-W{week:02d}-1', "%G-W%V-%u")
    return [monday + timedelta(days=i) for i in range(7)]

def skapa_faktura_i_bokio(data_lista):
    if not data_lista:
        print("❌ Ingen data hittades i kalendern för denna period.", file=sys.stderr)
        return

    BOKIO_API_TOKEN = os.getenv("BOKIO_API_TOKEN")
    COMPANY_ID = os.getenv("COMPANY_ID")
    CUSTOMER_ID = os.getenv("CUSTOMER_ID")
    TIMPRIS = float(os.getenv("TIMPRIS", 1000)) 
    
    if not BOKIO_API_TOKEN or not COMPANY_ID or not CUSTOMER_ID:
        print("❌ FEL: Saknade uppgifter i .env-filen!", file=sys.stderr)
        return

    dag_projekt_summering = defaultdict(float)
    veckodata = defaultdict(lambda: defaultdict(lambda: [0.0]*7))
    
    # För filnamnet: Hitta period (yyyy-mm) och första aktivitet
    fil_period = "okand_period"
    fil_aktivitet = "okand_aktivitet"

    for rad in data_lista:
        p = rad.get('Ämne', '').strip()
        if p.lower() == 'friskvård': 
            continue
            
        tid = rad.get('Duration_decimal', 0)
        if tid <= 0:
            continue

        datum_str_raw = rad.get('Startdatum', rad.get('Start Date', rad.get('Datum', '')))
        datum_str = str(datum_str_raw).split(' ')[0] if datum_str_raw else "Okänt_datum"
        
        # Sätt prefix för filnamnet baserat på den första giltiga raden
        if fil_period == "okand_period" and datum_str != "Okänt_datum":
            fil_period = datum_str[:7] # Tar YYYY-MM
            fil_aktivitet = p.replace(" ", "_")
        
        ar, vecka, veckodag_index = (datetime.now().year, 1, 0)
        
        if datum_str != "Okänt_datum":
            try:
                d_obj = datetime.strptime(datum_str, '%Y-%m-%d')
                ar, vecka, veckodag = d_obj.isocalendar()
                veckodag_index = veckodag - 1
            except ValueError:
                datum_str = f"Formatfel: {datum_str}"

        nyckel = (datum_str, p)
        dag_projekt_summering[nyckel] += tid
        veckodata[(ar, vecka)][p][veckodag_index] += tid

    if not dag_projekt_summering:
        print("❌ Inga fakturerbara rader hittades.", file=sys.stderr)
        return

    # --- SKAPA RADER TILL BOKIO ---
    line_items = []
    for (datum, p), tid in sorted(dag_projekt_summering.items()):
        line_items.append({
            "description": f"{datum} {p}" if datum != "Okänt_datum" else p,
            "quantity": round(tid, 2),
            "unit": "h",
            "unitPrice": TIMPRIS,
            "taxRate": 25.0,
            "productType": 0,
            "itemType": 0
        })

    # --- BOKIO API ANROP ---
    idag = datetime.now()
    faktura_datum = idag.strftime('%Y-%m-%d')
    forfallo_datum = (idag + timedelta(days=30)).strftime('%Y-%m-%d')

    payload = {
        "customerId": CUSTOMER_ID,
        "invoiceDate": faktura_datum,
        "dueDate": forfallo_datum,
        "currency": "SEK",
        "lineItems": line_items,
        "footerText": "Tack för förtroendet! Bifogar detaljerad tidrapport."
    }

    url = f"https://api.bokio.se/v1/companies/{COMPANY_ID}/invoices"
    headers = {"Authorization": f"Bearer {BOKIO_API_TOKEN}", "Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            print(f"✅ Fakturautkast skapat i Bokio med {len(line_items)} separata rader!")
        else:
            print(f"❌ API-Fel (HTTP {response.status_code}):", file=sys.stderr)
    except Exception as e:
        print(f"❌ Nätverksfel: {e}", file=sys.stderr)

    # --- SKAPA TEXTFILEN MED NYTT NAMN OCH FORMAT ---
    timestamp = idag.strftime('%Y%m%d_%H%M')
    filnamn = f"Tidrapport_{fil_period}_{fil_aktivitet}_{timestamp}.txt"
    
    try:
        with open(filnamn, "w", encoding="utf-8") as f:
            f.write("Kopiera blocken nedan och klistra in direkt i Excel eller Agresso.\n\n")
            for (ar, vecka) in sorted(veckodata.keys()):
                f.write(f"--- VECKA {vecka} ({ar}) ---\n")
                
                dates = get_week_dates(ar, vecka)
                date_headers = "\t".join([f"{d.day}/{d.month}" for d in dates])
                
                # Använder KOLUMN_BREDD och trunkerar vid behov
                header_text = "Aktivitet"[:KOLUMN_BREDD].ljust(KOLUMN_BREDD)
                f.write(f"{header_text}\t{date_headers}\tTotalt\n")
                
                for p, dagar in sorted(veckodata[(ar, vecka)].items()):
                    rad_tot = sum(dagar)
                    dagar_str = "\t".join([str(round(d, 2)) if d > 0 else "0" for d in dagar])
                    
                    # Trunkera aktivitet om den är för lång, annars fyll ut till KOLUMN_BREDD
                    p_formaterad = p[:KOLUMN_BREDD].ljust(KOLUMN_BREDD)
                    f.write(f"{p_formaterad}\t{dagar_str}\t{round(rad_tot, 2)}\n")
                f.write("\n")
        print(f"✅ Tidrapport för systemexport skapad: {filnamn}")
    except Exception as e:
        print(f"❌ Kunde inte spara textfilen: {e}", file=sys.stderr)

if __name__ == "__main__":
    input_text = sys.stdin.read()
    if input_text:
        try:
            skapa_faktura_i_bokio(json.loads(input_text))
        except:
            print("❌ Kunde inte läsa JSON.", file=sys.stderr)
