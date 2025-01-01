import yt_dlp
from io import BytesIO
from pydub import AudioSegment

def download_and_convert_to_mp3(url):
    # Baixar o vídeo como blob
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '-',
        'quiet': True,
        'no_warnings': True,
        # 'progress_hooks': [lambda d: print(f"Baixando: {d['_percent_str']} de {d['_total_bytes_str']}")],
    }

    buffer = BytesIO()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        buffer.write(ydl.prepare_filename(info_dict).encode())
        buffer.seek(0)
    
    # Converter o blob em MP3
    audio = AudioSegment.from_file(buffer, format="webm")
    mp3_buffer = BytesIO()
    audio.export(mp3_buffer, format="mp3")
    mp3_buffer.seek(0)
    
    return mp3_buffer

# Exemplo de uso
url = 'https://www.youtube.com/watch?v=djJiHXTC31A&list=PLtjHcdqsswzgxeQsZvP54KGEW0chvLIjg&index=8'
mp3_blob = download_and_convert_to_mp3(url)
with open('output.mp3', 'wb') as f:
    f.write(mp3_blob.read())
