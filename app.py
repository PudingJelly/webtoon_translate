from io import BytesIO
import os
from flask import Flask, render_template, request, send_file
from googletrans import Translator
from psd_tools import PSDImage
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
translator = Translator()


@app.route("/")
def index():
    return render_template(
        "index.html",
        all_layer_info="",
        all_extracted_info_list="",
        extracted_text_data="",
        translated_text_data="",
    )


@app.route("/extract", methods=["POST"])
def extract_text():
    # HTML에 출력하기 위한 리스트 초기화
    all_layer_info = []
    all_extracted_info_list = []
    extracted_text_data = []
    translated_text_data = []

    try:
        source_files = request.files.getlist("source_file")
        for source_file in source_files:
            source = PSDImage.open(source_file, encoding="cp1252")

            if source:
                all_layer_info = vars(source)  # 레이어의 정보

                # PSD 파일의 이미지 추출
                image = source.compose()

                # 원본 파일 이름 추출
                original_filename = os.path.splitext(source_file.filename)[0]

                # 파일 저장 경로 및 네이밍
                remove_text_save_path = (
                    "C:/Users/remis/Desktop/test-images/remove_text_test/remove_text/"
                )
                remove_text_base_name = f"{original_filename}_remove_text.png"

                translated_text_save_path = "C:/Users/remis/Desktop/test-images/remove_text_test/translated_text/"
                translated_text_base_name = f"{original_filename}_translated_text.png"

                # 텍스트 레이어 추출을 위한 리스트 초기화
                text_layer_info = []

                # 모든 하위 레이어들을 찾아서 텍스트 레이어만 추출
                for layer in source.descendants(include_clip=True):
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
                # 텍스트 레이어 정보 추출
                extracted_info = text_layer_info
                all_extracted_info_list.append(text_layer_info)

                # 이미지 분리를 위한 원본소스 복사
                # remove_text_image = image.copy()
                translated_text_image = image.copy()

                # font_size = 100  # 폰트 크기 설정
                font = ImageFont.truetype("arial.ttf", 90)  # 사용할 폰트와 크기 설정

                # 텍스트 레이어의 좌표, 크기 세분화 추출
                # detail_info =[]
                for layer in extracted_info:
                    name, text, top, left, width, height = (
                        layer["name"],
                        layer["text"],
                        layer["top"],
                        layer["left"],
                        layer["size"][0],
                        layer["size"][1],
                    )
                    extracted_text_data.append(layer["text"])
                    clean_text = text.replace('\r', '\n')
                    print(clean_text)
                    translated_name = translator.translate(
                        clean_text, src="ko", dest="en"
                    ).text
                    print(translated_name)

                    # if remove_text_image:
                    #     white_box = Image.new("RGB", (width, height), color="white")
                    #     remove_text_image.paste(white_box, (left, top))
                    
                    white_box = Image.new("RGB", (width+170, height+80), color="white")
                    draw = ImageDraw.Draw(white_box)
                    draw.text((0, 10), translated_name, fill="black", font=font)
                    translated_text_image.paste(white_box, (left-100, top-50))

                    # 번역내용 화면에 출력
                    # translated_text_data.append(translated_text)

                # 이미지 저장
                # remove_text_image.save(remove_text_save_path + remove_text_base_name)
                translated_text_image.save(
                    translated_text_save_path + translated_text_base_name
                )

    except Exception as e:
        all_layer_info = []
        all_extracted_info_list = f"Error extracting text: {str(e)}"
        extracted_text_data = []
        translated_text_data = []

    return render_template(
        "index.html",
        all_layer_info=all_layer_info,
        all_extracted_info_list=all_extracted_info_list,
        extracted_text_data=extracted_text_data,
        translated_text_data=translated_text_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
