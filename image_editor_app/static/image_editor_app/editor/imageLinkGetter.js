// gets link for image

function updateImage() {
     let im = document.getElementById("image");
     let download = document.getElementById("download");

     let link = "/image?" + (new Date).getMilliseconds()
     im.setAttribute("src", link);
     // set new link for download
     download.setAttribute("href", link);
     // on load, center and fit to screen, run switchScreen
     im.onload = function() {
        setSize(false, true);
        switchScreen(document.getElementById("editor"))
        };
}

updateImage()
