function removeSession() {
    // sends a message to delete another session from the user's ip, used when max ip users is reached
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == XMLHttpRequest.DONE && xhttp.status == 200) {
            let response = xhttp.responseText;
            let json = JSON.parse(response);
            if (json["status"] === "success") {
                window.location = "/edit"
                return;
            }

            alert("The server responded incorrectly! Error 502. Please try again, or report a bug.")
        }
    }

    xhttp.open("POST", "/edit/api/remsession");
    xhttp.send("{'type': 'removesession'}")
}