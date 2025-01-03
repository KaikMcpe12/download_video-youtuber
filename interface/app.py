import tkinter
import tkinter.simpledialog
import customtkinter
from tkinter import filedialog, messagebox
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

        self.status_label = customtkinter.CTkLabel(self.progress_frame, text="Preparado para baixar", font=("Arial", 14))
        self.status_label.grid(row=2, column=0, padx=10, pady=5)

        self.details_button = customtkinter.CTkButton(self.progress_frame, text="Detalhes dos Downloads", command=self.open_details_window)
        self.details_button.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tkinter.END)
            self.path_entry.insert(0, directory)
            self.downloader.recipient = directory

    def open_details_window(self):
        # toplevel
        self.details_window = customtkinter.CTkToplevel(self)
        self.details_window.title("Detalhes dos Downloads")
        self.details_window.geometry("600x400")

        self.details_label = customtkinter.CTkLabel(self.details_window, text="Downloads Detalhados", font=("Arial", 18, "bold"))
        self.details_label.pack(pady=10)

        # bg toplevel
        background_color = self.details_window.cget("bg")

        # listbox
        self.download_list = tkinter.Listbox(self.details_window, font=("Arial", 14), bg=background_color, highlightthickness=0, borderwidth=0)
        self.download_list.pack(expand=True, fill="both", padx=10, pady=10)

        # update list
        self.update_download_list()
    
    def update_download_list(self):
        # clear list
        if hasattr(self, 'download_list'):
            self.download_list.delete(0, tkinter.END)

            # added itens
            for video in self.list_videos:
                status = "Concluído" if video["status"] else "Em progresso"
                self.download_list.insert(tkinter.END, f"{video['name']} - {status}")

    def update_progress(self, d):
        if d['status'] == 'downloading':
            try:
                progress = float(re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str']).replace('%', '')) / 100
                speed = re.sub(r'\x1b\[[0-9;]*m', '', d['_speed_str'])
                self.progress_bar.set(progress)

                # update status list
                # self.list_videos[self.current_video - 1]["status"] = False
                # self.update_download_list()
                
                if self.total_videos > 1:
                    self.playlist_label.configure(
                        text=f"Baixando vídeo {self.current_video}/{self.total_videos}"
                    )
                
                self.status_label.configure(
                    text=f"Baixando: {progress*100:.1f}% a {speed}."
                )
                self.update_idletasks()
            except Exception:
                print('e1')
                pass
        elif d['status'] == 'finished':
            messagebox.showinfo("Download Completo", "O download foi concluído com sucesso!")
            self.current_video += 1
            self.progress_bar.set(1)
            self.status_label.configure(text="Download Completo!")
            self.download_button.configure(state='enabled')
 
            # update status list to finished
            # self.list_videos[self.current_video - 2]["status"] = True
            # self.update_download_list()

    def switch_changed(self):
        if self.switch.get() == 1:
            self.switch.configure(text="Áudio")
        else:
            self.switch.configure(text="Vídeo")

    def start_download(self):
        self.download_button.configure(state='disabled')

        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Atenção", "Por favor, insira uma URL válida.")
            return

        self.downloader.recipient = self.path_entry.get()

        try:
            self.info_url = self.downloader.get_url_info(url)
        except Exception as e:
            messagebox.showerror("Erro ao Obter Informações", f"Não foi possível obter informações da URL:\n{str(e)}")
            self.download_button.configure(state='enabled')
            return
        
        self.total_videos = len(self.info_url)
        self.current_video = 1

        if not self.total_videos:
            self.status_label.configure(text="Nenhum vídeo encontrado")
            return

        if self.total_videos == 1:
            self.playlist_label.configure(
                text=f"{self.info_url[0]['name']}"
            )
            self.downloader.set_progress_callback(self.update_progress)
        else:
            self.playlist_label.configure(
                text=f"Preparando para baixar {self.total_videos} vídeos"
            )
            self.downloader.set_progress_callback(self.update_progress)

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
            messagebox.showerror("Erro no Download", f"Um erro ocorreu durante o download:\n{str(e)}")
            self.status_label.configure(text=f"Erro: {str(e)}")
            self.progress_bar.set(0)

    def __download_video(self, urls):
        for url in urls:
            self.downloader.download_video(url)

    def __download_audio(self, urls):
        for url in urls:
            self.downloader.download_audio(url)

    def __save_info_url(self, info_url):
        for video in info_url:
            self.list_videos.append(
                {
                    "name": video['name'],
                    "url": video['url'],
                    "status": False
                }
            )

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
