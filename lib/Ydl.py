import yt_dlp

class Ydl_Downloader:
    def __init__(self):
        self.ydl_opts = {
            'progress_hooks': [self.__on_progress],
            'postprocessors': []
        }
        self._recipient = './'

    def __on_progress(self, d):
        if d['status'] == 'downloading':
            print(f"Baixando: {d['_percent_str']} de {d['_total_bytes_str']} a {d['_speed_str']}")

    @property
    def recipient(self): 
        return self._recipient
    
    @recipient.setter
    def recipient(self, recipient):
        if(not recipient):
            raise ValueError("Recipient não pode ser vazio")
        
        self.recipient = recipient

    def download_video(self, url):
        self.ydl_opts.update({
            'format': 'bestvideo/best',
            'outtmpl': f'{self.recipient}/%(title)s.%(ext)s'
        })

        try: 
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl: 
                info_dict = ydl.extract_info(url, download=True) 
                return (f"Download concluído: {info_dict['title']}") 
        except Exception as e:
            return (f"Erro ao baixar o vídeo: {str(e)}")
        
    def download_audio(self, url):
        self.ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': f'{self.recipient}/%(title)s.%(ext)s'
        })

        try: 
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl: 
                info_dict = ydl.extract_info(url, download=True) 
                return (f"Download concluído: {info_dict['title']}") 
        except Exception as e:
            return (f"Erro ao baixar o audio: {str(e)}")


downloader = Ydl_Downloader()

res = downloader.download_video('https://youtu.be/up6fgxby4Do?si=n94Mp55YnabakMMu')