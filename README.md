# 🌉 Emulated Hue Custom (Alexa Fix & Auto-Clean)

[![it](https://img.shields.io/badge/lang-it-green.svg)](https://github.com/SalvatoreITA/Emulated-Hue/blob/main/README_it.md)
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/SalvatoreITA/Emulated-Hue/blob/main/README.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-v1.0.0-blue.svg)]()
[![maintainer](https://img.shields.io/badge/maintainer-Salvatore_Lentini_--_DomHouse.it-green.svg)](https://www.domhouse.it)


## 📖 Descrizione

Versione personalizzata e ottimizzata dell'integrazione **Emulated Hue** per Home Assistant.

Nell'integrazione ufficiale di Home Assistant, tutti gli interruttori (`switch`), gli `input_boolean` e i dispositivi On/Off vengono forzati ed esposti ad Amazon Alexa come **Lampadine (`On/Off light`)**. Questo causa un grave problema: pronunciando *"Alexa, spegni le luci"* in una stanza, Alexa spegne anche TV, elettrodomestici, PC o caldaie associati a quella stanza.

Questa versione Custom risolve il problema alla radice, permettendo di decidere via YAML se esporre ogni singola entità come **Altro (`other`)** o come **Luce (`light`)**, aggiungendo inoltre il ricalcolo dinamico dell'ID univoco quando si cambia tipo e la pulizia automatica del database JSON.

## ✨ Caratteristiche Principali

1. **Scelta manuale tra Luce e Altro/ (`hue_type`)**:
   - `hue_type: "other" -> Espone l'entità come dispositivo generico (`On/Off plug-in unit` - Modello `LOM001`). Nell'App Alexa verrà classificato come tipo **Altro** e **non** verrà spento insieme alle luci della stanza quando si pronuncia *"Alexa, spegni le luci"*.
   - `hue_type: "light"` -> Espone l'entità come lampadina On/Off (`On/Off light` - Modello `HASS321`).
   - **Omettendo `hue_type`** -> L'integrazione mantiene il comportamento nativo (esponendo automaticamente funzioni di dimmerazione, temperatura colore e RGB per i domini `light.*` compatibili).

2. **Ricalcolo automatico del MAC Address al cambio tipo (`reset_id: true`)**:
   Quando si cambia il tipo a un dispositivo già conosciuto da Alexa (es. da `light` a `other`), gli Echo spesso ignorano la modifica perché mantengono in cache il vecchio indirizzo MAC virtuale (`uniqueid`). Inserendo `reset_id: true` nella configurazione dell'entità, l'`uniqueid` viene generato combinando il nome dell'entità e il suo modello (`entity_id` + `modelid`): in questo modo, ad ogni cambio di `hue_type` corrisponderà automaticamente un nuovo indirizzo MAC, forzando Alexa a rilevare subito la nuova categoria.

3. **Auto-Pulizia del file `.storage/emulated_hue.ids`**:
   A differenza del componente ufficiale che accumula all'infinito le vecchie entità nel file JSON, ad ogni avvio di Home Assistant (con `expose_by_default: false`) il componente confronta il database con il file YAML ed elimina automaticamente gli ID delle entità rimosse o impostate su `hidden: true`.

4. **Log di Home Assistant sempre puliti**:
   Le richieste residue degli Echo verso vecchi ID rimossi vengono gestite a livello `DEBUG` anziché `ERROR`, eliminando i fastidiosi errori rossi nel registro di sistema di Home Assistant.

## 📦 Installazione

### Opzione A — HACS (consigliata)

1. In HACS apri il menu **⋮ → Repository personalizzate**.
2. Incolla `https://github.com/SalvatoreITA/Emulated-Hue`, categoria **Integration**, poi **Aggiungi**.
3. Cerca **Emulated Hue Custom**, installalo e **riavvia** Home Assistant.

### Opzione B — Manuale

1. Copia la cartella `custom_components/emulated_hue/` dentro `config/custom_components/`.
2. Riavvia Home Assistant.

## ⚙️ Configurazione (YAML)

### Esempio di configurazione:

```
emulated_hue:
  host_ip: 192.168.1.100
  listen_port: 80
  expose_by_default: false
  entities:
    # Esposta come dispositivo non luminoso (Model ID: LOM001)
    switch.presa_ventilatore:
      name: "Ventilatore"
      hidden: false
      hue_type: "other"
      reset_id: true

     # Esposta come dispositivo non luminoso (Model ID: LOM001)
    input_boolean.modalita_cinema:
      name: "Modalità Cinema"
      hidden: false
      hue_type: "other"
      reset_id: true

    # Forzata come LUCE ON/OFF semplice senza dimmer (Model ID: HASS321)
    light.luce_specchio_bagno:
      name: "Luce Specchio"
      hidden: false
      hue_type: light
      reset_id: true

    # Comportamento standard (nessun hue_type specificato)
    light.lampada_salotto:
      name: "Lampada Salotto"
      hidden: false

```

### Valori supportati per `hue_type`:

| Valore | Tipo Hue Emulato | Model ID | Riconoscimento su Alexa | 
| ----- | ----- | ----- | ----- | 
| `other` | `On/Off plug-in unit` | `LOM001` | Riconosciuto come **"Altro"** (Dispositivo On/Off generico, escluso dal gruppo Luci). | 
| `light` | `On/Off light` | `HASS321` | Riconosciuto come **"Luce"** semplice On/Off (senza controllo luminosità/dimmer). | 
| *(non specificato)* | *Automatico* | *Vari* | Comportamento originale di Home Assistant basato sulle feature dell'entità. | 

## 🔄 Come aggiornare i dispositivi già presenti su Alexa

## ☕ Supporta il Progetto

Ogni piccolo supporto fa un'enorme differenza: mi aiuta a mantenere vivo l'entusiasmo e mi stimola a creare e condividere nuove soluzioni per la community. Grazie di cuore per il tuo aiuto! 🚀

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/salvatore_dh)

## ❤️ Crediti
Sviluppato da [Salvatore Lentini - DomHouse.it](https://www.domhouse.it)
