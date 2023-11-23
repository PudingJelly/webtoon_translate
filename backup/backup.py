@app.route("/extract", methods=["POST"])
def extract_text():
    source_file = request.files["source_file"]
    all_layer_info = []
    extracted_info = []
    extracted_text_data = []

    if source_file:
        try:
            source = PSDImage.open(source_file)
            all_layer_info = vars(source)

            # PSD 파일의 이미지 추출
            image = source.compose()

            # 원본 파일 이름 추출
            original_filename = os.path.splitext(source_file.filename)[0]

            # 파일 저장 경로 및 네이밍
            save_path = "C:/Users/remis/Desktop/test-images/remove_text_test/"
            base_name = f"{original_filename}_remove_text.png"

            # 텍스트 레이어 추출
            layer_info = []
            for layer in source.descendants(include_clip=True):
                if layer.kind == "type":
                    layer_info.append(
                        {
                            "kind": layer.kind,
                            "name": layer.name,
                            "text": layer.text,
                            "top": layer.top,
                            "left": layer.left,
                            "size": layer.size,
                        }
                    )
            extracted_info = layer_info

            text_image = image.copy()
            # mask = Image.new("L", image.size, 0)
            # draw = ImageDraw.Draw(mask)

            # 텍스트 레이어의 정보 추출
            for layer in extracted_info:
                top, left, width, height = (
                    layer["top"],
                    layer["left"],
                    layer["size"][0],
                    layer["size"][1],
                )
                # draw.rectangle([(left, top), (left + width, top + height)], fill=255)
                white_box = Image.new("RGB", (width, height), color="white")
                image.paste(white_box, (left, top))

            # 마스크를 이미지에 적용하여 텍스트가 있는 부분만 투명하게 만듦
            # text_image.putalpha(mask)

            # 이미지 저장
            image.save(save_path + base_name)

            # 텍스트 레이어 데이터
            extracted_text_data.append(
                layer["text"],
            )

        except Exception as e:
            extracted_info = f"Error extracting text: {str(e)}"
            extracted_text_data = []

    return render_template(
        "index.html",
        all_layer_info=all_layer_info,
        extracted_info=extracted_info,
        extracted_text_data=extracted_text_data,
    )
    
    
@app.route("/extract", methods=["POST"])
def extract_text():
    source_file = request.files["source_file"]
    all_layer_info = []
    extracted_info = []
    extracted_text_data = []

    if source_file:
        try:
            source = PSDImage.open(source_file)
            all_layer_info = vars(source)

            # PSD 파일의 이미지 추출
            # image = source.compose()

            # 원본 파일 이름 추출
            original_filename = os.path.splitext(source_file.filename)[0]

            # 파일 저장 경로 및 네이밍
            remove_text_save_path1 = "C:/Users/remis/Desktop/test-images/remove_text_test/"
            remove_text_base_name1 = f"{original_filename}_remove_text.png"
            text_save_path2 = "C:/Users/remis/Desktop/test-images/remove_text_test/"
            text_base_name2 = f"{original_filename}_text_image.png"

            # 텍스트 레이어 추출
            layer_info = []
            for layer in source.descendants(include_clip=True):
                if layer.kind == "type":
                    layer_info.append(
                        {
                            "kind": layer.kind,
                            "name": layer.name,
                            "text": layer.text,
                            "top": layer.top,
                            "left": layer.left,
                            "width": layer.width,
                            "height": layer.height,
                        }
                    )
            extracted_info = layer_info

            text_image = source.copy()
            text_remove_image = source.copy()
            # mask = Image.new("L", image.size, 0)
            draw = ImageDraw.Draw(text_image)

            # 텍스트 레이어의 정보 추출
            for layer in extracted_info:
                top, left, width, height = (
                    layer["top"],
                    layer["left"],
                    layer["width"],
                    layer["height"],
                )
                white_box = Image.new("RGB", (width, height), color="white")
                text_remove_image.paste(white_box, (left, top))
                draw.rectangle([(left, top), (left + width, top + height)], fill=255)

                # 텍스트 레이어 데이터
                extracted_text_data.append(
                    layer["text"],
                )

            text_image.save(os.path.join(save_path2 + base_name2))
            text_remove_image.save(os.path.join(save_path1 + base_name1))

            # 이미지 저장
            # image.save(save_path + base_name)

        except Exception as e:
            extracted_info = f"Error extracting text: {str(e)}"
            extracted_text_data = []

    return render_template(
        "index.html",
        all_layer_info=all_layer_info,
        extracted_info=extracted_info,
        extracted_text_data=extracted_text_data,
    )
