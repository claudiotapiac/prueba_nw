from flask import Flask, jsonify, request
import torch
from model_atraso import AutoencoderClassifier
from flask_cors import CORS
import pandas as pd
import pickle
from zipfile import ZipFile


model_rf_extract = ZipFile('./models/model_rf.zip')
model_rf_extract.extract('model_rf.pickle', './models/')

app = Flask(__name__)
CORS(app)

try:
  rf_model = pickle.load(open('./models/model_rf.pickle', 'rb'))
except:
  print("No existe archivo para el modelo de RandomForest")

torch_model = AutoencoderClassifier(8)
torch_model.load_state_dict(torch.load('./models/model_pytorch.pth')) 
torch_model.eval()


def str_2_model(input_model, type = "sklearn"):
  for i, value in enumerate(input_model):
    input_model[i] = float(value)
  if type == "pytorch":
    input_model = torch.tensor(input_model, dtype=torch.float32)
  else:
    input_model = pd.DataFrame(input_model).T
  return input_model


@app.route('/torch/',methods = ['POST', 'GET'])
def pytorch():
  input_model = request.form.to_dict(flat=False)
  input_model = input_model['values']
  input_model = str_2_model(input_model, "pytorch")

  with torch.no_grad():
    output = torch_model(input_model)

  result = {'value': output.item()}
  return jsonify(result)


@app.route('/rf/',methods = ['POST', 'GET'])
def rf():
  try:
    input_model = request.form.to_dict(flat=False)
    input_model = input_model['values']
    input_model = str_2_model(input_model, "sklearn")
    
    output = rf_model.predict(input_model)

    result = {'value': output.item()}
  except:
    result = {}
  return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)


