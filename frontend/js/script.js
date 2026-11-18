
// Base URL of the FastAPI backend server.
const API_URL = "http://127.0.0.1:8000";


// ==========================================
// PASSWORD SHOW / HIDE
// ==========================================

// Select all buttons used to show or hide passwords.
const toggleButtons = document.querySelectorAll(".toggle-password");

// Add a click event to every password toggle button.
toggleButtons.forEach(function(button) {
    button.addEventListener("click", function() {

        // Get the ID of the password input connected to this button.
        const inputId = button.getAttribute("data-target");

        // Find the corresponding password input field.
        const passwordInput = document.getElementById(inputId);

        // Change the input type to show or hide the password.
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            button.textContent = "Hide";
        } else {
            passwordInput.type = "password";
            button.textContent = "Show";
        }
    });
});


// ==========================================
// LOAD EVENTS
// ==========================================

// Fetch events from the backend and display them on the homepage.
async function loadEvents() {

    // Find the container where event cards will appear.
    const eventGrid = document.getElementById("eventGrid");

    // Stop if the current page does not contain an event grid.
    if (!eventGrid) return;

    try {
        // Send a GET request to retrieve all available events.
        const response = await fetch(`${API_URL}/events`);

        // Check whether the server returned a successful response.
        if (!response.ok) {
            throw new Error("Unable to load events");
        }

        // Convert the server response into JavaScript data.
        const events = await response.json();

        // Display a message if no events are available.
        if (events.length === 0) {
            eventGrid.innerHTML = "<p>No events available yet.</p>";
            return;
        }

        // Create an HTML card for each event received from the API.
        eventGrid.innerHTML = events.map((event, index) => {

            // Convert the event date into a JavaScript Date object.
            const eventDate = new Date(event.event_date);

            // Format the date for display on the event card.
            const date = eventDate.toLocaleDateString("en-PK", {
                day: "2-digit",
                month: "short"
            });

            // Select an image style by cycling through three CSS classes.
            const imageClass = ["image-one", "image-two", "image-three"][index % 3];

            // Return the HTML structure for one event card.
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

        // Display the error in the browser console for debugging.
        console.error("Error loading events:", error);

        // Show a friendly message if events cannot be loaded.
        eventGrid.innerHTML = "<p>Unable to load events.</p>";
    }
}


// ==========================================
// USER SIGNUP
// ==========================================

// Find the registration form on the signup page.
const registerForm = document.querySelector(".register-layout .auth-form");

// Run this code only if the signup form exists on the current page.
if (registerForm) {

    // Handle form submission without refreshing the page.
    registerForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        // Read and clean the user's signup information.
        const fullName = document.getElementById("full-name").value.trim();
        const email = document.getElementById("register-email").value.trim();
        const password = document.getElementById("register-password").value;
        const confirmPassword = document.getElementById("confirm-password").value;

        // Check whether both entered passwords match.
        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        try {
            // Send signup information to the backend registration endpoint.
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

            // Read the response returned by the backend.
            const data = await response.json();

            // Display the backend validation or registration error.
            if (!response.ok) {
                alert(data.detail || "Registration failed!");
                return;
            }

            // Notify the user and redirect to the login page.
            alert("Account created successfully! Please log in.");
            window.location.href = "login.html";

        } catch (error) {

            // Log connection or request errors for debugging.
            console.error("Signup error:", error);

            // Inform the user if the backend cannot be reached.
            alert("Unable to connect to server. Please try again.");
        }
    });
}


// ==========================================
// USER LOGIN
// ==========================================

// Find the login form on the login page.
const loginForm = document.querySelector(".login-layout .auth-form");

// Run this code only if the login form exists.
if (loginForm) {

    // Handle login form submission without refreshing the page.
    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        // Read the user's login credentials.
        const email = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value;

        try {
            // Send login credentials to the backend login endpoint.
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

            // Convert the backend response into JavaScript data.
            const data = await response.json();

            // Show an error if the login credentials are incorrect.
            if (!response.ok) {
                alert(data.detail || "Login failed!");
                return;
            }

            // Save the JWT access token in browser local storage.
            localStorage.setItem("access_token", data.access_token);

            // Save the logged-in user's basic information.
            localStorage.setItem("user", JSON.stringify(data.user));

            // Welcome the user and redirect to the homepage.
            alert("Login successful! Welcome " + data.user.full_name);
            window.location.href = "index.html";

        } catch (error) {

            // Log login request errors for debugging.
            console.error("Login error:", error);

            // Display a connection error message.
            alert("Unable to connect to server. Please try again.");
        }
    });
}


// ==========================================
// PAGE LOAD
// ==========================================

// Load events when the page has finished loading.
document.addEventListener("DOMContentLoaded", loadEvents);


// ==========================================
// USER WELCOME AND LOGOUT
// ==========================================

// Run the navigation update after the page content loads.
document.addEventListener("DOMContentLoaded", function() {

    // Find the navigation area that displays login actions.
    const navActions = document.getElementById("navActions");

    // Stop if this page does not contain the navigation area.
    if (!navActions) return;

    // Retrieve the logged-in user's information from local storage.
    const user = JSON.parse(localStorage.getItem("user"));

    // Display the user's name and logout button if logged in.
    if (user) {
        navActions.innerHTML = `
            <span class="login-link">
                Welcome, ${user.full_name}
            </span>
            <button class="nav-cta" id="logoutBtn">
                Logout
            </button>
        `;

        // Add a click event to the logout button.
        document.getElementById("logoutBtn").addEventListener("click", function() {

            // Remove the saved JWT token and user information.
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");

            // Inform the user that logout was successful.
            alert("You have logged out successfully!");

            // Redirect the user to the login page.
            window.location.href = "login.html";
        });
    }
});


// ==========================================
// EVENT REGISTRATION
// ==========================================

// Find the event grid where registration buttons are displayed.
const eventGridForRegistration = document.getElementById("eventGrid");

// Add registration functionality only if the event grid exists.
if (eventGridForRegistration) {

    // Listen for clicks inside the event grid.
    // Event delegation handles buttons created dynamically by loadEvents().
    eventGridForRegistration.addEventListener("click", async function(event) {

        // Find the registration button that was clicked.
        const button = event.target.closest(".register-event-btn");

        // Ignore clicks that are not on a registration button.
        if (!button) return;

        // Get the logged-in user's information from local storage.
        const user = JSON.parse(localStorage.getItem("user"));

        // Require login before allowing event registration.
        if (!user) {
            alert("Please login first!");
            window.location.href = "login.html";
            return;
        }

        // Read the event ID stored in the clicked button.
        const eventId = Number(button.dataset.eventId);

        // Disable the button to prevent repeated clicks while processing.
        button.disabled = true;

        try {
            // Send the registration details to the backend.
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

            // Read the backend response.
            const data = await response.json();

            // Display any registration error returned by the backend.
            if (!response.ok) {
                alert(data.detail || "Registration failed!");
                button.disabled = false;
                return;
            }

            // Confirm successful registration to the user.
            alert("Event registration successful!");

            // Reload events to display the latest available seat counts.
            await loadEvents();

        } catch (error) {

            // Log registration request errors for debugging.
            console.error("Registration error:", error);

            // Show a message if the backend connection fails.
            alert("Unable to connect to server!");

            // Re-enable the button so the user can try again.
            button.disabled = false;
        }
    });
}
