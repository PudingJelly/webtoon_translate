import os
import pytesseract
import cv2
from io import BytesIO
from flask import Flask, render_template, request, send_file, redirect, url_for
from googletrans import Translator
from psd_tools import PSDImage

from PIL import Image, ImageDraw, ImageChops

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

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
    )


@app.route("/extract", methods=["POST"])
def extract_text():
    source_files = request.files.getlist("source_file")
    # translator = Translator()

    for source_file in source_files:
        source = PSDImage.open(source_file)

        # psd를 png로 변환하여 저장
        source_png_file = f"uploads/{source_file.filename.split('.')[0]}.png"
        source.compose().save(source_png_file)

        # png 파일 열기
        image = cv2.imread(source_png_file)

        # 이미지 전처리 작업
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # 텍스트와 위치 정보 추출
        # 텍스트와 위치 정보 추출
        text_boxes = pytesseract.image_to_boxes(gray)

        # 추출된 텍스트와 위치에 대해 번역하고 이미지에 삽입
        for b in text_boxes.splitlines():
            b = b.split()
            character = b[0]
            x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
            text = character

            # 텍스트 번역 (예시로 영어로 번역)
            translated_text = translator.translate(text, src="ko", dest="en").text

            # 번역된 텍스트를 이미지에 삽입
            cv2.putText(
                image,
                translated_text,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2,
            )

        # 새로운 파일로 이미지 저장
        save_path = "C:/Users/remis/Desktop/test-images/test/"
        base_name = f"{source_file.filename.split('.')[0]}_translated.png"
        cv2.imwrite(os.path.join(save_path, base_name), image)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
    
    
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
            source = PSDImage.open(source_file)

            if source:
                # all_layer_info = vars(source)  # 레이어의 정보
                all_layer_info = []  # 레이어의 정보

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
                translated_text_base_name = f"{original_filename}_translated_text_en.png"

                # 텍스트 레이어 추출을 위한 리스트 초기화
                text_layer_info = []

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
                # 텍스트 레이어 정보 추출
                extracted_info = text_layer_info
                all_extracted_info_list.append(text_layer_info)

                # 이미지 분리를 위한 원본소스 복사
                remove_text_image = image.copy()
                translated_text_image = image.copy()

                # font_size = 100  # 폰트 크기 설정
                font = ImageFont.truetype("arial.ttf", 70)  # 사용할 폰트와 크기 설정

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
                    extracted_text_data.append(text)
                    clean_text = text.replace('\r', '\n')
                    # print(clean_text)
                    translated_name = translator.translate(
                        clean_text, src="ko", dest="en"
                    ).text
                    # print(translated_name)

                    if remove_text_image:
                        white_box = Image.new("RGB", (width, height), color="white")
                        remove_text_image.paste(white_box, (left, top))

                    if translated_text_image:
                        # 말풍선 텍스트 지우기
                        # white_box = Image.new("RGB", (width, height), color="white")
                        # translated_text_image.paste(white_box, (left, top))
                        # 말풍선 지우고 번역하여 채우기
                        text_box = Image.new("RGB", (width+70, height+60), color="white")
                        # text_length = draw.textlength(translated_name, font=font)
                        draw = ImageDraw.Draw(text_box)
                        draw.text((0, 0), translated_name, fill="black", font=font)
                        translated_text_image.paste(text_box, (left-30, top-10))

                    # 번역내용 화면에 출력
                    translated_text_data.append(translated_name)

                # 이미지 저장
                remove_text_image.save(remove_text_save_path + remove_text_base_name)
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

# @app.route("/conversion", methods=["POST"])
# def conversion():
#     all_layer_info = []
#     all_extracted_info_list = []
#     extracted_text_data = []
#     translated_text_data = []

#     try:
#         source_files = request.files.getlist("source_file")
#         for source_file in source_files:
#             source = PSDImage.open(source_file)
            
#             if source:
#                 all_layer_info = vars(source)  # 레이어의 정보
            
#                 psd_image = PSDImage.open(source_file)
#                 image = psd_image.compose()

#                 for layer in psd_image.descendants(include_clip=True):
#                     all_extracted_info_list.append(
#                         {
#                             "kind": layer.kind,
#                             "name": layer.name,
#                             "top": layer.top,
#                             "left": layer.left,
#                             "size": layer.size,
#                         }
#                     )

#                     if layer.kind == "type":
#                         text = layer.text.replace("\r", "\n")
#                         extracted_text_data.append(text)

#                         translated_text = translator.translate(
#                             text, src="ko", dest="en"
#                         ).text
#                         translated_text_data.append(translated_text)
                        
#                 original_filename = secure_filename(os.path.splitext(source_file.filename)[0])
#                 output_image_path = f"static/images/{original_filename}.png"
#                 image.save(output_image_path)
                
#                 image_data = output_image_path

#     except Exception as e:
#         traceback.print_exc()
#         return render_template(
#             "index.html", all_layer_info=f"Error extracting text: {str(e)}"
#                 )

#     return render_template(
#         "index.html",
#         image_data=image_data,
#         all_layer_info=all_layer_info,
#         all_extracted_info_list=all_extracted_info_list,
#         extracted_text_data=extracted_text_data,
#         translated_text_data=translated_text_data,
#     )