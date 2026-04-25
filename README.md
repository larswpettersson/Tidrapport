# Tidrapport -> Bokio fakturautkast

Detta projekt tar tid från en ICS-kalender, filtrerar på period och valfritt kundprefix, och skapar ett fakturautkast i Bokio.

## Filer

- `fakturera_kund.sh` - kör hela flödet.
- `ics2tidrapport.py` - hämtar kalenderdata och skickar JSON till nästa steg.
- `skapa_faktura_i_bokio.py` - läser JSON och skapar fakturautkast via Bokio API.
- `.env-example` - mall för miljövariabler.

## Krav

- Python 3
- `pip`
- Python-paket:
  - `requests`
  - `icalendar`
  - `python-dotenv`

Installera paket:

```bash
pip install requests icalendar python-dotenv
```

## Konfiguration

1. Skapa en lokal `.env` från mallen:

```bash
cp .env-example .env
```

2. Fyll i värden i `.env`:

- `KALENDER_URL` - publik eller delad ICS-länk till kalendern
- `BOKIO_API_TOKEN` - token för Bokio API
- `COMPANY_ID` - ditt företags-id i Bokio
- `CUSTOMER_ID` - kund-id i Bokio
- `TIMPRIS` - timpris per timme (standard 1200 om den saknas)

## Användning

Kör hela pipelinen:

```bash
./fakturera_kund.sh <yyyy-mm> [prefix]
```

Exempel:

```bash
./fakturera_kund.sh 2026-04
./fakturera_kund.sh 2026-04 AcmeCorp
```

- `yyyy-mm` är obligatorisk period, t.ex. `2026-04`
- `prefix` är valfritt och filtrerar på ämnesradens början, t.ex. `AcmeCorp`

## Manuell körning (felsökning)

Testa datasteg 1 separat:

```bash
python ics2tidrapport.py 2026-04 AcmeCorp
```

Testa hela pipen manuellt:

```bash
python ics2tidrapport.py 2026-04 AcmeCorp | python skapa_faktura_i_bokio.py
```

## Vanliga fel

- `Fel: Ingen KALENDER_URL hittades i .env`
  - Kontrollera att `.env` finns och att variabeln är ifylld.
- `Ingen data att fakturera.`
  - Ingen kalenderdata matchade period/prefix.
- `Fel vid API-anrop` eller `❌ Fel: ...`
  - Kontrollera Bokio-token, company/customer-id och API-behörighet.

## Säkerhet

- `.env` ska inte committas (ligger i `.gitignore`).
- Dela aldrig `BOKIO_API_TOKEN` publikt.
