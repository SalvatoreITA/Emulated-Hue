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

### Fase 1: Pulizia totale dei dispositivi su Alexa
Prima di toccare Home Assistant, è fondamentale rimuovere qualsiasi residuo dal Cloud di Amazon.

1. Apri l'**App Alexa** sul tuo smartphone.
2. Vai su **Dispositivi** e seleziona la lista completa.
3. Entra uno ad uno nei dispositivi collegati tramite Emulated Hue e **rimuovili/cestinziali** tutti.
4. Esci dall'app o chiudila completamente per evitare che mantenga dati in cache.
5. Togli alimentazione a tutti i tuoi dispositivi Alexa e dopo un paio di minuti accendine solo uno che farà da Hub Master

### Fase 2: Pulizia dei file di storage su Home Assistant
Il componente Emulated Hue memorizza gli ID univoci generati in un file di storage locale. Per evitare conflitti con i vecchi MAC address, bisogna eliminarlo.

1. Accedi a Home Assistant tramite File Editor o SSH.
2. Posizionati nella cartella nascosta `.storage/`.
3. Individua e cancella il file:
   ```text
   .storage/emulated_hue.ids
   ```
   *(Nota: Se non trovi il file, salta pure questo passaggio, verrà rigenerato automaticamente al primo avvio).*

### Fase 3: Applicazione del file YAML definitivo
Nel tuo file di configurazione principale (`configuration.yaml`), struttura le entità assegnando a ognuna il proprio tipo e la proprietà di reset dell'ID:

```yaml
emulated_hue:
  host_ip: 192.168.1.246
  listen_port: 80
  expose_by_default: false
  entities:
    # Esempio per una luce
    switch.luce_cucina:
      name: "Luce Cucina"
      hidden: false
      hue_type: "light"
      reset_id: true

    # Esempio per una presa o elettrodomestico
    switch.forno:
      name: "Forno"
      hidden: false
      hue_type: "other"
      reset_id: true
```

* **`hue_type: "light"`**: Forza l'apparato a essere visto da Alexa come una lampadina (`modelid: HASS321`).
* **`hue_type: "other"`**: Forza l'apparato a essere visto da Alexa come una presa/interruttore generico (`modelid: LOM001`), isolandolo dai gruppi di illuminazione.
* **`reset_id: true`**: Permette al sistema di ricalcolare l'ID univoco in caso di modifiche future, evitando sdoppiamenti o blocchi di cache.

---

### Fase 4: Riavvio e Nuova Scansione
1. Salva il file YAML e **riavvia interamente Home Assistant**.
2. Verifica che il bridge risponda correttamente aprendo nel browser l'indirizzo:
   `http://<IP_DI_HOME_ASSISTANT>/api/nouser/lights` (dovresti vedere l'elenco in formato JSON di tutte le entità configurate).
3. Prendi l'Echo principale (es. *Alexa Sala*) e procedi alla ricerca:
   * **Tramite voce:** Pronuncia *"Alexa, scopri dispositivi"*.
   * **Tramite app:** Vai su App Alexa -> Dispositivi -> Aggiungi dispositivo -> Altro / Philips Hue -> Ricerca dispositivi.
4. Attendi il completamento della scansione.

### Fase 5: Ripristino finale
1. Una volta completata con successo la scoperta dei dispositivi puliti, puoi **riaccendere gli altri Echo** della casa
2. Esegui un test rapido accendendo/spegnendo un paio di entità (sia di tipo luce che di tipo other) per confermare la piena operatività.

## ☕ Supporta il Progetto

Ogni piccolo supporto fa un'enorme differenza: mi aiuta a mantenere vivo l'entusiasmo e mi stimola a creare e condividere nuove soluzioni per la community. Grazie di cuore per il tuo aiuto! 🚀

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/salvatore_dh)

## ❤️ Crediti
Sviluppato da [Salvatore Lentini - DomHouse.it](https://www.domhouse.it)
