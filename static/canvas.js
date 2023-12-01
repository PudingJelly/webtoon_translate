var canvas = document.getElementById("myCanvas");
var ctx = canvas.getContext("2d");
clear();
// 검은색 사각형 그리기

// 마우스 클릭 확인
var dx = canvas.offsetLeft;
var dy = canvas.offsetTop;
var onoff = false;
var oldx = -dx;
var oldy = -dy;

// 브러쉬 색상 설정
var linecolor = "black";
// 선 굵기 설정
var linw = 4;

var dir;

function IsPC() {
    var userAgentInfo = navigator.userAgent;
    var Agents = ["Android", "iPhone",
        "SymbianOS", "Windows Phone",
        "iPad", "iPod"];
    var flag = true;
    for (var v = 0; v < Agents.length; v++) {
        if (userAgentInfo.indexOf(Agents[v]) > 0) {
            flag = false;
            break;
        }
    }
    return flag;
}

if (IsPC()) {
    canvas.addEventListener("mousemove", draw, true);
    canvas.addEventListener("mousedown", down, false);
    canvas.addEventListener("mouseup", up, false);
} else {
    canvas.addEventListener("touchmove", touch, true);
    canvas.addEventListener("touchend", touch, false);
    canvas.addEventListener("touchstart", touch, false);
}

function touch(event) {
    var event = event || window.event;
    switch (event.type) {
        case "touchstart":
            onoff = true;
            // 마우스가 눌린 위치를 기록하고 선 그리기의 시작 좌표로 설정
            oldx = event.touches[0].clientX - dx;
            oldy = event.touches[0].clientY - dy;
            break;
        case "touchend":
            onoff = false;
            var oldx = -dx;
            var oldy = -dy;
            cPush();
            break;
        case "touchmove":
            if (true == onoff) {
                var newx = event.touches[0].clientX - dx;
                var newy = event.touches[0].clientY - dy;
                ctx.beginPath();
                // 선 그리기의 시작점 설정
                ctx.moveTo(oldx, oldy);
                // 선 그리기의 끝점 설정
                ctx.lineTo(newx, newy);
                // 브러쉬 색상 설정
                ctx.strokeStyle = linecolor;
                // 브러쉬 굵기 설정
                ctx.lineWidth = linw;
                // 펜 캡 설정
                ctx.lineCap = "round";
                // 선 그리기 완료
                ctx.stroke();
                // 다음 선 그리기의 시작 좌표로 설정
                oldx = newx;
                oldy = newy;
            }
            break;
    }

}

function clear() {
    canvas.height = canvas.height;
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, 512, 512);
}

// Canvas redo & undo
var cPushArray = new Array();
var cStep = -1;

function cPush() {
    cStep++;
    if (cStep < cPushArray.length) { cPushArray.length = cStep; }
    cPushArray.push(canvas.toDataURL());
}

cPush();
function cUndo() {
    if (cStep > 0) {
        cStep--;
        var canvasPic = new Image();
        canvasPic.src = cPushArray[cStep];
        canvasPic.onload = function () {
            clear();
            ctx.drawImage(canvasPic, 0, 0);
        }
    }
}

function cRedo() {
    if (cStep < cPushArray.length - 1) {
        cStep++;
        var canvasPic = new Image();
        canvasPic.src = cPushArray[cStep];
        canvasPic.onload = function () {
            clear();
            ctx.drawImage(canvasPic, 0, 0);
        }
    }
}

function down(event) {
    onoff = true;
    oldx = event.pageX - dx;
    oldy = event.pageY - dy;
}

function up(event) {
    onoff = false;
    var oldx = -dx;
    var oldy = -dy;
    cPush();
}

function draw(event) {
    if (true == onoff) {
        var newx = event.pageX - dx;
        var newy = event.pageY - dy;
        ctx.beginPath();
        ctx.moveTo(oldx, oldy);
        ctx.lineTo(newx, newy);
        ctx.strokeStyle = linecolor;
        ctx.lineWidth = linw;
        ctx.lineCap = "round";
        ctx.stroke();
        oldx = newx;
        oldy = newy;
    }
}

// Canvas 초기화
function cInit() {
    var img = new Image();
    img.crossOrigin = "*";
    var num = Math.random() * 4 + 1;
    num = parseInt(num, 10);
    img.src = "static/init/i" + num + ".jpg";
    img.onload = function () {
        clear();
        ctx.drawImage(img, 0, 0);
    }
}

// Canvas 리셋
function cReset() {
    clear();
}

// 파일 가져오기
$("#import").click(function () {
    $("#files").click();
});

function resize(maxWidth, maxHeight, width, height) {
    var param = {
        width: width,
        height: height
    };
    if (width > maxWidth || height > maxHeight) {
        rateWidth = width / maxWidth;
        rateHeight = height / maxHeight;
        if (rateWidth > rateHeight) {
            param.width = maxWidth;
            param.height = Math.round(height / rateWidth);
        } else {
            param.width = Math.round(width / rateHeight);
            param.height = maxHeight;
        }
    }
    return param;
}

function selectImage() {
    var img = new Image();
    var reader = new FileReader();
    reader.onload = function () {
        img.src = this.result;
    }
    reader.readAsDataURL($('#files').prop('files')[0]);
    img.onload = function () {
        var height = img.height;
        var width = img.width;
        var new_height, new_width;
        if (height > width) {
            if (height > 512) {
                new_height = 512;
                new_width = 512 * width / height;
            } else {
                new_height = height;
                new_width = width;
            }
        } else {
            if (width > 512) {
                new_width = 512;
                new_height = 512 * height / width;
            } else {
                new_height = height;
                new_width = width;
            }
        }
        clear();
        ctx.drawImage(img, (512 - new_width) / 2, (512 - new_height) / 2, new_width, new_height);
    }
}

// 스케치 효과
function cSketchify() {
    $.ajax({
        type: "POST",
        url: "/sketchify",
        // async: false,
        data: {
            image: canvas.toDataURL("image/png").substring(22)
        },
        dataType: "json",
        success: function (data) {
            var img = new Image();
            img.src = data['image1'];
            img.onload = function () {
                clear();
                ctx.drawImage(img, 0, 0);
            }
        },
        error: function (htp, s, e) {
            alert("정보를 가져오는 데 실패했습니다. 페이지를 새로 고침해주세요");
        }
    });

}

// 변형
function transformWithoutColor(event) {
    $.ajax({
        type: "POST",
        url: "/trans1",
        // async: false,
        data: {
            image: canvas.toDataURL("image/png").substring(22)
        },
        dataType: "json",
        success: function (data) {
            $('#imgResult').attr('src', data['image2']);
        },
        error: function (htp, s, e) {
            console.log(htp)
            console.log(s)
            console.log(e)
            alert("정보를 가져오는 데 실패했습니다. 페이지를 새로 고침해주세요");
        }
    });
}

function transformWithColor(event) {
    $.ajax({
        type: "POST",
        url: "/trans2",
        // async: false,
        data: {
            image: canvas.toDataURL("image/png").substring(22)
        },
        dataType: "json",
        success: function (data) {
            $('#imgResult').attr('src', data['image2']);
        },
        error: function (htp, s, e) {
            alert("정보를 가져오는 데 실패했습니다. 페이지를 새로 고침해주세요");
        }
    });
}

function transformCartoon(event) {
    $.ajax({
        type: "POST",
        url: "/trans3",
        // async: false,
        data: {
            image: canvas.toDataURL("image/png").substring(22)
        },
        dataType: "json",
        success: function (data) {
            $('#imgResult').attr('src', data['image2']);
        },
        error: function (htp, s, e) {
            alert("정보를 가져오는 데 실패했습니다. 페이지를 새로 고침해주세요");
        }
    });
}

// 알 수 없는 기능

function updateBorders(color) {
    var hexColor = "transparent";
    if (color) {
        hexColor = color.toHexString();
    }
    linecolor = hexColor;
}

$(function () {

    $("#full").spectrum({
        allowEmpty: true,
        color: "#ECC",
        showInput: true,
        containerClassName: "full-spectrum",
        showInitial: true,
        showPalette: true,
        showSelectionPalette: true,
        showAlpha: true,
        maxPaletteSize: 10,
        preferredFormat: "hex",
        localStorageKey: "spectrum.demo",
        move: function (color) {
            updateBorders(color);
        },
        show: function () {

        },
        beforeShow: function () {

        },
        hide: function (color) {
            updateBorders(color);
        },

        palette: [
            ["rgb(0, 0, 0)", "rgb(67, 67, 67)", "rgb(102, 102, 102)", /*"rgb(153, 153, 153)","rgb(183, 183, 183)",*/
                "rgb(204, 204, 204)", "rgb(217, 217, 217)", /*"rgb(239, 239, 239)", "rgb(243, 243, 243)",*/ "rgb(255, 255, 255)"],
            ["rgb(152, 0, 0)", "rgb(255, 0, 0)", "rgb(255, 153, 0)", "rgb(255, 255, 0)", "rgb(0, 255, 0)",
                "rgb(0, 255, 255)", "rgb(74, 134, 232)", "rgb(0, 0, 255)", "rgb(153, 0, 255)", "rgb(255, 0, 255)"],
            ["rgb(230, 184, 175)", "rgb(244, 204, 204)", "rgb(252, 229, 205)", "rgb(255, 242, 204)", "rgb(217, 234, 211)",
                "rgb(208, 224, 227)", "rgb(201, 218, 248)", "rgb(207, 226, 243)", "rgb(217, 210, 233)", "rgb(234, 209, 220)",
                "rgb(221, 126, 107)", "rgb(234, 153, 153)", "rgb(249, 203, 156)", "rgb(255, 229, 153)", "rgb(182, 215, 168)",
                "rgb(162, 196, 201)", "rgb(164, 194, 244)", "rgb(159, 197, 232)", "rgb(180, 167, 214)", "rgb(213, 166, 189)",
                "rgb(204, 65, 37)", "rgb(224, 102, 102)", "rgb(246, 178, 107)", "rgb(255, 217, 102)", "rgb(147, 196, 125)",
                "rgb(118, 165, 175)", "rgb(109, 158, 235)", "rgb(111, 168, 220)", "rgb(142, 124, 195)", "rgb(194, 123, 160)",
                "rgb(166, 28, 0)", "rgb(204, 0, 0)", "rgb(230, 145, 56)", "rgb(241, 194, 50)", "rgb(106, 168, 79)",
                "rgb(69, 129, 142)", "rgb(60, 120, 216)", "rgb(61, 133, 198)", "rgb(103, 78, 167)", "rgb(166, 77, 121)",
                /*"rgb(133, 32, 12)", "rgb(153, 0, 0)", "rgb(180, 95, 6)", "rgb(191, 144, 0)", "rgb(56, 118, 29)",
                "rgb(19, 79, 92)", "rgb(17, 85, 204)", "rgb(11, 83, 148)", "rgb(53, 28, 117)", "rgb(116, 27, 71)",*/
                "rgb(91, 15, 0)", "rgb(102, 0, 0)", "rgb(120, 63, 4)", "rgb(127, 96, 0)", "rgb(39, 78, 19)",
                "rgb(12, 52, 61)", "rgb(28, 69, 135)", "rgb(7, 55, 99)", "rgb(32, 18, 77)", "rgb(76, 17, 48)"]
        ]
    });

});
