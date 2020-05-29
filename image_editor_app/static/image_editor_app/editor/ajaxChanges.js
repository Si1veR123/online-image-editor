// handles ajax requests with server

crop_mode = false

function edit(data) {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == XMLHttpRequest.DONE && xhttp.status == 200) {
            // on ready, parse JSON response and notify of errors, else reload image
            let response = xhttp.responseText;
            let json = JSON.parse(response);
            if (json["type"] === "error") {
                alert(json["error"]);
                return;
            }
            if (json["type"] === "link") {
                let im = document.getElementById("image");
                let download = document.getElementById("download");
                im.setAttribute("src", json["imageLink"]);
                download.setAttribute("href", json["imageLink"]);
                return;
            }

            // server responded without error message or link
            alert("The server responded incorrectly! Error 502. Please try again later, or report a bug.")
        }
    }
    // send AJAX POST request to makeEdit API
    xhttp.open("POST", "/edit/api/makeEdit");
    xhttp.send(data)
}

// send undo to server
function undo() {
    edit('{"type": "undo"}')
}

// send redo to server
function redo() {
    edit('{"type": "redo"}')
}

// not completed
function filter() {

}

function crop() {
    let box = document.getElementById("crop-box");
    let image = document.getElementById("image");

    // get ratio for upscale of image
    let ratio = image.naturalWidth / image.offsetWidth;

    // send data to server for cropping
    document.getElementById("crop-confirm").style.transform = "scale(0)";
    edit('{"type": "crop", "data": ' + "[" + (box.offsetLeft - image.offsetLeft) * ratio + "," + (box.offsetTop - image.offsetTop) * ratio + "," + box.offsetWidth * ratio + "," + box.offsetHeight * ratio + "]}")

    cancelCrop();
}

// send rotate data
function rotate(dir) {
    edit('{"type": "rotate", "data": ' + '"' + dir + '"' + '}')
}

// send HSL adjustments
function adjust(form) {
    // get values from sliders
    let hSlider = document.getElementById("h-slider");
    let sSlider = document.getElementById("s-slider");
    let lSlider = document.getElementById("l-slider");

    // check value has been changed
    if (hSlider.value !== "50" || sSlider.value !== "50" || lSlider.value !== "50") {
        // JSON data
        data = {
            "type": "adjust",
            "data": {
                        "h": -50 + Number(hSlider.value),
                        "s": -50 + Number(sSlider.value),
                        "l": -50 + Number(lSlider.value)
                    }
        }

        // send data as a string
        edit(JSON.stringify(data))

        // reset data
        hSlider.value = 50;
        sSlider.value = 50;
        lSlider.value = 50;

        // reset text next to sliders
        document.getElementById("h-value").innerHTML = 0;
        document.getElementById("s-value").innerHTML = 0;
        document.getElementById("l-value").innerHTML = 0;
    }
}
