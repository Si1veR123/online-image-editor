// underline the given lement

function arrayIncludes(array, item) {
    // check if item is in the given array
    for (let i = 0; i < array.length; i++) {
        if (array[i] === item) {
            return true;
        }
    }
    return false;
}

function underlineElement(el) {
    // set the width rule of animation to the width of el
    let underlineSheet = document.styleSheets[2];
    underlineSheet.cssRules[0].cssRules[1].style.width = el.offsetWidth;

    let left = el.offsetLeft;
    let top = el.offsetTop;

    // create div for the line and set properties
    let underline = document.createElement("div");
    underline.setAttribute("class", "menu-underline");
    underline.style.left = left;
    underline.style.top = top + el.offsetHeight;
    underline.style.width = el.offsetWidth;

    // add underline to DOM
    el.parentNode.appendChild(underline);

    // animate line
    underline.classList.add("underlineAnimation");
}

function undoUnderline(el) {
    // get all underlines
    let underlines = document.getElementsByClassName("menu-underline");

    // iterate over underlines
    for (let i = 0; i < underlines.length; i++) {
        // if line isn't already closing
        if (!arrayIncludes(underlines[i], "closeUnderlineAnimation")) {
            // remove underline animation
            underlines[i].classList.remove("underlineAnimation");
            // add close underline animation
            underlines[i].classList.add("closeUnderlineAnimation");
            // wait for animation to finish, then remove from DOM
            let delay = parseFloat(document.styleSheets[2].cssRules[3].style.animationDuration) * 1000;
            setTimeout(function() {
                underlines[i].parentNode.removeChild(underlines[i])
            }, delay)
            break;
        }
    }
}
