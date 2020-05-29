function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function switchScreen(now, force=false) {
    // switch between info and editor
    // now is current screen (editor or info)
    // if force is on, don't check if cookie (set when info has been viewed) is there
    let editor = document.getElementById("editor");
    let info = document.getElementById("info");

    // if cookie doesn't exist (user hasn't seen help page) or force = true
    if (!getCookie("dmlld2Vk") || force) {
        // switch to info
        if (now === editor) {
            editor.style.display = "none";
            info.style.display = "initial";
        // switch to editor
        } else if (now === info) {
            editor.style.display = "initial";
            info.style.display = "none";
        }
        setCookie("dmlld2Vk", "1", 1)
    // cookie does exist (user has seen info), show editor
    } else {
        editor.style.display = "initial";
        info.style.display = "none";
    }
}
