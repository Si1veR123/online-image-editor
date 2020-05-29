function setSize(ignoreLarger, resetCenterPos) {
    let img = document.getElementById("image");
    let canvas = document.getElementById("canvas");
    // im ratio
    let ratio = img.naturalWidth / img.naturalHeight;
    // ignore larger means whether to set size even if image is larger than canvas
    // if ignore larger is false or image is smaller than canvas
    if (!ignoreLarger || (img.offsetHeight < canvas.offsetHeight && img.offsetWidth < canvas.offsetWidth)) {
        if (canvas.offsetWidth - img.offsetWidth < canvas.offsetHeight - img.offsetHeight) { // extend to width
            var extraWidth = canvas.offsetWidth - img.offsetWidth; // width to add
            img.width = img.offsetWidth + extraWidth; // add width
            img.height = img.offsetWidth / ratio; // add the correct height calculated with ratio
        } else { // extend to height
            var extraHeight = canvas.offsetHeight - img.offsetHeight; // height to add
            img.height = img.offsetHeight + extraHeight;
            img.width = img.offsetHeight * ratio; // add the correct width calculated with ratio
        }

        if (resetCenterPos) {
            resetCenter() // reset center if resetCenterPos is true
        }

        centerImage() // center image to anchor point
    }
}
