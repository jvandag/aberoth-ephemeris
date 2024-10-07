const key = 'admin' //set to what ever your key is set to in your .env file
let vars = {
    //times are epoch timestamps in ms
    //orb options are white, black, green, red, purple, yellow, cyan, and blue
    //Orb: [startTime, StopTime]
    green: [1715107314000, 1715208745000],
    black: [1715107314000, 1715308745000],
    red: [1714407314000, 1715404745000],
    white: [1715407314000, 1715908745000]
}

function sendData() {
    const url = 'http://<server-ip>:5000/update-variables';  // Replace <server-ip> with your server's IP address
    const data = {
        message: "",
        timestamp: new Date().toISOString(),
        vars: vars

    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${key}`
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}