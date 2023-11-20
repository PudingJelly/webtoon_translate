// window.onload = function() {
//     var PSD = require('psd');
//     document.getElementById('fileInput').addEventListener('change', function (e) {
//         var file = e.target.files[0];
//         console.log('업로드된 파일: ', file);
//         var reader = new FileReader();
//         reader.onload = function (event) {
//             // PSD 객체 생성
//             PSD.fromFile(file).then(function (psd) {
//                 // PSD 파일 로드 완료 후 처리할 내용
//                 var textLayers = psd.tree().descendants().filter(layer => layer.isText());
//                 textLayers.forEach(function (textLayer) {
//                     console.log('텍스트 내용:', textLayer.text.value);
//                     console.log('텍스트 레이어 좌표:', textLayer.get('left'), textLayer.get('top'));
//                     // 여기서 텍스트 레이어의 정보를 사용하여 추가적인 작업 수행 가능
//                 });
//             }).catch(function (err) {
//                 // PSD 파일 로드 중 오류 발생 시 처리
//                 console.error('PSD 파일을 로드하는 중 오류가 발생했습니다:', err);
//             });
//         };
//         reader.readAsArrayBuffer(file);
//     });
// };

import PSD from "psd";

window.onload = function() {
    document.getElementById('fileInput').addEventListener('change', function(event) {
        var file = event.target.files[0];
        if(file) {
            var psd = new PSD();

            psd.parse(file).then(function() {
                var textLayers = [];
                var groupLayers = [];
                var tree = psd.tree();
                tree.descendants().forEach(function(node) {
                    if(node.isGroup()) {
                        groupLayers.push(node);
                    } else if (node.layer && node.layer.text) {
                        textLayers.push(node.layer.text.value);
                    }
                });
                console.log("Text Layeres: ", textLayers);
                console.log("Group Layeres: ", groupLayers);
            })
        }
    })
}