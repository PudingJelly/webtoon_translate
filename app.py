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
        "index.html", tranlated_text="", extracted_info="", layer_kind_info=""
    )


@app.route("/translate", methods=["POST"])
def translate():
    text = request.form["text"]
    target_language = request.form["target_language"]
    default_language = request.form["default_language"]

    if default_language == "":
        translated_text = translator.translate(text, dest=target_language).text
    else:
        translated_text = translator.translate(
            text, src=default_language, dest=target_language
        ).text

    return render_template("index.html", translated_text=translated_text)


@app.route("/extract", methods=["POST"])
def extract_text():
    psd_file = request.files["psd_file"]
    extracted_info = []
    layer_kind_info = []

    if psd_file:
        try:
            psd = PSDImage.open(psd_file)
            print(vars(psd))
            layer_info = []
            for layer in psd:
                layer_kind_info.append(layer.kind)
                if layer.kind == "pixel":
                    layer_info = {
                        "kind": layer.kind,
                        "name": layer.name,
                        "bbox": layer.bbox,
                        "size": layer.size,
                    }
                # layer_kind_info.append(layer.name)
                elif layer.kind == "type":
                    layer_info = {
                        "kind": layer.kind,
                        "name": layer.name,
                        "bbox": layer.bbox,
                        "size": layer.size,
                        "text": layer.text,
                    }
                elif layer.kind == "group":
                    layer_info = {
                        "kind": layer.kind,
                        "name": layer.name,
                        "bbox": layer.bbox,
                        "size": layer.size,
                        "layer": layer,
                    }
                extracted_info.append(layer_info)
            print(layer_kind_info)

        except Exception as e:
            extracted_info = f"Error extracting text: {str(e)}"

    return render_template(
        "index.html", extracted_info=extracted_info, layer_kind_info=layer_kind_info
    )


@app.route('/download_image', methods=['POST'])
def download_image_without_text():
    try:
        psd_file = request.files['psd_file']

        if psd_file:
            psd = PSDImage.open(psd_file)
            img = Image.new("RGBA", (psd.width, psd.height), (255, 255, 255, 0))

            for layer in psd:
                if layer.kind != 'type':  # 텍스트 레이어를 제외한 다른 레이어 필터링
                    img.paste(layer.compose(), (0, 0), layer.compose())
            
            img_io = BytesIO()
            img.save(img_io, format='JPEG')

            img_io.seek(0)
            return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name=f'{psd_file.filename}_without_text.jpg')
    
    
    except Exception as e:
        return f"Error downloading image: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
