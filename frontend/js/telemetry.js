async function loadTelemetry() {

    try {

        const response =
        await fetch(
            "http://127.0.0.1:5000/api/telemetry"
        );

        const data =
        await response.json();

        document.getElementById(
            "batteryValue"
        ).innerText =
        data.battery + "%";

        document.getElementById(
            "temperatureValue"
        ).innerText =
        data.temperature + "°C";

        document.getElementById(
            "speedValue"
        ).innerText =
        data.speed;

        document.getElementById(
            "latencyValue"
        ).innerText =
        data.latency + "ms";
    }

    catch(error) {

        console.error(error);
    }
}

/* AUTO REFRESH */

setInterval(
    loadTelemetry,
    2000
);