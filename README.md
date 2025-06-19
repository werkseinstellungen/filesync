# filesync

**filesync** is a super simple web app for uploading and downloading files.  
Each uploaded file gets a unique ID and a private download link.

👉 **[Go check it out →](https://crashdebug.dev)**

## Features

- Upload files up to 50 MB
- Receive a private, unguessable download link
- Simple, no-frills user interface
- No registration or login required
- Files are not publicly listed
- Files may be deleted at any time, without notice or reason

## Usage

### Upload

1. Visit `/upload`
2. Select your file and upload
3. You'll receive a unique link like `/download/<file_id>`

### Download

Visit your download link.  
Example: `/download/example`

## Tech Stack

- Python 3
- Flask
- HTML (Jinja2 templates)
- Tailwind CSS (via CDN)

## Running the App

```bash
# Install dependencies
pip install flask

# Run the server
python app.py
