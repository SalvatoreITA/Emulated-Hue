# 🌉 Emulated Hue Custom (Alexa Fix & Auto-Clean)

[![it](https://img.shields.io/badge/lang-it-green.svg)](https://github.com/SalvatoreITA/Emulated-Hue/blob/main/README_it.md)
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/SalvatoreITA/Emulated-Hue/blob/main/README.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-v1.1.0-blue.svg)]()
[![maintainer](https://img.shields.io/badge/maintainer-Salvatore_Lentini_--_DomHouse.it-green.svg)](https://www.domhouse.it)


## 📖 Descrizione

Versione personalizzata e ottimizzata dell'integrazione **Emulated Hue** per Home Assistant.

Nell'integrazione ufficiale di Home Assistant, tutti gli interruttori (`switch`), gli `input_boolean` e i dispositivi On/Off vengono forzati ed esposti ad Amazon Alexa come **Lampadine (`On/Off light`)**. Questo causa un grave problema: pronunciando *"Alexa, spegni le luci"* in una stanza, Alexa spegne anche TV, elettrodomestici, PC o caldaie associati a quella stanza.

Questa versione Custom risolve il problema alla radice, permettendo di decidere via YAML se esporre ogni singola entità come **Altro (`other`)** o come **Luce (`light`)**. In più aggiunge ID univoci stabili, la pulizia automatica del database degli ID e la possibilità di legare tutti i dispositivi a un solo **Echo master**, anche in case con più Echo.

## ✨ Caratteristiche Principali

1. **Scelta manuale tra Luce e Altro (`hue_type`)**:
   - `hue_type: "other"` -> Espone l'entità come dispositivo generico (`On/Off plug-in unit` - Modello `LOM001`). Nell'App Alexa verrà classificato come tipo **Altro** e **non** verrà spento insieme alle luci della stanza quando si pronuncia *"Alexa, spegni le luci"*.
   - `hue_type: "light"` -> Espone l'entità come lampadina On/Off (`On/Off light` - Modello `HASS321`).
   - **Omettendo `hue_type`** -> L'integrazione mantiene il comportamento nativo (esponendo automaticamente funzioni di dimmerazione, temperatura colore e RGB per i domini `light.*` compatibili).

2. **Nuovo ID al cambio tipo (`reset_id: true`)**:
   Quando si cambia il tipo a un dispositivo già conosciuto da Alexa (es. da `light` a `other`), gli Echo spesso ignorano la modifica perché mantengono in cache il vecchio indirizzo MAC virtuale (`uniqueid`). Con `reset_id: true`:
   - **insieme a `hue_type`** -> l'`uniqueid` viene generato da `entity_id` + modello (`modelid`): ogni cambio di `hue_type` produce automaticamente un nuovo ID e Alexa rileva subito la nuova categoria;
   - **senza `hue_type`** -> l'entità riceve un nuovo ID fisso, utile per forzare Alexa a ri-scoprire un dispositivo "incastrato".

3. **ID univoci stabili, niente doppioni**:
   L'`uniqueid` non dipende mai dallo stato dell'entità. Quando una luce dimmerabile/RGB va `unavailable` perde le sue funzioni e viene vista temporaneamente come On/Off: se l'ID dipendesse dal tipo, cambierebbe e Alexa la vedrebbe come un dispositivo nuovo, creando doppioni. Qui l'ID resta sempre lo stesso.

4. **Numeri dei dispositivi mai riutilizzati**:
   Ogni entità esposta riceve un numero progressivo, che è quello con cui Alexa la comanda. Il componente salva il numero più alto mai assegnato, così un numero liberato dalla pulizia automatica (entità rimossa) **non viene mai riassegnato** a un'entità nuova. Altrimenti la nuova entità erediterebbe il numero della vecchia, che Alexa ha ancora in memoria, e un comando o una routine pensati per il vecchio dispositivo azionerebbero quello nuovo.

5. **Echo master unico (`upnp_allowed_ips`)**:
   Gli Echo cercano dispositivi in rete (SSDP) di continuo: all'avvio, a intervalli e a ogni ricerca lanciata da un altro Echo. Con l'Hue locale, Alexa lega i dispositivi **all'Echo che li ha trovati**, quindi in una casa con più Echo i dispositivi finiscono sparsi o duplicati ogni volta che un Echo si riavvia. Con `upnp_allowed_ips` il bridge risponde alla ricerca **solo** agli IP indicati: tutti i dispositivi restano sempre legati al tuo Echo master. I comandi vocali dati agli altri Echo continuano a funzionare normalmente.

6. **Auto-Pulizia del file `.storage/emulated_hue.ids`**:
   A differenza del componente ufficiale che accumula all'infinito le vecchie entità nel file JSON, ad ogni avvio di Home Assistant (con `expose_by_default: false`) il componente confronta il database con il file YAML ed elimina automaticamente gli ID delle entità rimosse o impostate su `hidden: true`.

7. **Log di Home Assistant sempre puliti**:
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

```yaml
emulated_hue:
  host_ip: 192.168.1.100
  listen_port: 80
  expose_by_default: false
  upnp_allowed_ips:          # opzionale: solo l'Echo master vede il bridge
    - 192.168.1.50
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
      hue_type: "light"
      reset_id: true

    # Comportamento standard (nessun hue_type specificato)
    light.lampada_salotto:
      name: "Lampada Salotto"
      hidden: false
```

### Opzioni generali

| Opzione | Default | Descrizione |
| ----- | ----- | ----- |
| `host_ip` | IP di HA | IP su cui il bridge è in ascolto e che viene comunicato agli Echo. |
| `listen_port` | `8300` | Porta del bridge. Per Alexa usa **`80`**. |
| `expose_by_default` | `true` | Con `false` vengono esposte solo le entità elencate in `entities` (consigliato; attiva anche l'auto-pulizia). |
| `upnp_allowed_ips` | *(vuoto)* | Lista di IP a cui il bridge risponde durante la ricerca dispositivi. Se vuota o assente, risponde a tutti (comportamento originale). |

### Opzioni per entità

| Opzione | Descrizione |
| ----- | ----- |
| `name` | Nome con cui l'entità compare in Alexa. |
| `hidden` | Con `true` l'entità non viene esposta (e il suo ID viene rimosso all'avvio). |
| `hue_type` | `"other"` o `"light"` (vedi tabella sotto). |
| `reset_id` | Con `true` genera un nuovo ID univoco (vedi *Caratteristiche*, punto 2). |

### Valori supportati per `hue_type`:

| Valore | Tipo Hue Emulato | Model ID | Riconoscimento su Alexa |
| ----- | ----- | ----- | ----- |
| `other` | `On/Off plug-in unit` | `LOM001` | Riconosciuto come **"Altro"** (Dispositivo On/Off generico, escluso dal gruppo Luci). |
| `light` | `On/Off light` | `HASS321` | Riconosciuto come **"Luce"** semplice On/Off (senza controllo luminosità/dimmer). |
| *(non specificato)* | *Automatico* | *Vari* | Comportamento originale di Home Assistant basato sulle feature dell'entità. |

### Echo master (`upnp_allowed_ips`)

1. Scegli l'Echo che farà da master: meglio uno **sempre acceso** e collegato bene alla rete.
2. Assegnagli un **IP riservato** nel DHCP del router. Se l'IP cambia, il bridge non risponde più a nessuno.
3. Inserisci l'IP in `upnp_allowed_ips` e riavvia Home Assistant.

> ⚠️ Il master deve trovarsi nella **stessa rete/subnet** di Home Assistant: la ricerca SSDP (multicast) non attraversa le VLAN.
>
> ℹ️ Se il master è spento, i dispositivi non rispondono ai comandi finché non torna online: nessun altro Echo può prenderne il posto. È il prezzo di avere un master fisso.

## 🔄 Come aggiornare i dispositivi già presenti su Alexa

### Fase 1: Pulizia totale dei dispositivi su Alexa
Prima di toccare Home Assistant, è fondamentale rimuovere qualsiasi residuo dal Cloud di Amazon.

1. Apri l'**App Alexa** sul tuo smartphone.
2. Vai su **Dispositivi** e seleziona la lista completa.
3. Entra uno ad uno nei dispositivi collegati tramite Emulated Hue e **rimuovili** tutti.
4. Esci dall'app o chiudila completamente per evitare che mantenga dati in cache.
5. **Se usi `upnp_allowed_ips`** puoi lasciare tutti gli Echo accesi: risponderà solo il master.
   **Se non lo usi**, togli alimentazione a tutti i tuoi dispositivi Alexa e dopo un paio di minuti accendine solo uno, che farà da Hub Master.

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
  upnp_allowed_ips:
    - 192.168.1.50   # IP dell'Echo master
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
* **`reset_id: true`**: Genera un nuovo ID univoco: insieme a `hue_type` l'ID cambia automaticamente a ogni cambio di tipo, evitando sdoppiamenti o blocchi di cache.

---

### Fase 4: Riavvio e Nuova Scansione
1. Salva il file YAML e **riavvia interamente Home Assistant** (un semplice "Ricarica YAML" non basta: emulated_hue legge la configurazione solo all'avvio).
2. Verifica che il bridge risponda correttamente aprendo nel browser l'indirizzo:
   `http://<IP_DI_HOME_ASSISTANT>/api/nouser/lights` (dovresti vedere l'elenco in formato JSON di tutte le entità configurate).
3. Avvia la ricerca dei dispositivi:
   * **Tramite voce:** Pronuncia *"Alexa, scopri dispositivi"* all'Echo master.
   * **Tramite app:** Vai su App Alexa -> Dispositivi -> Aggiungi dispositivo -> Altro / Philips Hue -> Ricerca dispositivi. Anche dall'app la ricerca viene fatta dagli Echo di casa, quindi con `upnp_allowed_ips` risponde comunque solo il master.
4. Attendi il completamento della scansione.

### Fase 5: Ripristino finale
1. Se avevi spento gli altri Echo, una volta completata con successo la scoperta dei dispositivi puoi **riaccenderli**.
2. Esegui un test rapido accendendo/spegnendo un paio di entità (sia di tipo luce che di tipo other) per confermare la piena operatività.

## 🔁 Passaggio dall'integrazione ufficiale

- **File degli ID**: se arrivi dall'Emulated Hue ufficiale, il file `.storage/emulated_hue.ids` viene convertito automaticamente nel formato di questo componente al primo avvio. Le associazioni numero ↔ entità restano identiche. Se preferisci ripartire da zero, segui la procedura *Come aggiornare i dispositivi già presenti su Alexa*.
- **Opzioni custom**: `hue_type`, `reset_id` e `upnp_allowed_ips` esistono solo in questo componente. Installalo e **riavvia** Home Assistant **prima** di aggiungerle allo YAML: altrimenti il controllo configurazione (che usa ancora l'integrazione ufficiale) le segnala come opzioni non valide e blocca il riavvio.

## 🔍 Diagnostica: leggere il log

Per vedere cosa succede tra il bridge e gli Echo (chi cerca il bridge, a chi risponde, quali richieste vengono ignorate) attiva il log di debug.

### Metodo rapido (senza riavvio)
Vai in **Strumenti per sviluppatori → Azioni**, passa in modalità YAML ed esegui:

```yaml
action: logger.set_level
data:
  custom_components.emulated_hue: debug
```

Il debug resta attivo fino al prossimo riavvio di Home Assistant. Per disattivarlo prima, esegui la stessa azione con `warning` al posto di `debug`.

### Metodo permanente (YAML)
In `configuration.yaml`, se hai già un blocco `logger:` aggiungi solo la riga sotto `logs:`, altrimenti incolla l'intero blocco e riavvia:

```yaml
logger:
  default: warning
  logs:
    custom_components.emulated_hue: debug
```

### Dove leggerlo
**Impostazioni → Sistema → Log → Mostra log completi** (oppure il file `home-assistant.log`).

### Cosa significano le righe

```text
UPNP M-SEARCH da 192.168.1.50 accettato: ...
UPNP risposta a 192.168.1.50: ...
UPNP M-SEARCH da 192.168.1.60 ignorato (non autorizzato)
```

| Riga | Significato |
| ----- | ----- |
| `M-SEARCH da <IP> accettato` | Un dispositivo autorizzato (il tuo master) sta cercando il bridge. |
| `risposta a <IP>` | Il bridge ha risposto: quel dispositivo può trovare e collegare le entità. |
| `M-SEARCH da <IP> ignorato (non autorizzato)` | Un dispositivo non presente in `upnp_allowed_ips` ha cercato il bridge ed è stato ignorato. È normale: gli Echo e molti altri dispositivi (TV, media server...) fanno queste ricerche di continuo. |

**Problemi tipici:**
- **La ricerca su Alexa non trova nulla** e nel log non compare mai `accettato`: l'IP in `upnp_allowed_ips` non è quello del master (o è cambiato), oppure il master è spento/su un'altra rete.
- **Nessuna riga `M-SEARCH`**: il debug non è attivo, oppure gli Echo non sono nella stessa rete di Home Assistant.
- **Dispositivi legati a un Echo sbagliato**: sono residui di ricerche precedenti. Rimuovili dall'app Alexa e ripeti la ricerca: con il filtro attivo torneranno sul master.

## ☕ Supporta il Progetto

Ogni piccolo supporto fa un'enorme differenza: mi aiuta a mantenere vivo l'entusiasmo e mi stimola a creare e condividere nuove soluzioni per la community. Grazie di cuore per il tuo aiuto! 🚀

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/salvatore_dh)

## ❤️ Crediti
Sviluppato da [Salvatore Lentini - DomHouse.it](https://www.domhouse.it)
