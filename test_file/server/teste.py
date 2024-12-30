import yt_dlp

url = "https://www.youtube.com/watch?v=up6fgxby4Do"
destino = 'videos'

def on_progress(d):
    if d['status'] == 'downloading':
        print(f"Baixando: {d['_percent_str']} de {d['_total_bytes_str']} a {d['_speed_str']}")

ydl_opts = {
    'outtmpl': f'{destino}/%(title)s.%(ext)s',
    'progress_hooks': [on_progress],
    
    'format': 'm4a/bestaudio/best',
    'postprocessors': [{ 
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info_dict = ydl.extract_info(url, download=True)
    print(info_dict['title'])
