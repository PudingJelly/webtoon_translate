window.onload = function () {

    // 초기화 클릭
    $("#init").click(function () {
        $("#initialize").submit();
    });

    // 파일가져오기 클릭
    $("#upload").click(function () {
        $("#source_file").click();
    });

    // 파일가져오기 변동이 생길 때
    // 파일 가져오기 취소 시 로딩써클 해제
    $("#source_file").change(function (e) {
        if (this.files.length === 0) {
            $("#loadingOverlay").hide();
        } else {
            $("#uploadForm").submit();
            $("#loadingOverlay").show();
        }
    });

    // 저장하기
    $("#download").click(function () {
        $("#downloadForm").submit();
    });

    // 전체 번역하기
    $("#translate-button").click(function () {
        $("#translateForm").submit();
        $("#loadingOverlay").show();
    });

    // 사용자 번역하기
    $("#modify-button").click(function () {
        $("#userTranslation").click();
        $("#loadingOverlay").show();
    });

    $("#userTranslation").click(function () {
        prepareModifiedTexts();
    });

    function prepareModifiedTexts() {
        // 수정된 텍스트 데이터를 담을 빈 배열
        let modifiedTexts = [];
        let textAreas = $(".tr_text_data");

        for (let i = 0; i < textAreas.length; i++) {
            let value = textAreas[i].value.trim(); // 앞뒤 공백 제거
            modifiedTexts.push(value);
        }
        sendModifiedTexts(modifiedTexts);
    };

    function sendModifiedTexts(modifiedTexts) {
        let form = $("<form>").attr({ 
            "method": "post", 
            "action": "/user_translation", 
            "enctype": "multipart/form-data" 
        });

        // 수정된 텍스트 데이터를 폼으로 추가
        for (let i = 0; i < modifiedTexts.length; i++) {
            $("<input>").attr({
                "type":"hidden",
                "name":"modified_text",
                "value":modifiedTexts[i]
            }).appendTo(form);
        };
        
        // 폼을 현재 페이지에 추가하고 전송
        $("body").append(form);
        form.submit();
    };

    const originImgContainer = $(".toon-image-origin");
    const translatedImgContainer = $(".toon-image-translated");

    originImgContainer.on("scroll", function() {
        translatedImgContainer.scrollTop = this.scrollTop;
    });

    translatedImgContainer.on("scroll", function() {
        originImgContainer.scrollTop = this.scrollTop;
    });

    // 파일 업로드 완료 시 로딩써클 해제
    $(document).ajaxStop(function () {
        $('#loadingOverlay').hide(); // 로딩 이미지 숨기기
    });
}