from flask import Flask, render_template, request, session, send_file, redirect, url_for, jsonify
import yt_dlp
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return redirect(url_for("youtube"))

@app.route('/download/mp3', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': []
    }

    try:
        buffer = BytesIO()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            ydl.download([url])
            buffer.write(ydl.prepare_filename(info_dict).encode())
            buffer.seek(0)
        
        title = info_dict.get('title', 'audio')
        fileName = f"{title}.mp3"

        return send_file(buffer, as_attachment=True, download_name=fileName, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
