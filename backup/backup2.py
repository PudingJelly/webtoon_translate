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
