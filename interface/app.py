import tkinter
import tkinter.simpledialog
import customtkinter
from tkinter import ttk
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

        # style = ttk.Style()
        # style.theme_use("default")
        # style.configure("Treeview", 
        #                 background="#2c2c2c", 
        #                 foreground="white", 
        #                 rowheight=25, 
        #                 fieldbackground="#2c2c2c",
        #                 font=("Arial", 12))
        # style.map("Treeview", background=[("selected", "#3a9bfd")])
        # style.configure("Treeview.Heading", font=("Arial", 14, "bold"), foreground="white", background="#1a1a1a")

    def setup_ui(self):
        self.title("YouTube Downloader")
        # self.geometry("900x600")
        self.resizable(False, False)

        # sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="ns", padx=10, pady=10)

        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Downloader", font=("Arial", 24, "bold"), text_color="#3a9bfd"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")

        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Aparência:", anchor="w", font=("Arial", 14)
        )
        self.appearance_mode_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")

        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionmenu.grid(row=5, column=0, padx=20, pady=10)

        # URL frame
        self.url_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.url_frame.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=1)

        self.url_label = customtkinter.CTkLabel(
            self.url_frame, text="Cole o link do vídeo/playlist:", font=("Arial", 16)
        )
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.url_entry = customtkinter.CTkEntry(self.url_frame, placeholder_text="Cole o link aqui")
        self.url_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # directory
        self.path_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.path_frame.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)

        self.path_label = customtkinter.CTkLabel(self.path_frame, text="Salvar em:", font=("Arial", 16))
        self.path_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.path_entry = customtkinter.CTkEntry(self.path_frame)
        self.path_entry.insert(0, os.path.expanduser("~/Downloads"))
        self.path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.browse_button = customtkinter.CTkButton(
            self.path_frame, text="Procurar", command=self.browse_path, corner_radius=8
        )
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        # switch (video and audio)
        self.switch_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.switch_frame.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        self.switch_label = customtkinter.CTkLabel(
            self.switch_frame, text="Baixar como:", font=("Arial", 16)
        )
        self.switch_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.switch = customtkinter.CTkSwitch(self.switch_frame, text="Vídeo", command=self.switch_changed)
        self.switch.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # download
        self.download_button = customtkinter.CTkButton(
            self, text="Baixar", font=("Arial", 18), command=self.start_download
        )
        self.download_button.grid(row=3, column=1, padx=20, pady=20, sticky="ew")

        # progress
        self.progress_frame = customtkinter.CTkFrame(self)
        self.progress_frame.grid(row=5, column=1, padx=20, pady=10, sticky="ew")

        self.playlist_label = customtkinter.CTkLabel(self.progress_frame, text="")
        self.playlist_label.grid(row=0, column=0, padx=10, pady=5)

        self.progress_bar = customtkinter.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.status_label = customtkinter.CTkLabel(self.progress_frame, text="Preparado para baixar", font=("Arial", 14))
        self.status_label.grid(row=2, column=0, padx=10, pady=5)

        self.details_button = customtkinter.CTkButton(self.progress_frame, text="Detalhes dos Downloads", command=self.create_details_window)
        self.details_button.grid(row=1, column=3, padx=20, pady=10, sticky="ew")

        self.progress_frame.grid_columnconfigure(0, weight=1)
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def browse_path(self):
        directory = tkinter.filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tkinter.END)
            self.path_entry.insert(0, directory)
            self.downloader.recipient = directory
    
    def switch_changed(self):
        self.switch.configure(text="Áudio" if self.switch.get() else "Vídeo")

    def create_details_window(self):
        # if exists window
        if hasattr(self, "details_window") and self.details_window.winfo_exists():
            self.details_window.lift()  
            return

        self.details_window = customtkinter.CTkToplevel(self)
        self.details_window.title("Detalhes dos Downloads")
        self.details_window.geometry("600x400")

        details_label = customtkinter.CTkLabel(self.details_window, text="Downloads Detalhados", font=("Arial", 18, "bold"))
        details_label.pack(pady=10)

        # frame
        tree_frame = tkinter.Frame(self.details_window)
        tree_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Configurar o Treeview
        self.tree = ttk.Treeview(tree_frame, columns=("Vídeo", "Progresso", "Status"), show="headings")
        self.tree.heading("Vídeo", text="Vídeo")
        self.tree.heading("Progresso", text="Progresso")
        self.tree.heading("Status", text="Status")
        self.tree.column("Vídeo", anchor="w", width=250)
        self.tree.column("Progresso", anchor="center", width=100)
        self.tree.column("Status", anchor="center", width=100)
        self.tree.pack(expand=True, fill="both")

        # insert treeview
        for video in self.list_videos:
            if not any(self.tree.item(child)["values"][0] == video["name"] for child in self.tree.get_children()):
                self.tree.insert("", "end", values=(video["name"], video["progress"], video["status"]))

    def open_details_window(self):
        self.details_window.configure(open=True)

    def update_progress_details(self, d):
        if d["status"] == "downloading":
            progress = float(re.sub(r"\x1b\[[0-9;]*m", "", d["_percent_str"]).replace("%", "")) / 100
            current_video = self.list_videos[self.current_video - 1]
            current_video["progress"] = f"{int(progress * 100)}%"
            current_video["status"] = "Em andamento"

            if hasattr(self, "tree"):
                self.tree.item(self.tree.get_children()[self.current_video - 1], values=(current_video["name"], current_video["progress"], current_video["status"]))
            self.update_idletasks()

        elif d["status"] == "finished":
            current_video = self.list_videos[self.current_video - 1]
            current_video["progress"] = "100%"
            current_video["status"] = "Concluído"

            if hasattr(self, "tree"):
                self.tree.item(self.tree.get_children()[self.current_video - 1], values=(current_video["name"], current_video["progress"], current_video["status"]))

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            tkinter.messagebox.showwarning("Atenção", "Por favor, insira uma URL válida.")
            return

        self.download_button.configure(state='disabled')
        self.downloader.recipient = self.path_entry.get()

        try:
            self.info_url = self.downloader.get_url_info(url)
        except Exception as e:
            tkinter.messagebox.showerror("Erro ao Obter Informações", f"Não foi possível obter informações da URL:\n{str(e)}")
            self.download_button.configure(state='enabled')
            return
        
        self.total_videos = len(self.info_url)
        self.current_video = 1
        self.status_label.configure(text="Preparando para baixar...")

        if not self.total_videos:
            self.status_label.configure(text="Nenhum vídeo encontrado")
            return

        if self.total_videos == 1:
            self.playlist_label.configure(
                text=f"{self.info_url[0]['name']}"
            )
        else:
            self.playlist_label.configure(
                text=f"Preparando para baixar {self.total_videos} vídeos"
            )
        self.downloader.set_progress_callback(self.update_progress_details)

        # thread
        threading.Thread(target=self._perform_download, daemon=True).start()

    def _perform_download(self):
        try:
            for video_info in self.info_url:
                title = video_info.get("name", "Vídeo Desconhecido")
                url = video_info.get("url")
                if self.switch.get():
                    self.__save_info_url(self.info_url, 'mp3')   
                    self.downloader.download_audio(url)
                else:
                    self.__save_info_url(self.info_url, 'mp4')
                    self.downloader.download_video(url)

                self.current_video += 1
                progress = self.current_video / self.total_videos
                self.progress_bar.set(progress)
                self.status_label.configure(text=f"Baixando {self.current_video}/{self.total_videos}: {title}")
            self.status_label.configure(text="Todos os downloads concluídos!")
        except Exception as e:
            tkinter.messagebox.showerror("Erro no Download", f"Um erro ocorreu durante o download:\n{str(e)}")
            self.progress_bar.set(0)

    # save info videos
    def __save_info_url(self, info_url, type_url):
        for video in info_url:
            video_data = {
                "name": f"{video['name']}.{type_url}",
                "url": video["url"],
                "progress": "0%",
                "status": "Pendente",
            }
            self.list_videos.append(video_data)

            if hasattr(self, "tree"):
                self.tree.insert("", "end", values=(video_data["name"], video_data["progress"], video_data["status"]))


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
