const ws = new WebSocket("ws://localhost:8888/ws");

ws.onopen = () => {
    console.log("WebSocket aperto");
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    console.log("RAW MESSAGE:", event.data);
    console.log("PARSED:", msg);

    // gestisce solo i messaggi matches
    if (msg.type !== "matches") return;

    console.log("Ricevute partite:", msg.data.length);
    renderMatches(msg.data);
};

ws.onclose = () => {
    console.log("WebSocket chiuso");
};

ws.onerror = (error) => {
    console.error("Errore WebSocket:", error);
};

console.log("caricato app");

// 👇 SOLO rendering (WebSocket-only)
function renderMatches(matches) {
    const list = document.getElementById("matchList");
    list.innerHTML = "";

    matches.forEach(t => {
        const li = document.createElement("li");

        // Team1
        const team1Span = document.createElement("span");
        team1Span.textContent = t.team1;

        // Team2
        const team2Span = document.createElement("span");
        team2Span.textContent = t.team2;

        // Tempo
        const timeSpan = document.createElement("span");
        timeSpan.textContent = t.time;

        // Risultato
        const resultSpan = document.createElement("span");
        resultSpan.textContent = t.result;

        // Data
        const dateSpan = document.createElement("span");
        dateSpan.textContent = t.date;

        li.appendChild(team1Span);
        li.appendChild(team2Span);
        li.appendChild(timeSpan);
        li.appendChild(resultSpan);
        li.appendChild(dateSpan);

        list.appendChild(li);
    });

    console.log("Caricamento completato!");
}
