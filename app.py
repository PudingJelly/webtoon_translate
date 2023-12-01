import os
from flask import Flask, render_template, request, session, send_file
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
        text_layer_info="",
        extracted_text_data="",
        translated_text_data="",
    )


@app.route("/upload", methods=["POST"])
def upload_file():
    # HTML에 출력하기 위한 리스트 초기화
    text_layer_info = []
    extracted_text_data = []
    translated_text_data  = []

    try:
        source_file = request.files["source_file"]

        if source_file:
            source = PSDImage.open(source_file)

            # PSD 파일의 이미지 추출
            image = source.compose()
            # 원본 파일 이름 추출
            original_filename = os.path.splitext(source_file.filename)[0]

            # 원본 png 변환 후 저장
            converted_image_path = (
                f"static/images/original_converted/{original_filename}.png"
            )
            image.save(converted_image_path)

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
            text_layer_info.sort(key=lambda x: x['top'])
            
            # 이미지 분리를 위한 원본소스 복사
            common_image = image.copy()
            # translated_text_image = image.copy()

            # 텍스트 레이어 세부정보 추출
            for layer in text_layer_info:
                text, top, left, width, height = (
                    layer["text"],
                    layer["top"],
                    layer["left"],
                    layer["size"][0],
                    layer["size"][1],
                )
                
                extracted_text_data.append(text)

                white_box = Image.new("RGB", (width, height), color="white")
                common_image.paste(white_box, (left, top))
            
            # 텍스트제거 이미지 저장
            remove_text_save_path = (
                f"static/images/remove_text/{original_filename}_remove_text.png"
            )
            common_image.save(remove_text_save_path)

            session["converted_image_path"] = converted_image_path
            session["original_filename"] = original_filename
            # session["all_layer_info"] = all_layer_info
            session["text_layer_info"] = text_layer_info
            session["extracted_text_data"] = extracted_text_data
            session["remove_text_save_path"] = remove_text_save_path

            return render_template(
                "index.html",
                image_data=converted_image_path,
                text_layer_info=text_layer_info,
                extracted_text_data=extracted_text_data,
                translated_text_data=translated_text_data
            )

    except Exception as e:
        return render_template(
            "index.html",
            image_data=None,
            translated_text_image_data=None,
            all_layer_info=f"Error extracting text: {str(e)}",
            text_layer_info=[],
            extracted_text_data=[],
            translated_text_data=""
        )


@app.route("/auto_translation", methods=["POST"])
def auto_translation():
    # 번역된 텍스트 데이터 리스트
    translated_text_data = []

    # 세션값 가져오기
    text_layer_info = session.get("text_layer_info")
    original_filename = session.get("original_filename")
    converted_image_path = session.get("converted_image_path")
    remove_text_save_path = session.get("remove_text_save_path")
    extracted_text_data = session.get("extracted_text_data")

    target_language = request.form.get("target_language")
    font = ImageFont.truetype(f"static/fonts/NotoSansKR-Regular.ttf", 70)  # 사용할 폰트와 크기 설정

    # 텍스트를 삽입 할 이미지 복사
    translated_image = Image.open(remove_text_save_path).copy()

    # 이미지에 번역된 텍스트들을 그려서 합치기
    draw = ImageDraw.Draw(translated_image)

    for layer in text_layer_info:
        text, top, left = (
            layer["text"],
            layer["top"],
            layer["left"],
        )

        # 텍스트 특수 기호 처리 및 번역
        clean_text = text.replace("\r", "\n")
        translated_text = translator.translate(clean_text, dest=target_language).text
        translated_text_data.append(translated_text)

        # 이미지에 텍스트 그리기
        draw.text((left - 10, top), translated_text, fill="black", font=font)

    # 번역 이미지 저장
    translated_text_save_path = f"static/images/auto_translation/{target_language}/"
    translated_text_base_name = f"{original_filename}_{target_language}.png"

    # 경로내에 폴더가 없을 경우 폴더 생성
    if not os.path.exists(translated_text_save_path):
        os.mkdir(translated_text_save_path)

    translated_image_path = translated_text_save_path + translated_text_base_name
    translated_image.save(translated_image_path)

    # 세션에 저장
    session["translated_image_path"] = translated_image_path
    session["target_language"] = target_language
    session["translated_text_data"] = translated_text_data

    return render_template(
        "index.html",
        image_data=converted_image_path,
        translated_text_image_data=translated_image_path,
        text_layer_info=text_layer_info,
        extracted_text_data=extracted_text_data,
        translated_text_data=translated_text_data,
    )
    
@app.route("/user_translation", methods=["POST"])
def user_translation():
    user_translated_text_data = []
    user_translated_text = []
    
    modified_texts = request.form.getlist('modified_text')
    print(modified_texts)

    text_layer_info = session.get("text_layer_info")
    original_filename = session.get("original_filename")
    remove_text_save_path = session.get("remove_text_save_path")
    target_language = session.get("target_language")
    converted_image_path = session.get("converted_image_path")
    extracted_text_data = session.get("extracted_text_data")
    translated_text_data = session.get("translated_text_data")
    
    font = ImageFont.truetype(f"static/fonts/NotoSansKR-Regular.ttf", 70)
    user_translated_image = Image.open(remove_text_save_path).copy()
    
    draw = ImageDraw.Draw(user_translated_image)
    
    for index, layer in enumerate(text_layer_info):
          
        user_translated_text_data.append({
            "text": modified_texts[index] if index < len(modified_texts) else "",
            "top": layer["top"],
            "left": layer["left"]
        })
    
    for layer in user_translated_text_data:
        modi_text, top, left = (
            layer["text"],
            layer["top"],
            layer["left"],
        )
        user_translated_text.append(modi_text)
        
        draw.text((left - 10, top), modi_text, fill="black", font=font)
    
    # 번역 이미지 저장
    user_translated_text_save_path = f"static/images/user_translation/{target_language}/"
    user_translated_text_base_name = f"user_{original_filename}_{target_language}.png"

    # 경로내에 폴더가 없을 경우 폴더 생성
    if not os.path.exists(user_translated_text_save_path):
        os.mkdir(user_translated_text_save_path)

    user_translated_image_path = user_translated_text_save_path + user_translated_text_base_name
    user_translated_image.save(user_translated_image_path)
    
    session["translated_image_path"] = user_translated_image_path
    
    return render_template(
        "index.html",
        image_data=converted_image_path,
        translated_text_image_data=user_translated_image_path,
        text_layer_info=text_layer_info,
        extracted_text_data=extracted_text_data,
        translated_text_data=user_translated_text,
    )
    

# 가장 마지막으로 번역 작업 된 이미지만 다운로드
@app.route("/download")
def download():
    translated_image_path = session.get("translated_image_path")
    return send_file(translated_image_path, as_attachment=True)


# @app.route("/session_clear")
# def session_clear():
#     session.clear()

if __name__ == "__main__":
    app.run(debug=True)
