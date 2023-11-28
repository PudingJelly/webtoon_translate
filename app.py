from io import BytesIO
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, request, session
from googletrans import Translator
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.secret_key = "webtoontest"
translator = Translator()


@app.route("/")
def index():
    session.clear()
    return render_template(
        "index.html",
        image_data=None,
        translated_text_image_data=None,
        all_layer_info="",
        all_extracted_info_list="",
        extracted_text_data="",
        translated_text_data="",
    )


@app.route("/upload", methods=["POST"])
def upload_file():
    # HTML에 출력하기 위한 리스트 초기화
    all_layer_info = []
    text_layer_info = []
    extracted_text_data = []
    translated_text_data = []

    try:
        source_file = request.files["source_file"]
        target_language = request.form.get("target_language")
        font = ImageFont.truetype("arial.ttf", 70)  # 사용할 폰트와 크기 설정

        if source_file:
            source = PSDImage.open(source_file)

            # PSD 파일의 이미지 추출
            image = source.compose()
            # 원본 파일 이름 추출
            original_filename = os.path.splitext(source_file.filename)[0]
            # 원본 png 변환 후 저장
            converted_image_path = (
                f"static/images/original-converted/{original_filename}.png"
            )
            image.save(converted_image_path)

            # 모든 하위 레이어들을 찾아서 텍스트 레이어만 추출
            for layer in source.descendants(include_clip=True):
                all_layer_info.append(layer)
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
            translated_text_image = image.copy()
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
                clean_text = text.replace("\r", "\n")
                translated_text = translator.translate(
                    clean_text, src="ko", dest=target_language
                ).text
                translated_text_data.append(translated_text)

                if remove_text_image:
                    white_box = Image.new("RGB", (width, height), color="white")
                    remove_text_image.paste(white_box, (left, top))

                if translated_text_image:
                    # 말풍선 지우고 번역하여 채우기
                    text_box = Image.new(
                        "RGB", (width + 80, height + 60), color="white"
                    )
                    draw = ImageDraw.Draw(text_box)
                    draw.text((0, 0), translated_text, fill="black", font=font)
                    translated_text_image.paste(text_box, (left - 40, top - 10))

            # 프로젝트 내 이미지 저장경로
            remove_text_save_path = (
                f"static/images/remove-text/{original_filename}_remove_text.png"
            )
            remove_text_image.save(remove_text_save_path)
            translated_text_save_path = (
                f"static/images/translated-text/{target_language}/"
            )
            translated_text_base_name = f"{original_filename}_{target_language}.png"
            if not os.path.exists(translated_text_save_path):
                os.mkdir(translated_text_save_path)
            translated_image = translated_text_save_path + translated_text_base_name
            translated_text_image.save(translated_image)

            return render_template(
                "index.html",
                image_data=converted_image_path,
                translated_text_image_data=translated_image,
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


if __name__ == "__main__":
    app.run(debug=True)
