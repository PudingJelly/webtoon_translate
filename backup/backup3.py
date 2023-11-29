@app.route("/upload", methods=["POST"])
def upload_file():
    # HTML에 출력하기 위한 리스트 초기화
    all_layer_info = []
    text_layer_info = []
    extracted_text_data = []
    translated_text_data = []

    try:
        source_file = request.files["source_file"]
        # session["source_file"] = source_file
        target_language = request.form.get("target_language")
        font = ImageFont.truetype("arial.ttf", 70)  # 사용할 폰트와 크기 설정

        if source_file:
            source = PSDImage.open(source_file)

            # PSD 파일의 이미지 추출
            image = source.compose()
            # session['image'] = image
            # 원본 파일 이름 추출
            original_filename = os.path.splitext(source_file.filename)[0]
            session["original_filename"] = original_filename
            # 원본 png 변환 후 저장
            converted_image_path = (
                f"static/images/original-converted/{original_filename}.png"
            )
            image.save(converted_image_path)

            # 모든 하위 레이어들을 찾아서 텍스트 레이어만 추출
            for layer in source.descendants(include_clip=True):
                all_layer_info.append(
                    {
                        "kind": layer.kind,
                        "name": layer.name,
                        "top": layer.top,
                        "left": layer.left,
                        "size": layer.size,
                    }
                )
                # all_layer_info.append(sub_layer)
                if layer.kind == "type":
                    text_layer_info.append(
                        {
                            "kind": layer.kind,
                            "name": layer.name,
                            "text": layer.text,
                            "top": layer.top,
                            "left": layer.left,
                            "size": layer.size,
                        }
                    )
            # 이미지 분리를 위한 원본소스 복사
            remove_text_image = image.copy()
            # translated_text_image = image.copy()
            # 텍스트 레이어의 좌표, 크기 세분화 추출
            for layer in text_layer_info:
                name, text, top, left, width, height = (
                    layer["name"],
                    layer["text"],
                    layer["top"],
                    layer["left"],
                    layer["size"][0],
                    layer["size"][1],
                )
                extracted_text_data.append(text)
                # print(len(extracted_text_data))

                # 텍스트 특수 기호 처리 및 번역
                clean_text = text.replace("\r", "\n")
                translated_text = translator.translate(
                    clean_text, dest=target_language
                ).text
                translated_text_data.append(translated_text)

            # 텍스트 제거
            for layer in text_layer_info:
                name, text, top, left, width, height = (
                    layer["name"],
                    layer["text"],
                    layer["top"],
                    layer["left"],
                    layer["size"][0],
                    layer["size"][1],
                )

                white_box = Image.new("RGB", (width, height), color="white")
                remove_text_image.paste(white_box, (left, top))

            # 텍스트제거 이미지 저장
            remove_text_save_path = (
                f"static/images/remove-text/{original_filename}_remove_text.png"
            )
            remove_text_image.save(remove_text_save_path)

            # 텍스트제거 이미지에 번역텍스트 삽입
            for layer, translated_text in zip(text_layer_info, translated_text_data):
                name, text, top, left, width, height = (
                    layer["name"],
                    layer["text"],
                    layer["top"],
                    layer["left"],
                    layer["size"][0],
                    layer["size"][1],
                )

                # 말풍선 지우고 번역하여 채우기
                text_box = Image.new(
                    "RGBA", (width + 1000, height + 100), (255, 255, 255, 0)
                )
                draw = ImageDraw.Draw(text_box)
                draw.text((0, 0), translated_text, fill="black", font=font)
                remove_text_image.paste(text_box, (left, top), mask=text_box)

            # 번역 이미지 저장
            translated_text_save_path = (
                f"static/images/translated-text/{target_language}/"
            )
            translated_text_base_name = f"{original_filename}_{target_language}.png"

            # 경로내에 폴더가 없을 경우 폴더 생성
            if not os.path.exists(translated_text_save_path):
                os.mkdir(translated_text_save_path)

            translated_image_path = (
                translated_text_save_path + translated_text_base_name
            )
            remove_text_image.save(translated_image_path)

            # 세션에 번역이미지 경로 저장
            session["translated_image_path"] = translated_image_path

            return render_template(
                "index.html",
                image_data=converted_image_path,
                translated_text_image_data=translated_image_path,
                all_layer_info=all_layer_info,
                text_layer_info=text_layer_info,
                extracted_text_data=extracted_text_data,
                translated_text_data=translated_text_data,
            )

    except Exception as e:
        return render_template(
            "index.html",
            image_data=None,
            translated_text_image_data=None,
            all_layer_info=f"Error extracting text: {str(e)}",
            text_layer_info=[],
            extracted_text_data=[],
            translated_text_data=[],
        )