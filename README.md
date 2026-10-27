# 🌉 Emulated Hue Custom (Alexa Fix & Auto-Clean)

Versione personalizzata e ottimizzata dell'integrazione **Emulated Hue** per Home Assistant.

Nell'integrazione ufficiale di Home Assistant, tutti gli interruttori (`switch`), gli `input_boolean` e i dispositivi On/Off vengono forzati ed esposti ad Amazon Alexa come **Lampadine (`On/Off light`)**. Questo causa un grave problema: pronunciando *"Alexa, spegni le luci"* in una stanza, Alexa spegne anche TV, elettrodomestici, PC o caldaie associati a quella stanza.

Questa versione Custom risolve il problema alla radice, permettendo di decidere via YAML se esporre ogni singola entità come **Altro (`other`)** o come **Luce (`light`)**, aggiungendo inoltre il ricalcolo dinamico dell'ID univoco quando si cambia tipo e la pulizia automatica del database JSON.

---

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

---

## 🛠️ Installazione

