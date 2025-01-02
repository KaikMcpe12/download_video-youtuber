import tkinter
import tkinter.simpledialog
import customtkinter
from tkinter import filedialog
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from lib.Ydl import Ydl_Downloader
import os
import threading
import re


class YouTubeDownloader(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.downloader = Ydl_Downloader()
        self.downloader.set_progress_callback(self.update_progress)
        self.current_video = 0
        self.total_videos = 0
        self.list_videos = []
        self.setup_ui()

    def setup_ui(self):
        self.title("YouTube Downloader")
        # self.geometry("900x600")
        self.resizable(False, False)

        # Título centralizado
        self.title_label = customtkinter.CTkLabel(self, text="YouTube Downloader", font=("Arial", 24, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="n", columnspan=2)

        # URL Frame
        self.url_frame = customtkinter.CTkFrame(self)
        self.url_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)

        self.url_label = customtkinter.CTkLabel(self.url_frame, text="Cole o link do YouTube aqui:", font=("Arial", 14))
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.url_entry = customtkinter.CTkEntry(self.url_frame, placeholder_text="Link do vídeo ou playlist")
        self.url_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Destination Frame
        self.path_frame = customtkinter.CTkFrame(self)
        self.path_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.path_frame.grid_columnconfigure(1, weight=1)

        self.path_label = customtkinter.CTkLabel(self.path_frame, text="Salvar em:", font=("Arial", 14))
        self.path_label.grid(row=0, column=0, padx=10, pady=10)

        self.path_entry = customtkinter.CTkEntry(self.path_frame)
        self.path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.path_entry.insert(0, os.path.expanduser("~/Downloads"))

        self.browse_button = customtkinter.CTkButton(self.path_frame, text="Procurar", command=self.browse_path)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # Switch Frame for Video/Audio Choice
        self.switch_frame = customtkinter.CTkFrame(self)
        self.switch_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.switch_frame.grid_columnconfigure(0, weight=1)

        self.switch_label = customtkinter.CTkLabel(self.switch_frame, text="Escolha entre Vídeo e Áudio:", font=("Arial", 14))
        self.switch_label.grid(row=0, column=0, padx=10, pady=10)

        self.switch = customtkinter.CTkSwitch(self.switch_frame, text="Vídeo", command=self.switch_changed, font=("Arial", 14))
        self.switch.grid(row=0, column=1, padx=10, pady=10)

        # Download Button
        self.download_button = customtkinter.CTkButton(self, text="Baixar", command=self.start_download, font=("Arial", 16))
        self.download_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        # Progress Frame
        self.progress_frame = customtkinter.CTkFrame(self)
        self.progress_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.playlist_label = customtkinter.CTkLabel(self.progress_frame, text="")
        self.playlist_label.grid(row=0, column=0, padx=10, pady=5)

        self.progress_bar = customtkinter.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.status_label = customtkinter.CTkLabel(self.progress_frame, text="Pronto", font=("Arial", 14))
        self.status_label.grid(row=2, column=0, padx=10, pady=5)

    def abrir_dialogo(self): 
        dialogo = Dialogo(self) 
        self.wait_window(dialogo)

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tkinter.END)
            self.path_entry.insert(0, directory)
            self.downloader.recipient = directory

    def update_progress(self, d):
        if d['status'] == 'downloading':
            try:
                progress = float(re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str']).replace('%', '')) / 100
                speed = re.sub(r'\x1b\[[0-9;]*m', '', d['_speed_str'])
                self.progress_bar.set(progress)
                
                if self.total_videos > 1:
                    self.playlist_label.configure(
                        text=f"Baixando vídeo {self.current_video}/{self.total_videos}"
                    )
                
                self.status_label.configure(
                    text=f"Baixando: {progress*100}% a {speed}."
                )
                self.update_idletasks()
            except Exception:
                pass
        elif d['status'] == 'finished':
            self.current_video += 1
            self.progress_bar.set(1)
            self.status_label.configure(text="Download Completo!")

    def switch_changed(self):
        if self.switch.get() == 1:
            self.switch.configure(text="Áudio")
        else:
            self.switch.configure(text="Vídeo")

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            self.status_label.configure(text="Por favor, insira uma URL")
            return

        self.downloader.recipient = self.path_entry.get()
        self.info_url = self.downloader.get_url_info(url)
        self.total_videos = len(self.info_url)
        self.current_video = 1

        if not self.total_videos:
            self.status_label.configure(text="Nenhum vídeo encontrado")
            return

        self.playlist_label.configure(
            text=f"Preparando para baixar {self.total_videos} vídeos"
        )
        self.download_button.configure(state='disabled')

        # started thread
        thread = threading.Thread(target=self._perform_download, daemon=True)
        thread.start()

    def _perform_download(self):
        try:
            if self.switch.get() == 1:
                result = self.__download_audio([url['url'] for url in self.info_url])
            else:
                result = self.__download_video([url['url'] for url in self.info_url])

            self.status_label.configure(text=result)
        except Exception as e:
            self.status_label.configure(text=f"Erro: {str(e)}")
            self.progress_bar.set(0)

    def __download_video(self, urls):
        for url in urls:
            self.downloader.download_video(url)

    def __download_audio(self, urls):
        for url in urls:
            self.downloader.download_video(url)

    def __save_info_url(self, info_url):
        for video in info_url:
            self.list_videos.append(
                {
                    "name": video['name'],
                    "url": video['url'],
                    "status": False
                }
            )

class Dialogo(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("300x200")
        self.title("Diálogo")

        label = customtkinter.CTkLabel(self, text="Este é um diálogo")
        label.pack(pady=20)

        botao_fechar = customtkinter.CTkButton(self, text="Fechar", command=self.destroy)
        botao_fechar.pack(pady=20)


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
