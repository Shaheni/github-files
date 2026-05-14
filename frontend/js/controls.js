async function sendCommand(command) {

    try {

        const response =
        await fetch(

            "http://127.0.0.1:5000/api/control",

            {

                method: "POST",

                headers: {

                    "Content-Type":
                    "application/json"
                },

                body: JSON.stringify({

                    command: command
                })
            }
        );

        const data =
        await response.json();

        console.log(data);
    }

    catch(error) {

        console.error(error);
    }
}