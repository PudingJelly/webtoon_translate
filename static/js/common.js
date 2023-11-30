window.onload = function () {

    function submitForm() {
        document.getElementById("uploadForm").submit();
    }
    document.getElementById("source_file").addEventListener("change", e => submitForm());
    
    function prepareModifiedTexts() {
        // 수정된 텍스트 데이터를 담을 빈 배열
        let modifiedTexts = [];
    
        // 모든 textarea에서 수정된 내용을 가져와서 배열에 추가
        let textAreas = document.querySelectorAll("tr_text_data");
        for (let i = 0; i < textAreas.length; i++) {
            modifiedTexts.push(textAreas[i].textContent);
        }

        document.getElementById("modifiedTexts").textContent = modifiedTexts.join("\n");
    
        // JSON.stringify()를 사용하여 데이터를 JSON 형식의 문자열로 변환
        document.getElementById("userTranslationForm").submit();
    }

    document.getElementById("userTranslation").addEventListener("click", e => prepareModifiedTexts)
    
}

