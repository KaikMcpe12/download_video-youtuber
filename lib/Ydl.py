import yt_dlp
import datetime
from pydub import AudioSegment

class Ydl_Downloader:
    def __init__(self):        
        self.ydl_opts = {
            'postprocessors': [],
            'ignoreerrors': True,
            'quiet': True
        }
        self._recipient = './'
        self.progress_callback = None

    @property
    def recipient(self): 
        return self._recipient
    
    @recipient.setter
    def recipient(self, recipient):
        if(not recipient):
            raise ValueError("Recipient não pode ser vazio")
        self._recipient = recipient

    def set_progress_callback(self, callback):
        self.ydl_opts.update({
            'progress_hooks': [callback],
        })

    def get_url_info(self, url):
        opts = {**self.ydl_opts, 'extract_flat': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                data = ydl.extract_info(url, download=False)

                if 'entries' not in data.keys():
                    return [{
                        "name": data['title'],
                        "url": url
                    }]
                
                formatted_data = []
                for entry in data['entries']:
                    formatted_data.append({
                        "name": entry['title'],
                        "url": entry['url']
                    })
                return formatted_data
        except yt_dlp.utils.DownloadError as e:
            return {"error": str(e)}

    def download(self, url, format_type):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        opts = self.ydl_opts.copy()
        opts.update({
            'format': 'bestvideo+bestaudio/best' if format_type == 'video' else 'bestaudio/best',
            'outtmpl': f"{self.recipient}/%(title)s_{timestamp}.%(ext)s"
        })
        if format_type == 'audio':
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        else:
            opts['merge_output_format'] = 'mp4'
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                if info_dict.get('entries'):
                    return "Download de playlist concluído"
                return f"Download concluído: {info_dict['title']}"
        except yt_dlp.utils.DownloadError as e:
            return f"Erro ao baixar o {format_type}: {str(e)}"

    def download_video(self, url):
        return self.download(url, 'video')

    def download_audio(self, url):
        return self.download(url, 'audio')
    