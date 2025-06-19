import os
import uuid
import json
import hashlib
from datetime import datetime
from flask import Flask, request, send_file, render_template, redirect, url_for

UPLOAD_ROOT = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_ROOT'] = UPLOAD_ROOT
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

os.makedirs(UPLOAD_ROOT, exist_ok=True)


def generate_metadata(file_storage, file_id: str):
    file_bytes = file_storage.read()
    file_storage.seek(0)

    hash_sha256 = hashlib.sha256(file_bytes).hexdigest()
    extension = os.path.splitext(file_storage.filename)[1].lower()
    return {
        'file_id': file_id,
        'original_filename': file_storage.filename,
        'extension': extension,
        'mime_type': file_storage.mimetype,
        'sha256': hash_sha256,
        'size': len(file_bytes),
        'uploaded_at': datetime.utcnow().isoformat()
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload')
def upload_page():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/upload-failed')

    file = request.files['file']
    if file.filename == '':
        return redirect('/upload-failed')

    file_id = str(uuid.uuid4())
    file_dir = os.path.join(UPLOAD_ROOT, file_id)
    os.makedirs(file_dir, exist_ok=True)

    try:
        metadata = generate_metadata(file, file_id)

        data_path = os.path.join(file_dir, 'data')
        info_path = os.path.join(file_dir, 'info.json')

        file.save(data_path)
        with open(info_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return redirect(url_for('upload_success', file_id=file_id))
    except Exception:
        return redirect('/upload-failed')


@app.route('/upload-success')
def upload_success():
    file_id = request.args.get('file_id')
    info_path = os.path.join(UPLOAD_ROOT, file_id, 'info.json')
    if not os.path.exists(info_path):
        return redirect('/upload-failed?error=Upload+metadata+missing')

    with open(info_path, 'r') as f:
        metadata = json.load(f)

    return render_template('upload_success.html', metadata=metadata)


@app.route('/upload-failed')
def upload_failed():
    error = request.args.get("error", default=None)
    return render_template('upload_failed.html', error=error)


@app.errorhandler(413)
def file_too_large(e):
    return redirect("/upload-failed?error=File+too+large.+Maximum+size+is+50+MB.")


@app.route('/download/<file_id>')
def download_page(file_id):
    info_path = os.path.join(UPLOAD_ROOT, file_id, 'info.json')
    if not os.path.exists(info_path):
        return redirect('/not-found')

    with open(info_path, 'r') as f:
        metadata = json.load(f)

    return render_template('download.html', metadata=metadata)


@app.route('/files/<file_id>')
def serve_file(file_id):
    file_path = os.path.join(UPLOAD_ROOT, file_id, 'data')
    info_path = os.path.join(UPLOAD_ROOT, file_id, 'info.json')

    if not os.path.exists(file_path) or not os.path.exists(info_path):
        return redirect('/not-found')

    with open(info_path) as f:
        metadata = json.load(f)

    return send_file(file_path, as_attachment=True, download_name=metadata['original_filename'])


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
