console.log("caricato app");

async function loadTasks() {
    const res = await fetch("/api/matches", { credentials: "include" });

    const data = await res.json();
    console.log(data.items);
    const list = document.getElementById("matchList");
    list.innerHTML = "";

    console.log(data);

    data.items.forEach(t => {
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

        // Area icone
        const actions = document.createElement("div");


        /*
        🗑 icona
        const del = document.createElement("button");
        del.className = "icon-btn";
        del.innerHTML = '<i class="fa-solid fa-trash" title="Elimina"></i>';
        del.onclick = () => deleteTask(t.id);
        */

        li.appendChild(team1Span);
        li.appendChild(team2Span);
        li.appendChild(timeSpan);
        li.appendChild(resultSpan);
        li.appendChild(dateSpan);
        list.appendChild(li);
        console.log("Task:", t);

        console.log("✅ 6. Caricamento completato!");
    });
}

/*
if (location.pathname.endsWith("index.html"))
    loadTasks();
*/

document.addEventListener('DOMContentLoaded', loadTasks);
