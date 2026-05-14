console.log(
    "AI Robotics Dashboard Loaded"
);

const BACKEND_URL =
"http://127.0.0.1:5000";

/* ================================ */
/* START */
/* ================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializeApp();
    }
);

/* ================================ */
/* INITIALIZE */
/* ================================ */

function initializeApp() {

    console.log(
        "Initializing Dashboard..."
    );

    loadTelemetry();
}