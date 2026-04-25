#!/bin/bash

if [ "$#" -lt 1 ]; then
    echo "Användning: ./fakturera_kund.sh <yyyy-mm> [prefix]"
    echo "Exempel: ./fakturera_kund.sh 2026-04 AcmeCorp"
    exit 1
fi

YYYYMM=$1
PREFIX=$2

# Nu skickar vi bara vidare datum och prefix, Python sköter resten via .env
python ics2tidrapport.py "$YYYYMM" "$PREFIX" | python skapa_faktura_i_bokio.py
