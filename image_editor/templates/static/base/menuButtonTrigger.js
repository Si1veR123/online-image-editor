// adds and removes css animation classes for the menu animation

let buttonPressed = false;

// toggle pressed
function menuPressed() {
    if (buttonPressed) {
        buttonPressed = false;
        returnAnimation()
    } else {
        buttonPressed = true;
        activateAnimation()
    }
}

function activateAnimation() {
    let navButtonChildren = document.getElementById("navbutton").childNodes;
    navButtonChildren[3].classList.remove("closeTopMenuAnimation");
    navButtonChildren[5].classList.remove("closeMiddleMenuAnimation");
    navButtonChildren[7].classList.remove("closeBottomMenuAnimation");

    navButtonChildren[3].classList.add("topMenuAnimation");
    navButtonChildren[5].classList.add("middleMenuAnimation");
    navButtonChildren[7].classList.add("bottomMenuAnimation");

    let navbarMenu = document.getElementById("navbar-menu");
    navbarMenu.classList.remove("closeMenuOptionsAnimation");
    navbarMenu.classList.add("menuOptionsAnimation");

    // on animation, change tab index of menu elements, so that they can be tabbed to. They are removed when closed to stop being able to tab to the elements off screen
    for (let i = 0; i < navbarMenu.childNodes.length; i++) {
        let current = navbarMenu.childNodes[i];
        try {
            current.setAttribute("tabindex", i);
        } catch (TypeError) {}
    }

    let logo = document.getElementById("navbar-logo");
    logo.classList.remove("closeLogoAnimation");
    logo.classList.add("logoAnimation");
}

function returnAnimation() {
    let navButtonChildren = document.getElementById("navbutton").childNodes;
    navButtonChildren[3].classList.remove("topMenuAnimation");
    navButtonChildren[5].classList.remove("middleMenuAnimation");
    navButtonChildren[7].classList.remove("bottomMenuAnimation");

    navButtonChildren[3].classList.add("closeTopMenuAnimation");
    navButtonChildren[5].classList.add("closeMiddleMenuAnimation");
    navButtonChildren[7].classList.add("closeBottomMenuAnimation");

    let navbarMenu = document.getElementById("navbar-menu");
    navbarMenu.classList.remove("menuOptionsAnimation");
    navbarMenu.classList.add("closeMenuOptionsAnimation");

    // on animation, change tab index of menu elements, so that they can't be tabbed to. They are added when opened to allow being able to tab to the elements
    for (let i = 0; i < navbarMenu.childNodes.length; i++) {
        let current = navbarMenu.childNodes[i];
        try {
            current.setAttribute("tabindex", "-1");
        } catch (TypeError) {}
    }

    let logo = document.getElementById("navbar-logo");
    logo.classList.remove("logoAnimation");
    logo.classList.add("closeLogoAnimation");
}