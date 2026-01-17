const params = new URLSearchParams(window.location.search);
const matchId = params.get("id");

if (!matchId) {
    alert("Partita non trovata");
}

// 🔌 WebSocket (o fetch se preferisci)
const ws = new WebSocket("ws://localhost:8888/ws");

ws.onopen = () => {
    console.log("WS aperto (match detail)");
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type !== "matches" || !msg.data) return;

    const match = msg.data.find(m => m.matchId === matchId);
    if (!match) return;

    document.getElementById("match-title").textContent =
        `${match.team1} vs ${match.team2}`;

    document.getElementById("teams").textContent =
        `${match.team1} vs ${match.team2}`;

    document.getElementById("date").textContent = match.date || "-";
    document.getElementById("result").textContent = match.result || "-";
    document.getElementById("state").textContent = match.state || "-";
};
