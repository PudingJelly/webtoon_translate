from io import BytesIO
import os
from flask import Flask, render_template, request, send_file
from googletrans import Translator
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageChops

app = Flask(__name__)
translator = Translator()


@app.route("/")
def index():
    return render_template(
        "index.html",
        tranlated_text="",
        all_layer_info="",
        extracted_info="",
        extracted_text="",
        # lower_layer_info="",
        # lower_lower_layer_info="",
        # lower_lower_lower_layer_info="",
    )


@app.route("/translate", methods=["POST"])
def translate():
    text = request.form["text"]
    target_language = request.form["target_language"]
    default_language = request.form["default_language"]
    extracted_text_data = request.form.getlist("extracted_text_data")

    if default_language == "":
        translated_text = translator.translate(text, dest=target_language).text
    else:
        translated_text = translator.translate(
            text, src=default_language, dest=target_language
        ).text

    return render_template(
        "index.html",
        translated_text=translated_text,
        extracted_text_data=extracted_text_data,
    )


@app.route("/extract", methods=["POST"])
def extract_text():
    # HTML에 출력하기 위한 리스트 초기화
    layer_info = []
    extracted_info = []
    extracted_text_data = []

    try:
        source_files = request.files.getlist("source_file")
        for source_file in source_files:
            source = PSDImage.open(source_file)

            if source:
                layer_info = vars(source)  # 레이어의 정보

                # PSD 파일의 이미지 추출
                image = source.compose()

                # 원본 파일 이름 추출
                original_filename = os.path.splitext(source_file.filename)[0]

                # 파일 저장 경로 및 네이밍
                remove_text_save_path = (
                    "C:/Users/remis/Desktop/test-images/remove_text_test/remove_text/"
                )
                remove_text_base_name = f"{original_filename}_remove_text.png"
                text_save_path = (
                    "C:/Users/remis/Desktop/test-images/remove_text_test/text/"
                )
                text_base_name = f"{original_filename}_text.png"

                # 텍스트 레이어 추출
                layer_info = []
                # 모든 하위 레이어들을 찾아서 텍스트 레이어만 추출
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
                # 텍스트 레이어 정보 추출
                extracted_info = layer_info
                all_extracted_info_list.append(layer_info)

                # 이미지 분리를 위한 원본소스 복사
                remove_text_image = image.copy()
                text_image = image.copy()

                extracted_text_data = []
                text_masks = []
                # 텍스트 레이어의 좌표, 크기 세분화 추출
                for layer in extracted_info:
                    top, left, width, height = (
                        layer["top"],
                        layer["left"],
                        layer["size"][0],
                        layer["size"][1],
                    )

                    if remove_text_image:
                        white_box = Image.new("RGB", (width, height), color="white")
                        remove_text_image.paste(white_box, (left, top))

                    if text_image:
                        mask = Image.new("L", image.size, 0)
                        draw = ImageDraw.Draw(mask)
                        draw.rectangle(
                            [(left, top), (left + width, top + height)], fill=255
                        )
                        text_masks.append(mask)
                    
                    text_image.putalpha(mask)
                    # 텍스트 레이어 데이터
                extracted_text_data.append(layer["name"])

                # 이미지 저장
                remove_text_image.save(remove_text_save_path + remove_text_base_name)
                text_image.save(text_save_path + text_base_name)

                all_layer_info_list.append(all_layer_info)

    except Exception as e:
        layer_info = []
        all_extracted_info_list = f"Error extracting text: {str(e)}"
        extracted_text_data = []

    return render_template(
        "index.html",
        layer_info=layer_info,
        all_extracted_info_list=all_extracted_info_list,
        extracted_text_data=extracted_text_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
