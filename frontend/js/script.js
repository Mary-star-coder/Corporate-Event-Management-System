
const API_URL = "http://127.0.0.1:8000";

// ==============================
// PASSWORD SHOW / HIDE
// ==============================

const toggleButtons = document.querySelectorAll(".toggle-password");

toggleButtons.forEach(function(button) {
    button.addEventListener("click", function() {
        const inputId = button.getAttribute("data-target");
        const passwordInput = document.getElementById(inputId);

        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            button.textContent = "Hide";
        } else {
            passwordInput.type = "password";
            button.textContent = "Show";
        }
    });
});


// ==============================
// LOAD EVENTS
// ==============================

async function loadEvents() {
    const eventGrid = document.getElementById("eventGrid");

    if (!eventGrid) return;

    try {
        const response = await fetch(`${API_URL}/events`);

        if (!response.ok) {
            throw new Error("Unable to load events");
        }

        const events = await response.json();

        if (events.length === 0) {
            eventGrid.innerHTML = "<p>No events available yet.</p>";
            return;
        }

        eventGrid.innerHTML = events.map((event, index) => {
            const eventDate = new Date(event.event_date);

            const date = eventDate.toLocaleDateString("en-PK", {
                day: "2-digit",
                month: "short"
            });

            const imageClass = ["image-one", "image-two", "image-three"][index % 3];

            return `
                <article class="event-card">
                    <div class="event-image ${imageClass}">
                        <span class="category-tag">EVENT</span>
                        <span class="date-tag">${date}</span>
                    </div>
                    <div class="event-info">
                        <span class="event-location">${event.location}</span>
                        <h3>${event.title}</h3>
                        <p>${event.description || "Join us for this exciting event."}</p>
                        <button type="button"
    class="event-link register-event-btn"
    data-event-id="${event.id}">
    Register Now ↗
</button>
                    </div>
                </article>
            `;
        }).join("");

    } catch (error) {
        console.error("Error loading events:", error);
        eventGrid.innerHTML = "<p>Unable to load events.</p>";
    }
}


// ==============================
// USER SIGNUP
// ==============================

const registerForm = document.querySelector(".register-layout .auth-form");

if (registerForm) {
    registerForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const fullName = document.getElementById("full-name").value.trim();
        const email = document.getElementById("register-email").value.trim();
        const password = document.getElementById("register-password").value;
        const confirmPassword = document.getElementById("confirm-password").value;

        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    full_name: fullName,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                alert(data.detail || "Registration failed!");
                return;
            }

            alert("Account created successfully! Please log in.");
            window.location.href = "login.html";

        } catch (error) {
            console.error("Signup error:", error);
            alert("Unable to connect to server. Please try again.");
        }
    });
}


// ==============================
// USER LOGIN
// ==============================

const loginForm = document.querySelector(".login-layout .auth-form");

if (loginForm) {
    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const email = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value;

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                alert(data.detail || "Login failed!");
                return;
            }

            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("user", JSON.stringify(data.user));

            alert("Login successful! Welcome " + data.user.full_name);
            window.location.href = "index.html";

        } catch (error) {
            console.error("Login error:", error);
            alert("Unable to connect to server. Please try again.");
        }
    });
}


// ==============================
// PAGE LOAD
// ==============================

document.addEventListener("DOMContentLoaded", loadEvents);

// ==============================
// USER WELCOME AND LOGOUT
// ==============================

document.addEventListener("DOMContentLoaded", function() {

    const navActions = document.getElementById("navActions");

    if (!navActions) return;

    const user = JSON.parse(localStorage.getItem("user"));

    if (user) {
        navActions.innerHTML = `
            <span class="login-link">
                Welcome, ${user.full_name}
            </span>
            <button class="nav-cta" id="logoutBtn">
                Logout
            </button>
        `;

        document.getElementById("logoutBtn").addEventListener("click", function() {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");

            alert("You have logged out successfully!");

            window.location.href = "login.html";
        });
    }
});

// ==============================
// EVENT REGISTRATION
// ==============================

const eventGridForRegistration = document.getElementById("eventGrid");

if (eventGridForRegistration) {

    eventGridForRegistration.addEventListener("click", async function(event) {

        const button = event.target.closest(".register-event-btn");

        if (!button) return;

        const user = JSON.parse(localStorage.getItem("user"));

        if (!user) {
            alert("Please login first!");
            window.location.href = "login.html";
            return;
        }

        const eventId = Number(button.dataset.eventId);

        button.disabled = true;

        try {
            const response = await fetch(`${API_URL}/registrations`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    event_id: eventId,
                    attendee_name: user.full_name,
                    attendee_email: user.email
                })
            });

            const data = await response.json();

            if (!response.ok) {
                alert(data.detail || "Registration failed!");
                button.disabled = false;
                return;
            }

            alert("Event registration successful!");

            await loadEvents();

        } catch (error) {
            console.error("Registration error:", error);
            alert("Unable to connect to server!");
            button.disabled = false;
        }
    });
}