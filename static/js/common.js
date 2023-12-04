window.onload = function () {

    // 초기화 클릭
    // document.getElementById("init").addEventListener("click", e => initailize());
    // function initailize() {
    //     document.getElementById("initialize").submit();
    // }
    $('#init').click(function () {
        $('#initialize').submit();
    });

    // 파일가져오기 클릭
    document.getElementById("upload").addEventListener("click", e => uploadImage());
    function uploadImage() {
        document.getElementById("source_file").click();
    };

    // 파일가져오기 변동이 생길 때
    // 파일 가져오기 취소 시 로딩써클 해제
    document.getElementById("source_file").addEventListener("change", function (e) {
        if(this.files.length === 0) {
            $('loadingOverlay').hide();
        } else {
            document.getElementById("uploadForm").submit();
            $('#loadingOverlay').show();
        }
    });

    // 저장하기
    document.getElementById("download").addEventListener("click", function (e) {
        document.getElementById("downloadForm").submit();
    })

    // 전체 번역하기
    document.getElementById("translate-button").addEventListener("click", e => all_translation());
    function all_translation() {
        document.getElementById("translateForm").submit();
        $('#loadingOverlay').show();
    }

    // 사용자 번역하기
    document.getElementById("modify-button").addEventListener("click", e => user_translation());
    function user_translation() {
        document.getElementById("userTranslation").click();
        $('#loadingOverlay').show();
    }
    document.getElementById("userTranslation").addEventListener("click", e => prepareModifiedTexts());
    function prepareModifiedTexts() {
        // 수정된 텍스트 데이터를 담을 빈 배열
        let modifiedTexts = [];
        let textAreas = document.querySelectorAll(".tr_text_data");

        for (let i = 0; i < textAreas.length; i++) {
            let value = textAreas[i].value.trim(); // 앞뒤 공백 제거
            modifiedTexts.push(value);
        }
        console.log(modifiedTexts);

        sendModifiedTexts(modifiedTexts);
    };

    function sendModifiedTexts(modifiedTexts) {
        console.log("호출22", modifiedTexts);

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
    };

    const originImgContainer = document.querySelector(".toon-image-origin");
    const translatedImgContainer = document.querySelector(".toon-image-translated");

    originImgContainer.addEventListener("scroll", function (e) {
        translatedImgContainer.scrollTop = this.scrollTop;
    });

    translatedImgContainer.addEventListener("scroll", function (e) {
        originImgContainer.scrollTop = this.scrollTop;
    });

    // 파일 업로드 완료 시 로딩써클 해제
    $(document).ajaxStop(function () {
        $('#loadingOverlay').hide(); // 로딩 이미지 숨기기
    });
}