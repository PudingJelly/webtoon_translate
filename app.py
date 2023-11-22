from io import BytesIO
from flask import Flask, render_template, request, send_file
from googletrans import Translator
from psd_tools import PSDImage
from PIL import Image

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
    source_file = request.files["source_file"]
    all_layer_info = []
    extracted_info = []
    extracted_text_data = []
    # lower_layer_info = []
    # lower_lower_layer_info = []
    # lower_lower_lower_layer_info = []

    if source_file:
        try:
            source = PSDImage.open(source_file)
            all_layer_info = vars(source)

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
                        }
                    )
            extracted_info = layer_info

            # 텍스트 레이어의 정보 추출
            for layer in extracted_info:
                extracted_text_data.append(
                    layer["text"],
                )
            # print(extracted_text_data[1])

        except Exception as e:
            extracted_info = f"Error extracting text: {str(e)}"
            extracted_text_data = []

    return render_template(
        "index.html",
        all_layer_info=all_layer_info,
        extracted_info=extracted_info,
        extracted_text_data=extracted_text_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
