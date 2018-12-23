$(document).ready(function () {
    let ctx = $("#map").get(0).getContext('2d');
    for (let x in mapData) {
        let data = mapData[x];
        ctx.fillStyle = data.county;
        ctx.fillRect(data.x, data.y, 1, 1);
    }
});

function setPixel(ctx) {
    let imgdata = ctx.getImageData(0, 0, 640, 480);
    let imgdatalen = imgdata.data.length;
    ctx.putImageData(imgdata, 0, 0);
    for (let i = 0; i < imgdatalen / 4; i++) {  //iterate over every pixel in the canvas
        imgdata.data[4 * i] = 255;    // RED (0-255)
        imgdata.data[4 * i + 1] = 0;    // GREEN (0-255)
        imgdata.data[4 * i + 2] = 0;    // BLUE (0-255)
        imgdata.data[4 * i + 3] = 255;  // APLHA (0-255)
    }
    ctx.putImageData(imgdata, 0, 0);
}