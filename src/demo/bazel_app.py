from io import BytesIO
from flask import Flask, request, jsonify
import torch
import torchvision
from torchvision import io
from werkzeug import Request
import os
import certifi
from hello_rs import hello_rs

os.environ["SSL_CERT_FILE"] = certifi.where()

Request.max_form_parts = 16 * 1024 * 1024

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = None
app.config['MAX_FORM_MEMORY_SIZE'] = 50 * 1024 * 1024


@app.route("/")
def hello_world():
    return f"<p>{hello_rs.hello()}</p>"


@app.post("/classify")
def classify():
    image_data = bytearray(request.get_data())

    image_data = io.decode_image(torch.asarray(image_data, dtype=torch.uint8))

    weights = torchvision.models.ResNet50_Weights.DEFAULT
    model = torch.hub.load("pytorch/vision", "resnet50", weights=weights)
    model.eval()

    preprocess = weights.transforms()
    categories = weights.meta["categories"]

    input_batch = image_data.unsqueeze(0)
    input_batch = preprocess(input_batch)

    with torch.no_grad():
        output = model(input_batch)

    probabilities = output.squeeze(0).softmax(0)

    top5_prob, top5_catid = torch.topk(probabilities, 5)

    return jsonify({"result": categories[top5_catid[0]], "score": top5_prob[0].item()})
