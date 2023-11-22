from io import BytesIO
from flask import Flask, render_template, request, send_file
from googletrans import Translator
from psd_tools import PSDImage

app = Flask(__name__)
translator = Translator()


@app.route("/")
def index():
    return render_template(
        "index.html",
        extracted_info="",
        lower_layer="",
        lower_lower_layer=""
    )

@app.route("/extract", methods=["POST"])
def extract_text():
    psd_file = request.files["psd_file"]
    extracted_info = []
    lower_layer = []
    lower_lower_layer = []

    if psd_file:
        try:
            psd = PSDImage.open(psd_file)
            
            for layer in psd:
                layer_info = {
                    "kind": layer.kind,
                    "name": layer.name,
                    "top": layer.top,
                    "left": layer.left,
                    "sub_layers": []  # Initialize an empty list to hold sub-layers
                }
                if layer.is_group():
                    for sub_layer in layer:
                        sub_layer_info = {
                            "kind": sub_layer.kind,
                            "name": sub_layer.name,
                            "top": sub_layer.top,
                            "left": sub_layer.left,
                            "sub_sub_layers": []  # Initialize an empty list for sub-sub-layers
                        }
                        if sub_layer.is_group():
                            for sub_sub_layer in sub_layer:
                                sub_sub_layer_info = {
                                    "kind": sub_sub_layer.kind,
                                    "name": sub_sub_layer.name,
                                    "top": sub_sub_layer.top,
                                    "left": sub_sub_layer.left,
                                }
                                sub_layer_info["sub_sub_layers"].append(sub_sub_layer_info)
                        layer_info["sub_layers"].append(sub_layer_info)
                if not layer.is_group():
                    extracted_info.append(layer_info)
                else:
                    lower_layer.append(layer_info)
        
        except Exception as e:
            extracted_info = f"Error extracting layers: {str(e)}"

    return render_template(
        "index.html",
        extracted_info=extracted_info,
        lower_layer=lower_layer,
        lower_lower_layer=lower_lower_layer
    )
    
@app.route("/download_image", methods=["POST"])
def download_image():
    try:
        psd_file = request.files["psd_file"]

        if psd_file:
            psd = PSDImage.open(psd_file)
            has_text_layers = any(layer.kind == "type" for layer in psd)

            if has_text_layers:
                # 텍스트 레이어만 포함한 PSD 생성
                text_psd = PSDImage.new(psd.width, psd.height)
                text_layers = [layer for layer in psd if layer.kind == "type"]
                text_psd.layers = text_layers

                img_with_text_io = BytesIO()
                text_psd.save(img_with_text_io, format="JPEG")
                img_with_text_io.seek(0)

                return send_file(
                    img_with_text_io,
                    mimetype="image/jpeg",
                    as_attachment=True,
                    download_name=f"{psd_file.filename}_text_layers.jpg",
                )

            else:
                img_io = BytesIO()
                psd.composite().save(img_io, format="JPEG")
                img_io.seek(0)

                return send_file(
                    img_io,
                    mimetype="image/jpeg",
                    as_attachment=True,
                    download_name=f"{psd_file.filename}_without_text.jpg",
                )

    except Exception as e:
        return f"Error downloading image: {str(e)}"
    
    
    # if layer.is_group() and layer.name == "TEXT":
                #     extract_layers_info(layer, lower_layer_info)
                # for sub_layer in layer.descendants():
                #     if sub_layer.is_group():
                #         extract_layers_info(sub_layer, lower_lower_layer_info)
                #         for sub_sub_layer in sub_layer.descendants():
                #             if sub_sub_layer.is_group():
                #                 extract_layers_info(sub_sub_layer, lower_lower_lower_layer_info)
                # for sub_layer in layer:
                #     lower_layer_info.append({
                #             "kind": sub_layer.kind,
                #             "name": sub_layer.name,
                #         })

                #     if sub_layer.is_group():
                #         for sub_sub_layer in sub_layer:
                #             lower_lower_layer_info.append({
                #                     "kind": sub_sub_layer.kind,
                #                     "name": sub_sub_layer.name,
                #                 })

                #             if sub_sub_layer.is_group():
                #                 for sub_sub_sub_layer in sub_sub_layer:
                #                     lower_lower_lower_layer_info.append({
                #                             "kind": sub_sub_sub_layer.kind,
                #                             "name": sub_sub_sub_layer.name,
                #                         })
                
                # def extract_layers_info(layer, result):
#     for sub_layer in layer.descendants():
#         result.append(
#             {
#                 "kind": sub_layer.kind,
#                 "name": sub_layer.name,
#             }
#         )

if __name__ == "__main__":
    app.run(debug=True)