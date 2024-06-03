from flask import Flask, jsonify
from flask import request, make_response, url_for, flash, redirect, render_template, send_from_directory
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
import pandas as pd
import re
import sqlite3
import os
from werkzeug.utils import secure_filename
from io import StringIO
from pathlib import Path

app = Flask(__name__)

app_root = os.path.dirname(os.path.abspath(__file__))
upload_folder = os.path.join('staticfiles', 'uploads')
app.config['upload_folder'] = upload_folder
class CustomFlaskAppWithEncoder(Flask):
    json_provider_class = LazyJSONEncoder
app = CustomFlaskAppWithEncoder(__name__)

swagger_template = dict(
    info = {
        'title': LazyString(lambda: "Gold Challenge Muhammad Dimaz Farhan"),
        'version': LazyString(lambda: "1.0.0"),
        'description': LazyString(lambda: "Dokumentasi API untuk data Processing dan Modeling"),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "docs",
            "route": "/docs.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,config = swagger_config)

@swag_from(r"C:\Users\Samid\BINAR\GoldChallenge\text_processing.yml", methods= ['POST'])
@app.route('/text-processing', methods = ['POST'])
def text_processing():
    text = request.form.get("text")
    text_cleansing1 = str(text).upper()
    text_cleansing2 = re.sub(r'[^a-zA-Z0-9]', ' ', text_cleansing1)

    conn = sqlite3.connect('goldchallenge.db')
    print("Opened database successfully")

    conn.execute("INSERT INTO data (Text, Text_cleaned) VALUES (?, ?)", (text, text_cleansing2))
    print("Success to add database")

    conn.commit()
    print("Records created successfully")
    conn.close()
    print(text_cleansing2)
    
    json_response = {
        'Status_code': 200,
        'Description': "Teks yang sudah diproses",
        'Data': text_cleansing2
    }

    response_data= jsonify(json_response)
    return response_data


@swag_from(r"C:\Users\Samid\BINAR\GoldChallenge\file_processing.yml", methods = ['POST'])
@app.route('/file-processing', methods = ['POST'])
def upload_file():   
    if 'file_process' not in request.files:
        return redirect(request.url)
    
    file = request.files['file_process']
    if file.filename == '':
        return redirect(request.url)
    
    csv_filename = secure_filename(file.filename)
    file.save(os.path.join(upload_folder, csv_filename))
    path = os.path.join(upload_folder)
    print("file_data", csv_filename)

    file_path = Path(path) / csv_filename
    try:
        read = file_path.read_text(encoding='ANSI')

        df = pd.read_csv(StringIO(read), header = None)

        read_csv = df[0].head()
        print("read_csv", read_csv)

        cleaned_text= []
        for text in read_csv:
            cleaned_text.append(re.sub(r'[^a-zA-Z0-9]', ' ',text).lower())
        print("text_cleaned", cleaned_text)
    
        json_response = {
        'Status_code': 200,
        'Description': "File yang sudah diproses",
        'Data': cleaned_text,
    }
        conn = sqlite3.connect('goldchallenge.db')
        print("Opened database successfully")

        conn.execute("INSERT INTO data(Text, Text_cleaned) VALUES (?, ?)",(str(read_csv), str(cleaned_text)))
        print("add database successfully")
        conn.commit()
        conn.close()

    except Exception as read :
        response_data= jsonify(json_response)
        return response_data
    return cleaned_text


if __name__ == '__main__':
    app.run(debug=True)
