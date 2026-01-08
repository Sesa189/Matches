async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/api/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    });

    const data = await res.json();
    alert(data.message || data.error);

    if (res.status === 200)
        location.href = "index.html";
}


async function registerUser() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch("/api/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    });

    const data = await res.json();
    alert(data.message || data.error);

    if (res.status === 201)
        location.href = "login.html";
}


async function logout() {
    await fetch("/api/logout", {method: "POST"});
    location.href = "login.html";
}


async function loadTasks() {
    const resUser = await fetch("/api/user", { credentials: "include" });

    if (resUser.status !== 200) {
        location.href = "login.html";
        return;
    }

    const user = await resUser.json()

    const res = await fetch("/api/tasks", { credentials: "include" });

    if (res.status !== 200) {
        location.href = "login.html";
        return;
    }

    const data = await res.json();
    console.log(data.items);
    const list = document.getElementById("taskList");
    list.innerHTML = "";

    data.items.forEach(t => {
        const li = document.createElement("li");
        li.className = t.done ? "done" : "";

        if(user.email == t.email ){
            li.classList.add("current");
        }

        // Email + ora
        const emailSpan = document.createElement("span");
        if(user.email == t.email ){
            emailSpan.innerHTML = `<strong>You</strong> • ${t.date} :`;
        }
        else{
            emailSpan.innerHTML = `<strong>${t.email}</strong> • ${t.date} :`;
        }

        //Ora

        // Testo
        const textSpan = document.createElement("span");
        textSpan.textContent = t.text;

        // Area icone
        const actions = document.createElement("div");

        /*
        // ✓ / ↺ icona
        const toggle = document.createElement("button");
        toggle.className = "icon-btn";
        toggle.innerHTML = t.done
            ? '<i class="fa-solid fa-rotate-left" title="Segna come incompleta"></i>'
            : '<i class="fa-solid fa-check" title="Completa"></i>';
        toggle.onclick = () => updateTask(t.id, !t.done);
        */

        // 🗑 icona
        const del = document.createElement("button");
        del.className = "icon-btn";
        del.innerHTML = '<i class="fa-solid fa-trash" title="Elimina"></i>';
        del.onclick = () => deleteTask(t.id);

        //actions.appendChild(toggle);
        if(user.email == t.email){
            actions.appendChild(del);
        }

        li.appendChild(emailSpan);
        li.appendChild(textSpan);
        li.appendChild(actions);
        list.appendChild(li);
        console.log("Task:", t);
    });
}

async function addTask() {
    const text = document.getElementById("taskText").value;

    await fetch("/api/tasks", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text})
    });

    loadTasks();
}

/*
async function updateTask(id, done) {
    await fetch(`/api/tasks/${id}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({done})
    });

    loadTasks();
}
*/

async function deleteTask(id) {
    await fetch(`/api/tasks/${id}/delete`, {method: "DELETE"});
    loadTasks();
}

if (location.pathname.endsWith("index.html"))
    loadTasks();
