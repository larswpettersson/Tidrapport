# Google Apps Script backend

This folder contains an Apps Script version of the Python pipeline:

`./fakturera_kund.sh <yyyy-mm> [prefix]`

## What is implemented

- Fetch ICS calendar data
- Filter by `yyyy-mm` and optional `prefix`
- Build Bokio line items
- Create draft invoice in Bokio
- Return a text export block (Excel/Agresso style) in API response

## Deploy

1. Open [script.new](https://script.new)
2. Replace `Code.gs` with `Javascript/gscript/Code.gs`
3. Deploy as Web App:
   - Execute as: `Me`
   - Who has access: `Anyone` (demo)
4. Copy `/exec` URL and use it as `Bokio API base` in the web demo.

## Request payload

`POST` (text/plain JSON):

```json
{
  "action": "runPipeline",
  "token": "BOKIO_API_TOKEN",
  "yearMonth": "2026-04",
  "prefix": "ACME",
  "companyId": "b8d2bd5b-...",
  "customerId": "b28b5273-...",
  "calendarUrl": "https://.../basic.ics"
}
```

`calendarUrl` is optional if you configure Script Property `KALENDER_URL`.
