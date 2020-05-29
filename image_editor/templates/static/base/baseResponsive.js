function responsive() {
    // ELEMENTS
    let navButton = document.getElementById("navbutton");
    let navMenuSvgs = document.getElementsByClassName("navbuttonsvg");
    let navbar = document.getElementById("navbar-container");
    let navbarMenu = document.getElementById("navbar-menu");

    let navButtonAvailHeight = parseFloat(navbar.offsetHeight) * 0.5;
    let navButtonRectHeight = navButtonAvailHeight / 5;
    // iterate over menuSvg (3 lines)
    for (let i = 0; i < navMenuSvgs.length; i++) {
        if (i > 0) {
            // set padding top on bottom 2
            navMenuSvgs[i].style.paddingTop = navButtonRectHeight * 1.75 + "px"
        }
        // set height to the calculated halved
        navMenuSvgs[i].style.height = navButtonRectHeight * 0.5 + "px";
    }
    // set width to height * 1.32 (not sure why this value works, but it looks like a cross when animated)
    navButton.style.width = navButton.offsetHeight * 1.32 + "px";

    // set the menu animation sheet width for the middle line, to the width of the menu button
    let animationSheet = document.styleSheets[1];
    animationSheet.cssRules[12].cssRules[1].style.width = parseInt(navButton.style.width) + "px";

    // set width of the navbar menu (home, editor, faq) to 80% of navbar width - navbutton width
    navbarMenu.style.width = navbar.offsetWidth * 0.8 - parseInt(navButton.style.width);
}

// make event listener for resize to run responsive function
window.addEventListener("resize", responsive);
responsive()


window.addEventListener("keyup", function(e) {
    // if enter is pressed and navbutton is hovered, animate it. for accessability
    if (e.keyCode === 13 && document.getElementById("navbuttontab").matches(":focus")) {
        menuPressed()
    }
})
