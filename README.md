# 🏃 Marathon 4:35

App di tracciamento per la preparazione alla **Maratona di Torino — 19 Aprile 2026** con target passo **4:35–4:40 min/km**.

## Funzionalità

- **Dashboard** con countdown, statistiche e grafici
- **Tracciamento allenamenti** (manuale, Galaxy Watch CSV, Strava)
- **Dati biometrici** (FC, HRV, SpO2, sonno, passi)
- **Misurazioni corporee** (peso, composizione corporea, BMI)
- **Nutrizione** (macro, idratazione, integratori)
- **PWA** installabile su mobile
- **Sincronizzazione Strava** per importazione automatica corse

## Avvio rapido

```bash
pip install -r requirements.txt
python app.py
# Apri http://localhost:5000 — PIN default: pier2026
```

## Variabili d'ambiente

| Variabile | Descrizione | Default |
|---|---|---|
| `SECRET_KEY` | Chiave segreta Flask | Auto-generata |
| `APP_PIN` | PIN di accesso | `pier2026` |
| `PORT` | Porta del server | `5000` |
| `STRAVA_CLIENT_ID` | Client ID Strava API | — |
| `STRAVA_CLIENT_SECRET` | Client Secret Strava API | — |

## 🔄 Guida Configurazione Strava API

Per abilitare la sincronizzazione automatica degli allenamenti da Strava, segui questi passaggi:

### 1. Registra l'app su Strava

1. Vai su **[developers.strava.com](https://developers.strava.com)**
2. Effettua il login con il tuo account Strava
3. Vai su **[My API Application](https://www.strava.com/settings/api)**
4. Compila il modulo di creazione app:
   - **Application Name**: `Marathon 4:35` (o un nome a scelta)
   - **Category**: `Training`
   - **Club**: (lascia vuoto)
   - **Website**: l'URL della tua app (es. `https://tua-app.onrender.com`)
   - **Authorization Callback Domain**: il dominio della tua app senza protocollo (es. `tua-app.onrender.com`). Per sviluppo locale usa `localhost`
5. Clicca **Create** per ottenere il **Client ID** e il **Client Secret**

### 2. Configura le variabili d'ambiente

Imposta le seguenti variabili d'ambiente nel tuo ambiente di deploy (Render, Heroku, ecc.) o in un file `.env` locale:

```bash
export STRAVA_CLIENT_ID="il-tuo-client-id"
export STRAVA_CLIENT_SECRET="il-tuo-client-secret"
```

Su **Render**, aggiungi queste variabili nella sezione **Environment** del tuo servizio.

### 3. Collega il tuo account

1. Apri l'app e vai su **Impostazioni** (⚙️)
2. Clicca **Connetti con Strava**
3. Autorizza l'accesso nella pagina Strava
4. Vai nella pagina **Strava Sync** (🔄) e premi **Sincronizza Attività**

### Note importanti

- Strava importa **solo le attività di corsa** (tipo "Run")
- I dati importati: distanza, tempo, passo, FC media, FC max, cadenza, calorie
- Ogni attività viene importata **una sola volta** (deduplicazione automatica)
- Il passo viene confrontato automaticamente con il target 4:35–4:40 min/km
- Per i **dati biometrici avanzati** (composizione corporea, sonno, SpO2), continua a usare l'import CSV da Galaxy Watch

## Deploy su Render

1. Fai push del repository su GitHub
2. Collega il repository a [Render](https://render.com)
3. Imposta le variabili d'ambiente (`APP_PIN`, `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`)
4. Il deploy avviene automaticamente

## Licenza

Uso personale.
