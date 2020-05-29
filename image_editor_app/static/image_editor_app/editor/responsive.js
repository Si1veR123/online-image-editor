function responsive() {
    // set image size
    setSize();
    // move crop confirm container to bottom of canvas
    let container = document.getElementById("crop-confirm-container");
    container.style.top = document.getElementById("canvas").offsetTop + document.getElementById("canvas").offsetHeight - container.offsetHeight / 2;
}

window.addEventListener("resize", responsive);
responsive()
