document.addEventListener("DOMContentLoaded", () => {
    const ws = new WebSocket("ws://localhost:8888/ws");

    const urlParams = new URLSearchParams(window.location.search);
    const matchId = urlParams.get('id');

    console.log("Match ID richiesto:", matchId);

    if (!matchId) {
        document.getElementById("loading").textContent = "❌ Partita non trovata";
        return;
    }

    let matchFound = false;

    ws.onopen = () => {
        console.log("WebSocket aperto per dettaglio partita");
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        console.log("Messaggio WebSocket ricevuto:", msg);

        if (msg.type !== "matches") return;

        console.log("Confronto matchId:", {
            ricevuto: msg.matchId,
            cercato: matchId,
            match: msg.matchId === matchId
        });

        const isMatchById = msg.matchId === matchId;
        const isMatchByTeams = matchId.includes(msg.team1?.toLowerCase().replace(/\s+/g, '_')) &&
                               matchId.includes(msg.team2?.toLowerCase().replace(/\s+/g, '_'));

        if (isMatchById || isMatchByTeams) {
            console.log("✅ Dati partita ricevuti:", msg);
            matchFound = true;

            document.getElementById("loading").style.display = "none";
            document.getElementById("match-content").style.display = "block";

            updateMatchDetails(msg);
        }
    };

    ws.onclose = () => console.log("WebSocket chiuso");
    ws.onerror = (error) => console.error("Errore WebSocket:", error);

    function updateMatchDetails(match) {
        document.getElementById("match-title").textContent =
            `${match.team1} vs ${match.team2}`;

        const badge = document.getElementById("match-status-badge");
        const state = (match.state || "SCHEDULED").toLowerCase();
        badge.textContent = match.state || "SCHEDULED";
        badge.className = `match-status-badge ${state}`;

        const category = match.category === "torneo" ? "🏆 Torneo" : "🏐 Campionato";
        document.getElementById("category").textContent = category;

        document.getElementById("date").textContent = match.date || "-";

        document.getElementById("time").textContent = match.time || "00:00";

        document.getElementById("state").textContent = match.state || "SCHEDULED";

        document.getElementById("team1").textContent = match.team1;
        document.getElementById("team2").textContent = match.team2;

        let scoreText = "0 : 0";
        if (Array.isArray(match.result) && match.result.length > 0) {
            scoreText = match.result.filter(r => r).join("  |  ");
        } else if (match.result) {
            scoreText = match.result;
        }
        document.getElementById("score-value").textContent = scoreText;

        const eventsList = document.getElementById("events-list");
        if (match.events && match.events.length > 0) {
            eventsList.innerHTML = "";
            match.events.forEach(event => {
                const li = document.createElement("li");
                li.className = "event-item";
                li.textContent = event;
                eventsList.appendChild(li);
            });

            eventsList.scrollTop = eventsList.scrollHeight;
        }

        if (match.state === "FINISHED" && match.winner) {
            const winnerBanner = document.getElementById("winner-banner");
            winnerBanner.textContent = `Vincitore: ${match.winner}`;
            winnerBanner.style.display = "block";
        }
    }

    setTimeout(() => {
        if (!matchFound) {
            document.getElementById("loading").textContent =
                "⏳ In attesa dei dati della partita...";
        }
    }, 5000);
});