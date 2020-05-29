// javascript to add/remove animations for fading to white/black

function toWhite(el, text) {
    el.classList.remove("toBlackAnimation");
    el.classList.add("toWhiteAnimation");

    text.classList.remove("textToWhiteAnimation");
    text.classList.add("textToBlackAnimation");
}

function toBlack(el, text) {
    el.classList.remove("toWhiteAnimation");
    el.classList.add("toBlackAnimation");

    text.classList.remove("textToBlackAnimation");
    text.classList.add("textToWhiteAnimation");
}
