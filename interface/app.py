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
        self.selected_videos = set()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2c2c2c", 
                        foreground="white", 
                        rowheight=25, 
                        fieldbackground="#2c2c2c",
                        font=("Arial", 12))
        style.configure("Treeview.Heading", 
                       font=("Arial", 11, "bold"), 
                       foreground="white", 
                       background="#1a1a1a")
        style.map("Treeview.Heading",
                 background=[("active", "#1a1a1a")],
                 foreground=[("active", "white")])

    def setup_ui(self):
        self.title("YouTube Downloader")
        self.resizable(False, False)

        # sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=7, sticky="ns", padx=10, pady=10)
        self.sidebar_frame.grid_rowconfigure(999, weight=1)

        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Downloader Youtuber", font=("Arial", 24, "bold"), text_color="#3a9bfd", wraplength=200
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

        self.credits_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Projeto criado por", font=("Arial", 14)
        )
        self.credits_label.grid(row=999, column=0, padx=20, pady=(10, 0), sticky="s")

        self.author_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="KaikMcpe12", font=("Arial", 14, "bold")
        )
        self.author_label.grid(row=1000, column=0, padx=20, pady=(0, 20), sticky="s")

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

        # trace variable
        self.url_var = customtkinter.StringVar()
        self.url_entry.configure(textvariable=self.url_var)
        self.url_var.trace_add("write", self.on_url_change)

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

        # verify URL button
        self.verify_button = customtkinter.CTkButton(
            self, text="Verificar URL", font=("Arial", 18), command=lambda: threading.Thread(target=self.verify_url, daemon=True).start()
        )
        self.verify_button.grid(row=3, column=1, padx=20, pady=20, sticky="ew")

        # download button (initially hidden)
        self.download_button = customtkinter.CTkButton(
            self, text="Baixar Selecionados", font=("Arial", 18), command=self.start_download
        )
        self.download_button.grid(row=3, column=1, padx=20, pady=20, sticky="ew")
        self.download_button.grid_remove()

        # progress
        self.progress_frame = customtkinter.CTkFrame(self)
        self.progress_frame.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.playlist_label = customtkinter.CTkLabel(self.progress_frame, text="")
        self.playlist_label.grid(row=0, column=0, padx=10, pady=5)

        self.progress_bar = customtkinter.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.status_label = customtkinter.CTkLabel(self.progress_frame, text="Preparado para baixar", font=("Arial", 14))
        self.status_label.grid(row=2, column=0, padx=10, pady=5)

        # details frame
        self.details_frame = customtkinter.CTkFrame(self)
        self.details_frame.grid(row=5, column=1, padx=20, pady=10, sticky="nsew")
        self.details_frame.grid_columnconfigure(0, weight=1)

        # header frame for details
        self.details_header_frame = customtkinter.CTkFrame(self.details_frame)
        self.details_header_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        details_label = customtkinter.CTkLabel(self.details_header_frame, text="Vídeos Disponíveis", font=("Arial", 16, "bold"))
        details_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.select_all_var = customtkinter.BooleanVar(value=True)
        self.select_all_checkbox = customtkinter.CTkCheckBox(
            self.details_header_frame,
            text="Selecionar Todos",
            command=self.toggle_all_videos,
            variable=self.select_all_var
        )
        self.select_all_checkbox.grid(row=0, column=1, padx=10, pady=5)

        # tree frame
        tree_frame = tkinter.Frame(self.details_frame)
        tree_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # treeview
        self.tree = ttk.Treeview(tree_frame, columns=("Checkbox", "Vídeo", "Progresso", "Status"), show="headings", height=5)
        self.tree.heading("Checkbox", text="")
        self.tree.heading("Vídeo", text="Vídeo")
        self.tree.heading("Progresso", text="Progresso")
        self.tree.heading("Status", text="Status")
        self.tree.column("Checkbox", anchor="center", width=30)
        self.tree.column("Vídeo", anchor="w", width=250)
        self.tree.column("Progresso", anchor="center", width=100)
        self.tree.column("Status", anchor="center", width=100)
        self.tree.pack(expand=True, fill="both")
        
        # bind click event
        self.tree.bind('<Button-1>', self.handle_click)
    
    def on_url_change(self, *args):
        # show verify button
        self.verify_button.grid()
        self.download_button.grid_remove()
        
        # clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # reset labels and progress
        self.playlist_label.configure(text="")
        self.status_label.configure(text="Preparado para baixar")
        self.progress_bar.set(0)
        
        # clear lists
        self.list_videos.clear()
        self.selected_videos.clear()

    def handle_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            return
        
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return

        column = self.tree.identify('column', event.x, event.y)
        if column == '#1':
            current_values = self.tree.item(item)['values']
            is_checked = current_values[0] == '☒'
            new_checkbox = '☐' if is_checked else '☒'
            
            values = list(current_values)
            values[0] = new_checkbox
            self.tree.item(item, values=values)
            
            # udpate select videos set
            idx = self.tree.index(item)
            if new_checkbox == '☒':
                self.selected_videos.add(idx)
            else:
                self.selected_videos.discard(idx)
                self.select_all_var.set(False)
            
            # toggle select all checkbox
            total_selected = len(self.selected_videos)
            if total_selected == 0:
                self.playlist_label.configure(text="Nenhum vídeo selecionado")
            elif total_selected == 1:
                self.playlist_label.configure(text="1 vídeo selecionado")
            else:
                self.playlist_label.configure(text=f"{total_selected} vídeos selecionados")

    def toggle_all_videos(self):
        is_checked = self.select_all_var.get()
        checkbox_value = '☒' if is_checked else '☐'
        
        for item in self.tree.get_children():
            current_values = list(self.tree.item(item)['values'])
            current_values[0] = checkbox_value
            self.tree.item(item, values=current_values)
            
            # update selected videos
            idx = self.tree.index(item)
            if is_checked:
                self.selected_videos.add(idx)
            else:
                self.selected_videos.discard(idx)

    def verify_url(self):
        url = self.url_var.get()

        if not url:
            tkinter.messagebox.showwarning("Atenção", "Por favor, insira uma URL válida.")
            return

        try:
            #disabled verify button
            self.verify_button.configure(state='disabled')
            self.info_url = self.downloader.get_url_info(url)
        except Exception as e:
            tkinter.messagebox.showerror("Erro ao Obter Informações", f"Não foi possível obter informações da URL:\n{str(e)}")
            return

        # enable verify button
        self.verify_button.configure(state='normal')

        # clear previous items
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.list_videos.clear()
        self.selected_videos.clear()
        # add videos to tree
        for idx, video in enumerate(self.info_url):
            video_data = {
                "name": video['name'],
                "url": video["url"],
                "progress": "0%",
                "status": "Pendente"
            }
            self.list_videos.append(video_data)
            self.tree.insert("", "end", values=('☒', video_data["name"], video_data["progress"], video_data["status"]))
            self.selected_videos.add(idx)

        self.verify_button.grid_remove()
        self.download_button.grid()

        total_videos = len(self.info_url)
        self.playlist_label.configure(
            text=f"{total_videos} vídeo{'s' if total_videos > 1 else ''} encontrado{'s' if total_videos > 1 else ''}"
        )

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

    def update_progress_details(self, d):
        if d["status"] == "downloading":
            progress = float(re.sub(r"\x1b\[[0-9;]*m", "", d["_percent_str"]).replace("%", "")) / 100
            current_video = self.list_videos[self.current_video - 1]
            current_video["progress"] = f"{int(progress * 100)}%"
            current_video["status"] = "Em andamento"

            values = list(self.tree.item(self.tree.get_children()[self.current_video - 1])['values'])
            values[2:] = [current_video["progress"], current_video["status"]]
            self.tree.item(self.tree.get_children()[self.current_video - 1], values=values)
            self.update_idletasks()

        elif d["status"] == "finished":
            current_video = self.list_videos[self.current_video - 1]
            current_video["progress"] = "100%"
            current_video["status"] = "Concluído"

            values = list(self.tree.item(self.tree.get_children()[self.current_video - 1])['values'])
            values[2:] = [current_video["progress"], current_video["status"]]
            self.tree.item(self.tree.get_children()[self.current_video - 1], values=values)

    def start_download(self):
        url = self.url_var.get()
        if not url:
            tkinter.messagebox.showwarning("Atenção", "Por favor, insira uma URL válida.")
            return

        # if not selected videos
        if not self.selected_videos:
            tkinter.messagebox.showwarning("Atenção", "Por favor, selecione pelo menos um vídeo para download.")
            return

        self.download_button.configure(state='disabled')
        self.downloader.recipient = self.path_entry.get()

        # filter videos
        selected_info = [self.info_url[i] for i in self.selected_videos]
        
        # update videos count
        self.total_videos = len(selected_info)
        self.current_video = 1
        self.status_label.configure(text="Preparando para baixar...")

        if not self.total_videos:
            self.status_label.configure(text="Nenhum vídeo selecionado")
            return

        if self.total_videos == 1:
            self.playlist_label.configure(
                text=f"{selected_info[0]['name']}"
            )
        else:
            self.playlist_label.configure(
                text=f"Preparando para baixar {self.total_videos} vídeos"
            )
        self.downloader.set_progress_callback(self.update_progress_details)

        # clear previus items
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.list_videos.clear()

        # download
        if self.switch.get():
            self.__save_info_url(selected_info, 'mp3')
        else:
            self.__save_info_url(selected_info, 'mp4')

        # update info_url
        self.info_url = selected_info

        # thread
        threading.Thread(target=self._perform_download, daemon=True).start()

    def _perform_download(self):
        try:
            for video_info in self.info_url:
                title = video_info.get("name", "Vídeo Desconhecido")
                url = video_info.get("url")
                if self.switch.get():
                    self.downloader.download_audio(url)
                else:
                    self.downloader.download_video(url)

                self.current_video += 1
                progress = self.current_video / self.total_videos
                self.progress_bar.set(progress)
                self.status_label.configure(text=f"Baixando {self.current_video}/{self.total_videos}: {title}")
            
            # enable download button
            self.download_button.configure(state='normal')
            self.verify_button.grid()
            self.download_button.grid_remove()
            self.status_label.configure(text="Todos os downloads concluídos!")
            self.progress_bar.set(0)
            
        except Exception as e:
            tkinter.messagebox.showerror("Erro no Download", f"Um erro ocorreu durante o download, tente um link diferente ou verifique sua internet:\n{str(e)}")
            self.progress_bar.set(0)

            # enable donload button
            self.download_button.configure(state='normal')
            self.verify_button.grid()
            self.download_button.grid_remove()

    def __save_info_url(self, info_url, type_url):
        for video in info_url:
            video_data = {
                "name": f"{video['name']}.{type_url}",
                "url": video["url"],
                "progress": "0%",
                "status": "Pendente"
            }
            self.list_videos.append(video_data)
            self.tree.insert("", "end", values=('☒', video_data["name"], video_data["progress"], video_data["status"]))


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()