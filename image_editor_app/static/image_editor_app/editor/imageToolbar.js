var image = document.getElementById("image");
const ZOOM_AMOUNT = 1.1;

// for cropping, if first corner is selected, is true
firstSet = false;
// adjust menu open?
adj_menu_open = false;

function recenter(e) {
    // e is mouse click event
    // calculates and updates new image offset from mouse click

    // get center of image
    let centerX = image.offsetWidth / 2;
    let centerY = image.offsetHeight / 2;

    // get mouse click x and y
    let x = e.offsetX;
    let y = e.offsetY;

    // difference = image center - mouse click x/y
    let xDiff = centerX - x;
    let yDiff = centerY - y;

    // update offset
    image.setAttribute("data-centeroffset", String(xDiff) + "," + String(yDiff))
    centerImage()
}

function resetCenter() {
    // resets offset so image is in middle of canvas
    image.setAttribute("data-centeroffset", "0,0");
    centerImage()
}

function centerImage() {
    // positions image from current offset

    // get x axis empty space (on left/right)
    let xDiff = canvas.clientWidth - image.clientWidth;
    // get y axis empty space (on top/bottom)
    let yDiff = canvas.clientHeight - image.clientHeight;

    // get offsets
    let offsets = image.getAttribute("data-centeroffset").split(",");
    let xOffset = parseFloat(offsets[0]);
    let yOffset = parseFloat(offsets[1]);

    // new left/top = whitespace / 2 + offset
    image.style.left = (xDiff / 2) + xOffset;
    image.style.top = (yDiff / 2) + yOffset;
}

function zoom() {
    // zooms image

    // get image ratio
    let ratio = image.naturalWidth / image.naturalHeight;
    // times height by zoom amount
    image.height = image.offsetHeight * ZOOM_AMOUNT;
    // recalculate image width
    image.width = image.height * ratio;

    centerImage()
}

function zoomOut() {
    // zooms out on image

    // get image ratio
    let ratio = image.naturalWidth / image.naturalHeight;
    // divide height by zoom amount
    image.height = image.offsetHeight / ZOOM_AMOUNT;
    // recalculate width
    image.width = image.height * ratio;

    centerImage()
}

function resetZoom() {
    // reset zoom by reloading image
    let im = document.getElementById("image");
    im.setAttribute("src", im.getAttribute("src"))
}

function drawCropBox(e) {
    // draws crop box, called by event listener for clicks
    let x = e.offsetX;
    let y = e.offsetY;

    // if not clicking on canvas
    if (e.path[0] !== document.getElementById("canvas")) {
        let cropBox = document.getElementById("crop-box");
        // if click is first click
        if (!firstSet) {
            // make box opaque
            document.getElementById("crop-box").style.opacity = 1;
            // set all dimensions to 0
            cropBox.style.width = 0;
            cropBox.style.height = 0;
            cropBox.style.top = 0;
            cropBox.style.left = 0;
            // draw on click location
            cropBox.style.top = y + image.offsetTop;
            cropBox.style.left = x + image.offsetLeft;

            firstSet = true;
        } else {
            // set width/height to new click x/y - old click x/y
            cropBox.style.width = x - (cropBox.offsetLeft - image.offsetLeft);
            cropBox.style.height = y - (cropBox.offsetTop - image.offsetTop);
            firstSet = false;
        }
    } else {
        alert("Please click on the image.")
    }
}

function canvasClick(e) {
    // on click, if not in crop mode, center image
    if (!crop_mode) {
        recenter(e)
    // if in crop mode, pass to drawCropBox function
    } else {
        drawCropBox(e)
    }
}

function adjMenuClose() {
    // close adjustment menu
    let menu = document.getElementById("adj-menu");
    let bar = document.getElementById("toolbar");
    // hide menu
    menu.style.display = "none";
    // set canvas top to 0
    document.getElementById("canvas").style.top = 0;
    adj_menu_open = false;
}

function adjMenuOpen() {
    // open adjustment menu
    let menu = document.getElementById("adj-menu");
    let bar = document.getElementById("toolbar");
    let canvas = document.getElementById("canvas");
    // show menu
    menu.style.display = "initial";
    // set top of menu
    menu.style.top = bar.offsetTop + bar.offsetHeight;
    // move canvas down
    canvas.style.top = menu.offsetHeight;
    adj_menu_open = true;
}

function adjMenuClick() {
    // checks toggle and runs appropriate function
    if (adj_menu_open) {
        adjMenuClose();
    } else {
        adjMenuOpen();
    }
}


function cancelCrop() {
    // hides crop box and changes cancel on crop tool to crop

    // hide confirm button
    document.getElementById("crop-confirm").style.transform = "scale(0)";

    let box = document.getElementById("crop-box");

    // reset box dimensions and position
    box.style.left = 0;
    box.style.top = 0;
    box.style.height = 0;
    box.style.width = 0;
    box.style.opacity = 0;

    // turn crop mode back to false
    crop_mode = false;

    let text = document.getElementById("crop-text")

    // change crop text back to 'Crop' and white
    text.innerHTML = "Crop";
    text.style.color = "white";
}

function selectCrop() {
    // called by crop tool on click

    // if not currently cropping
    if (!crop_mode) {
        // show crop box
        document.getElementById("crop-confirm").style.transform = "scale(1)";
        crop_mode = true;
        let text = document.getElementById("crop-text")
        // crop text changes to 'Cancel' and colour red
        text.innerHTML = "Cancel";
        text.style.color = "red";
    // if currently cropping, cancel
    } else {
        cancelCrop();
    }
}

document.getElementById("canvas").addEventListener("click", canvasClick);
document.getElementById("canvas").addEventListener("wheel", function(e) {
    // (un)zoom on mouse wheel scroll
    e.preventDefault();
    if (e.deltaY < 0) {
        zoom();
    } else {
        zoomOut();
    }
});

function updateMenuVal(elName, input) {
    // runs on slider input value change
    val = -50 + Number(input.value)
    if (val > 0) {
        val = "+" + String(val)
    }
    // update value text with val
    document.getElementById(elName).innerHTML = val;
}
