"""
طراحی اسکیماهای استخراج داده منطبق بر الزامات ممیزی ISO 14001 و سیستم مدیریت زیست‌محیطی (SGA).
"""

AVAILABLE_SCHEMAS = {
    "scadenziario": {
        "description": "Scadenziario adempimenti, prescrizioni normative, autorizzazioni ambientali e visite mediche.",
        "fields": {
            "tema": "string (es. Gestione Rifiuti, Emissioni, Scarichi, PPGA, Salute e Sicurezza, Formazione)",
            "adempimento": "string (Descrizione sintetica e chiara dell'obbligo o della prescrizione)",
            "scadenza": "date (Data entro cui completare l'adempimento in formato YYYY-MM-DD)",
            "preavviso": "string (Tempo di preavviso necessario: es. 30 giorni, 6 mesi)",
            "responsabile": "string (Figura o ente responsabile dell'attuazione)",
            "stato": "string (Pianificato, In corso, Concluso, Da verificare)",
            "evidenza_note": "string (Documento di evidenza, verbale, protocollo o note operative)",
            "allerta": "string (Livello di priorità o allerta: Bassa, Media, Alta, Critica)"
        },
        "required": ["adempimento", "scadenza"]
    },

    "vehicle_fuel": {
        "description": "Monitoraggio parco veicoli, consumi carburante (L/100km) e scadenze revisioni periodiche.",
        "fields": {
            "targa": "string (Targa del veicolo normalizzata es. AA123BB)",
            "modello": "string (Marca e modello del veicolo)",
            "scadenza_revisione": "date (Data scadenza revisione periodica in formato YYYY-MM-DD)",
            "periodo": "string (Mese o intervallo di riferimento del consumo: es. Gennaio 2026)",
            "litri": "number (Litri totali di carburante consumati)",
            "chilometri": "number (Chilometri percorsi nel periodo)",
            "consumo_l_100km": "number (Consumo calcolato: litri / km * 100)"
        },
        "required": ["targa"]
    },

    "utility_consumption": {
        "description": "Monitoraggio consumi utenze (Energia elettrica eVISO, Acqua ACDA, Gas, Combustibili).",
        "fields": {
            "tipo_utenza": "string (Elettricità, Acqua Industriale/Civile, Gas Naturale, Gasolio)",
            "fornitore": "string (Ragione sociale fornitore: es. eVISO, ACDA, Enel)",
            "codice_pod_pdr": "string (Identificativo fornitura POD, PDR o Matricola contatore)",
            "periodo_riferimento": "string (Mese/Anno o intervallo temporale fatturato)",
            "consumo_totale": "number (Quantitativo totale fatturato)",
            "unita_misura": "string (kWh, m3, Smc, Litri)",
            "ripartizione_fasce": "string (Ripartizione F1, F2, F3 o dettagli scaglioni se presenti)",
            "totale_spesa_eur": "number (Importo totale documento in Euro)"
        },
        "required": ["tipo_utenza", "consumo_totale", "periodo_riferimento"]
    },

    "personnel_training": {
        "description": "Registro formazione obbligatoria del personale, abilitazioni attrezzature e D.Lgs 81/08.",
        "fields": {
            "nominativo_dipendente": "string (Nome e cognome lavoratore o corsista)",
            "codice_fiscale": "string (Codice Fiscale lavoratore es. FRSRMS90M03I470K)",
            "corso_descrizione": "string (Titolo corso o abilitazione: es. Carrelli Elevatori, Antincendio, RLS)",
            "riferimento_normativo": "string (Riferimento normativo o articolo di legge: es. Artt. 71 e 73 D.Lgs. 81/08)",
            "numero_protocollo": "string (Numero protocollo o identificativo attestato es. EB00F763/2026/0655)",
            "ente_formatore": "string (Soggetto formatore accreditato, CFPT o docente: es. Conflavoro PMI, 3R International)",
            "data_emissione": "date (Data attestato o superamento corso in formato YYYY-MM-DD)",
            "data_scadenza_rinnovo": "date (Data scadenza validità o termine aggiornamento obbligatorio)",
            "frequenza_anni": "number (Frequenza di aggiornamento in anni: es. 1, 2, 5)",
            "ore_formazione": "number (Durata complessiva del corso in ore)",
            "stato_validita": "string (Valido, In scadenza, Scaduto, Da verificare)"
        },
        "required": ["nominativo_dipendente", "corso_descrizione", "data_emissione"]
    },

    "regulatory_authorization": {
        "description": "Registro autorizzazioni ambientali, titoli abilitativi provinciali, iscrizioni Albo Gestori e codici EER/CER.",
        "fields": {
            "numero_atto_protocollo": "string (Numero identificativo autorizzazione, registro o protocollo)",
            "numero_iscrizione": "string (Numero di iscrizione Albo es. TO15878 o identificativo registro)",
            "ente_rilascio": "string (Provincia, Regione, Sezione Albo Gestori, ARPA)",
            "data_rilascio": "date (Data emanazione provvedimento in formato YYYY-MM-DD)",
            "data_scadenza": "date (Termine di validità dell'atto autorizzativo, se specificato)",
            "attivita_autorizzate": "string (Operazioni e categorie autorizzate: es. Categoria 4-E, Messa in riserva R13, Recupero R4)",
            "mezzi_autorizzati": "string (Targhe, tipologia mezzi e numeri telaio autorizzati o integrati: es. DB153EX, XA078VK)",
            "elenco_codici_eer": "string (Codici EER / CER trattabili o trasportabili)",
            "responsabili_tecnici_note": "string (Responsabili tecnici: nomine, conferme o cessazioni di incarico)",
            "prescrizioni_rilevanti": "string (Prescrizioni condizionanti, collaudi, garanzie finanziarie o condizioni di ricorso)"
        },
        "required": ["numero_atto_protocollo", "ente_rilascio"]
    },

    "general": {
        "description": "Estrazione generale per contratti, comunicazioni istituzionali e documentazione varia.",
        "fields": {
            "titolo_documento": "string (Titolo o oggetto principale)",
            "ente_emittente": "string (Azienda o ente che emette il documento)",
            "numero_protocollo": "string (Numero protocollo o identificativo)",
            "data_emissione": "date (Data emissione in formato YYYY-MM-DD)",
            "data_scadenza": "date (Data eventuale di scadenza o efficacia)",
            "oggetto_sintesi": "string (Sintesi del contenuto rilevante)"
        },
        "required": ["titolo_documento"]
    }
}