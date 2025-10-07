import shutil

from flask import Flask, json, request, jsonify, render_template
import os
from auth_utils import verify_user_token


import threading

model_lock = threading.Lock()
yolo_lock = threading.Lock()


os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64,garbage_collection_threshold:0.6"

import dpdc_amr.utils
from werkzeug.utils import secure_filename
from dpdc_amr.testMyML import getModel, examine
from dpdc_amr.digitExtractions import getYoloModel, extract_digits
from waitress import serve

app = Flask(__name__, template_folder='./templates')

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 16 MB

model = getModel()
yModel = getYoloModel()

app.secret_key = "caircocoders-ednalan"

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def secure_endpoint():
    data = request.get_json(silent=True)
    username = request.form.get("username") or (data.get("username") if data else None)
    token = request.form.get("token") or (data.get("token") if data else None)

    if not username:
        resp = jsonify({'message': 'Username is missing'})
        resp.status_code = 400
        return resp

    if not token:
        resp = jsonify({'message': 'Token is missing'})
        resp.status_code = 400
        return resp

    ok, message = verify_user_token(username, token)  # now always returns tuple
    if not ok:
        resp = jsonify({'message': message})
        resp.status_code = 401
        return resp

    return None  # verified



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/batch_proc')
def batch_proc():
    return render_template('batch_proc.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # --- Authentication ---
    auth = secure_endpoint()
    if auth:  # secure_endpoint returned a Response → auth failed
        return auth


    # check if the post request has the file part
    if 'files' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files')

    imgflg = False
    dAreaFlg = False
    if 'imgflg' in request.form:
        imgflg = True
    if 'dAreaFlg' in request.form:
        dAreaFlg = True

    errors = {}
    success = False
    messages = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                with model_lock:
                    result = examine(model, os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except Exception as e:
                print(e)
                print('Error in Image Classification!')
                errors['message'] = 'Error in Image Classification!'
                resp = jsonify(errors)
                resp.status_code = 500
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return resp
            obj = dpdc_amr.utils.Message(filename=filename, cls=result, reading='', img='', cimg='')
            if result == 'Meter':
                try:
                    with yolo_lock:
                        digits, b64, cb64 = extract_digits(yModel, os.path.join(app.config['UPLOAD_FOLDER'], filename),
                                                       0.5, imgflg, dAreaFlg)
                except Exception as e:
                    print(e)
                    print('Error in Reading!')
                    errors['message'] = 'Error in Reading!'
                    resp = jsonify(errors)
                    resp.status_code = 500
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return resp

                obj.reading = digits
                obj.img = b64
                obj.cimg = cb64
            messages.append(obj.__dict__)
            success = True
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        resp = jsonify({'message': messages})
        resp.status_code = 200
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


@app.route('/upload_batch', methods=['POST'])
def upload_batch():
    # --- Authentication ---
    auth = secure_endpoint()
    if auth:  # secure_endpoint returned a Response → auth failed
        return auth

    # check if the post request has the file part
    if 'files' not in request.files:
        resp = jsonify({'message': 'No file part in the request!'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files')

    imgflg = False
    dAreaFlg = False
    if 'imgflg' in request.form:
        imgflg = True
    if 'dAreaFlg' in request.form:
        dAreaFlg = True

    errors = {}
    success = False
    messages = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                with model_lock:
                    result = examine(model, os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except Exception as e:
                print(e)
                result = 'Error'

            obj = dpdc_amr.utils.Message(filename=filename, cls=result, reading='', img='', cimg='')
            if result == 'Meter':
                try:
                    with yolo_lock:
                        digits, b64, cb64 = extract_digits(yModel, os.path.join(app.config['UPLOAD_FOLDER'], filename),
                                                       0.5, imgflg, dAreaFlg)
                except Exception as e:
                    print(e)
                    print('Error in Reading!')
                    digits = 'Error'
                    b64 = ''
                    cb64 = ''

                obj.reading = digits
                obj.img = b64
                obj.cimg = cb64

            messages.append(obj.__dict__)
            success = True
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        resp = jsonify({'message': messages})
        resp.status_code = 200
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


def classify_folder(model, local_folder):
    messages = []
    for filename in os.listdir(local_folder):
        file_path = os.path.join(local_folder, filename)

        if os.path.isfile(file_path) and allowed_file(filename):
            try:
                with model_lock:
                    result = examine(model, file_path)
                    # Ensure result is a string
                    if isinstance(result, tuple):
                        result = result[0]
            except Exception as e:
                print(f"Error classifying {filename}: {e}")
                continue

            # Create subfolder for result
            dest_folder = os.path.join(local_folder, result)
            os.makedirs(dest_folder, exist_ok=True)

            dest_path = os.path.join(dest_folder, filename)

            # Move and replace if exists
            if os.path.exists(dest_path):
                os.remove(dest_path)
            shutil.move(file_path, dest_path)

            messages.append({'filename': filename, 'class': result})

    return messages

@app.route('/classify_folder', methods=['POST'])
def classify_folder_route():
    # --- Authentication ---
    auth = secure_endpoint()
    if auth:
        return auth

    folder = request.form.get('folder')
    if not folder or not os.path.isdir(folder):
        resp = jsonify({'message': 'Invalid folder path!'})
        resp.status_code = 400
        return resp

    messages = classify_folder(model, folder)

    resp = jsonify({'message': messages, 'status': 'completed'})
    resp.status_code = 200
    return resp






if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


def main():
    print("Server has started!")
    print("* Running on http://127.0.0.1:5151")
    serve(app, host='0.0.0.0', threads=16, port=5151, channel_timeout=60)
