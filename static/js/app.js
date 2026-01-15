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

    matches.forEach(m => {
        const li = document.createElement("li");
        li.className = "match";

        li.innerHTML = `
            <div class="match-top">
                <span class="match-status" data-state="${m.state.toLowerCase()}">${m.state}</span>
                <span class="match-date">${m.date}</span>
            </div>

            <div class="match-main">
                <div class="match-teams">
                    ${m.team1} vs ${m.team2}
                </div>
                <div class="match-score">
                    ${m.result}
                </div>
            </div>

            <div class="match-bottom">
                ⏱ ${m.time}
            </div>
        `;

        list.appendChild(li);
    });

    console.log("Caricamento completato!");
}
