document.addEventListener("DOMContentLoaded", () => {
    const ws = new WebSocket("ws://localhost:8888/ws");

    const faseContainer = document.getElementById("fase-container");
    const giornataContainer = document.getElementById("giornata-container");

    const fasi = [
        { name: "Ottavi", number: 8 },
        { name: "Quarti", number: 4 },
        { name: "Semifinali", number: 2 },
        { name: "Finali", number: 1 }
    ];

    let currentFase = null;
    let currentGiornata = null;
    let currentView = "torneo"; // stato selezionato
    let torneoMatches = [];
    let campionatoMatches = [];

    const btnTorneo = document.getElementById("btn-torneo");
    const btnCampionato = document.getElementById("btn-campionato");

    // ===== Inizializza partite segnaposto =====
    function inizializzaSegnaposto() {
        // === SEGNAPOSTO TORNEO ===
        // Ottavi: 8 partite
        for (let i = 1; i <= 8; i++) {
            torneoMatches.push({
                number: 8,
                stage: "ottavi",
                team1: `TBD`,
                team2: `TBD`,
                date: "",
                state: "SCHEDULED",
                result: "",
                isPlaceholder: true,
                matchId: `ottavo_${i}`
            });
        }

        // Quarti: 4 partite
        for (let i = 1; i <= 4; i++) {
            torneoMatches.push({
                number: 4,
                stage: "quarti",
                team1: `Vincitore Ottavo ${i*2-1}`,
                team2: `Vincitore Ottavo ${i*2}`,
                date: "",
                state: "SCHEDULED",
                result: "",
                isPlaceholder: true,
                matchId: `quarto_${i}`
            });
        }

        // Semifinali: 2 partite
        for (let i = 1; i <= 2; i++) {
            torneoMatches.push({
                number: 2,
                stage: "semifinali",
                team1: `Vincitore Quarto ${i*2-1}`,
                team2: `Vincitore Quarto ${i*2}`,
                date: "",
                state: "SCHEDULED",
                result: "",
                isPlaceholder: true,
                matchId: `semifinale_${i}`
            });
        }

        // Finale: 1 partita
        torneoMatches.push({
            number: 1,
            stage: "finale",
            team1: `Vincitore Semifinale 1`,
            team2: `Vincitore Semifinale 2`,
            date: "",
            state: "SCHEDULED",
            result: "",
            isPlaceholder: true,
            matchId: `finale_1`
        });

        console.log(`Segnaposto creati: ${torneoMatches.length} torneo, ${campionatoMatches.length} campionato`);
    }

    // ===== Mostra pulsanti Fasi =====
    function mostraFasi() {
        faseContainer.innerHTML = "";
        fasi.forEach((fase, index) => {
            const btn = document.createElement("button");
            btn.textContent = fase.name;
            btn.className = "fase-btn";

            if (index === 0 && currentFase === null)  {
                btn.classList.add("active");
                currentFase = fase.number;
            }

            btn.onclick = () => {
                currentFase = fase.number;

                // Rimuovo active da tutti i pulsanti
                document.querySelectorAll(".fase-btn").forEach(b => b.classList.remove("active"));
                // Aggiungo active al pulsante selezionato
                btn.classList.add("active");

                filtraEVisualizza();
            };

            faseContainer.appendChild(btn);
        });

        faseContainer.style.display = "flex";
    }

    function nascondiFasi() {
        faseContainer.style.display = "none";
        currentFase = null;
    }

    // ===== Mostra menu Giornate =====
    function mostraGiornate() {
        giornataContainer.innerHTML = "";

        const label = document.createElement("label");
        label.textContent = "Giornata: ";
        label.className = "giornata-label";

        const select = document.createElement("select");
        select.className = "giornata-select";
        select.id = "giornata-select";

        // Opzione "Tutte"
        const optionAll = document.createElement("option");
        optionAll.value = "all";
        optionAll.textContent = "Tutte le giornate";
        select.appendChild(optionAll);

        // Opzioni giornate (assumiamo 30 giornate per un campionato tipico)
        for (let i = 1; i <= 30; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = `Giornata ${i}`;
            select.appendChild(option);
        }

        select.onchange = (e) => {
            currentGiornata = e.target.value === "all" ? null : parseInt(e.target.value);
            filtraEVisualizza();
        };

        giornataContainer.appendChild(label);
        giornataContainer.appendChild(select);
        giornataContainer.style.display = "flex";
    }

    function nascondiGiornate() {
        giornataContainer.style.display = "none";
        currentGiornata = null;
    }

    // ===== Filtra e renderizza match =====
    function filtraEVisualizza() {
        let matches = currentView === "torneo" ? torneoMatches : campionatoMatches;

        // Filtra per fase (torneo usa 'number', campionato usa 'stage' come giornata)
        if (currentView === "torneo" && currentFase !== null) {
            matches = matches.filter(m => m.number === currentFase);
        }

        // Filtra per giornata (usa il campo 'stage' che contiene il numero della giornata)
        if (currentView === "campionato" && currentGiornata !== null) {
            matches = matches.filter(m => m.stage === currentGiornata);
        }

        renderMatches(matches);
    }

    // ===== Pulsanti Torneo / Campionato =====
    btnTorneo.onclick = () => {
        console.log("Cliccato Torneo");
        currentView = "torneo";
        setActiveButton();
        mostraFasi(); // mostra i pulsanti delle fasi
        nascondiGiornate(); // nasconde il menu giornate
        filtraEVisualizza();
    };

    btnCampionato.onclick = () => {
        console.log("Cliccato Campionato");
        currentView = "campionato";
        setActiveButton();
        nascondiFasi(); // nasconde i pulsanti delle fasi
        mostraGiornate(); // mostra il menu giornate
        filtraEVisualizza();
    };

    function setActiveButton() {
        btnTorneo.classList.toggle("active", currentView === "torneo");
        btnCampionato.classList.toggle("active", currentView === "campionato");
    }

    // ===== WebSocket =====
    ws.onopen = () => {
        console.log("WebSocket aperto");
        inizializzaSegnaposto(); // Crea i segnaposto all'apertura
        filtraEVisualizza(); // Mostra i segnaposto
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        console.log("Messaggio ricevuto:", msg);

        if (msg.type === "calendario" && msg.category === "campionato") {
            console.log("Calendario campionato ricevuto");

            campionatoMatches = [];

            Object.entries(msg.data).forEach(([giornata, partite]) => {
                partite.forEach(([team1, team2], index) => {
                    campionatoMatches.push({
                        stage: parseInt(giornata), // Usa 'stage' invece di 'giornata'
                        team1,
                        team2,
                        date: `Giornata ${giornata}`,
                        state: "SCHEDULED",
                        result: "",
                        isPlaceholder: true,
                        matchId: `giornata_${giornata}_match_${index}`
                    });
                });
            });

            // Se l'utente è già in vista campionato, aggiorna
            if (currentView === "campionato") {
                filtraEVisualizza();
            }

            return;
        }

        if (msg.type !== "matches") return;

        let matchesArray = msg.category === "torneo" ? torneoMatches
                        : msg.category === "campionato" ? campionatoMatches
                        : null;
        if (!matchesArray) return;

        if (msg.data) {
            msg.data.forEach(partita => {
                const index = matchesArray.findIndex(m => m.team1 === partita.team1 && m.team2 === partita.team2);
                if (index !== -1) {
                    // Mantieni lo stage dal segnaposto se esiste
                    matchesArray[index] = { ...matchesArray[index], ...partita, isPlaceholder: false };
                } else {
                    matchesArray.push(partita);
                }
            });
        } else {
            // Cerca un segnaposto della stessa fase che è ancora SCHEDULED
            let placeholderIndex = -1;
            if (msg.category === "torneo") {
                placeholderIndex = matchesArray.findIndex(m =>
                    m.isPlaceholder &&
                    m.number === msg.number &&
                    m.state === "SCHEDULED"
                );
            } else if (msg.category === "campionato") {
                // Per il campionato, cerca il segnaposto con le stesse squadre
                placeholderIndex = matchesArray.findIndex(m =>
                    m.team1 === msg.team1 && m.team2 === msg.team2
                );
            }

            if (placeholderIndex !== -1) {
                // Sostituisci il segnaposto mantenendo lo stage (giornata per campionato)
                console.log(`Sostituzione segnaposto ${placeholderIndex} con partita reale:`, msg.team1, "vs", msg.team2);
                const stage = matchesArray[placeholderIndex].stage;
                matchesArray[placeholderIndex] = { ...msg, stage, isPlaceholder: false };
            } else {
                // Cerca se la partita esiste già (per aggiornamenti)
                const existingIndex = matchesArray.findIndex(m =>
                    m.team1 === msg.team1 && m.team2 === msg.team2
                );

                if (existingIndex !== -1) {
                    // Aggiorna partita esistente mantenendo lo stage
                    const stage = matchesArray[existingIndex].stage;
                    matchesArray[existingIndex] = { ...msg, stage, isPlaceholder: false };
                } else {
                    // Aggiungi nuova partita
                    matchesArray.push({ ...msg, isPlaceholder: false });
                }
            }
        }

        // Filtra e aggiorna se la categoria corrente corrisponde
        if (currentView === msg.category) filtraEVisualizza();
    };

    ws.onclose = () => console.log("WebSocket chiuso");
    ws.onerror = (error) => console.error("Errore WebSocket:", error);

    // ===== Rendering =====
    function renderMatches(matches) {
        const list = document.getElementById("matchList");
        list.innerHTML = "";

        matches.forEach(m => {
            const li = document.createElement("li");
            li.className = "match";

            // Aggiungi classe per segnaposto
            if (m.isPlaceholder) {
                li.classList.add("placeholder");
            }

            // CLICK → PAGINA DETTAGLIO
            li.onclick = () => {
                window.location.href = `/match.html?id=${encodeURIComponent(m.matchId)}`;
            };

            li.innerHTML = `
                <div class="match-top">
                    <span class="match-status" data-state="${m.state?.toLowerCase() || 'unknown'}">${m.state || 'UNKNOWN'}</span>
                    <span class="match-date">${m.date || ''}</span>
                </div>
                <div class="match-main">
                    <div class="match-teams">${m.team1} vs ${m.team2}</div>
                    <div class="match-score">${Array.isArray(m.result) ? m.result.join(" ") : m.result || ''}</div>
                </div>
            `;

            list.appendChild(li);
        });
    }

    // ===== Avvio =====
    setActiveButton();
    mostraFasi(); // mostra le fasi perché di default è "torneo"
    // Non chiamare filtraEVisualizza() qui perché sarà chiamato da ws.onopen
});