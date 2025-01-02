import yt_dlp

class Ydl_Downloader:
    def __init__(self):
        self.ydl_opts = {
            # 'progress_hooks': [self.__on_progress],
            'postprocessors': [],
            'ignoreerrors': True,
            'quiet': True
        }
        self._recipient = './'
        self.progress_callback = None

    def __on_progress(self, d):
        if d['status'] == 'downloading':
            progress_str = f"Baixando: {d['_percent_str']} de {d['_total_bytes_str']} a {d['_speed_str']}"
            if self.progress_callback:
                self.progress_callback(d)

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
                        "url": data['url']
                    }]
                
                formatted_data = []
                for entry in data['entries']:
                    formatted_data.append({
                        "name": entry['title'],
                        "url": entry['url']
                    })
                return formatted_data
        except Exception:
            return None

    def download_video(self, url):
        self.ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{self.recipient}/%(title)s.%(ext)s'
        })

        try: 
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl: 
                info_dict = ydl.extract_info(url, download=True)
                if info_dict.get('entries'):
                    return "Download de playlist concluído"
                return f"Download concluído: {info_dict['title']}"
        except Exception as e:
            return f"Erro ao baixar o vídeo: {str(e)}"
        
    def download_audio(self, url):
        self.ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': f'{self.recipient}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        })

        try: 
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl: 
                info_dict = ydl.extract_info(url, download=True)
                if info_dict.get('entries'):
                    return "Download de playlist concluído"
                return f"Download concluído: {info_dict['title']}"
        except Exception as e:
            return f"Erro ao baixar o audio: {str(e)}"
