// adds accessability by clicking on file upload if it is hovered and enter is pressed
window.addEventListener("keyup", function(e) {
    if (e.keyCode === 13 && document.getElementById("file-container").matches(":focus")) {
        document.getElementById("uploadfile").click()
    }
})