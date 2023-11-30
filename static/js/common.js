window.onload = function () {

    document.querySelector("#source_file").addEventListener("change", e => submitForm());
    function submitForm() {
        document.querySelector("#uploadForm").submit();
    }

    document.querySelector("#userTranslation").addEventListener("click", e => prepareModifiedTexts())

    function prepareModifiedTexts() {
        // 수정된 텍스트 데이터를 담을 빈 배열
        let modifiedTexts = [];
        let textAreas = document.querySelectorAll(".tr_text_data");

        for (let i = 0; i < textAreas.length; i++) {
            let value = textAreas[i].value.trim(); // 앞뒤 공백 제거
            modifiedTexts.push(value);
        }

        sendModifiedTexts(modifiedTexts);
    }

    function sendModifiedTexts(modifiedTexts) {
        let form = document.createElement('form');
        form.setAttribute('method', 'post');
        form.setAttribute('action', '/user_translation');
        form.setAttribute('enctype', 'multipart/form-data');

        // 수정된 텍스트 데이터를 폼으로 추가
        for (let i = 0; i < modifiedTexts.length; i++) {
            let input = document.createElement('input');
            input.setAttribute('type', 'hidden');
            input.setAttribute('name', `modified_text`);
            input.setAttribute('value', modifiedTexts[i]);
            form.appendChild(input);
        }

        // 폼을 현재 페이지에 추가하고 전송
        document.body.appendChild(form);
        form.submit();
    }
}