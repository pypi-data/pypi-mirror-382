import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import sys
import yt_dlp
import threading
import re
from typing import Dict, Union, Callable

# --- Sabitler ve Ayarlar ---
# yt-dlp format kodlarına karşılık gelen çözünürlükler.
RESOLUTIONS: Dict[str, str] = {
    "En Yüksek Kalite (MP4)": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "1080p (MP4)": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "720p (MP4)": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "480p (MP4)": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]", 
    "360p (MP4)": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]", 
    "240p (MP4)": "bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]", 
    "144p (MP4)": "bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]", 
    "Sadece Ses (MP3)": "bestaudio/best",
}

# --- Sürüm Bilgisi Fonksiyonu ---
def get_yt_dlp_version() -> (bool, str):
    """yt-dlp'nin kurulu sürüm bilgisini döndürür."""
    try:
        current_version = yt_dlp.version.__version__
        return True, f"Kurulu Sürüm: **{current_version}**"
    except ImportError:
        return False, "**HATA:** 'yt-dlp' modülü kurulu değil."
    except Exception as e:
        return False, f"**HATA:** Sürüm alınırken beklenmeyen bir hata oluştu: {e}"

# --- Güvenlik: Dosya Adı Temizleme ---
def sanitize_filename(title: str, max_length: int = 100) -> str:
    """Video başlığını, dosya sistemi uyumlu ve güvenli bir isme dönüştürür."""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
    sanitized = sanitized.strip()
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    return sanitized[:max_length].strip()

# --- İndirme İşlemi ve Optimizasyon ---
def indir_video(
    url: str,
    output_dir: str,
    format_key: str,
    status_callback: Callable[[str, Union[float, None]], None]
) -> str:
    """Belirtilen URL'deki videoyu indirir ve durumu callback ile günceller."""
    
    format_string = RESOLUTIONS.get(format_key, RESOLUTIONS["En Yüksek Kalite (MP4)"])
    is_audio_only = "Sadece Ses" in format_key

    # İndirme ilerlemesini yakalamak için hook fonksiyonu
    def progress_hook(d: dict):
        if d['status'] == 'downloading':
            p = d.get('fragment_index', 0) / d.get('n_fragments', 1) 
            speed_str = d.get('_eta_str', 'N/A')
            # GUI'ye güvenli aktarım için status_callback kullanılır.
            status_callback(
                f"İndiriliyor: {d['_percent_str']} - Tahmini Kalan: {speed_str}", p
            )
        elif d['status'] == 'finished':
            status_callback("İndirme Tamamlandı. Dosya İşleniyor...", 1.0)
        elif d['status'] == 'postprocessing':
            status_callback("Dosya İşleniyor (Video/Ses Birleştiriliyor)...", 1.0)

    # yt-dlp indirme seçenekleri (Best Practices)
    ydl_opts = {
        'format': format_string,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'), 
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4', 
        'external_downloader': 'ffmpeg', # Hız için ffmpeg (mevcutsa)
        'quiet': True,
        'no_warnings': True,
    }

    if is_audio_only:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['outtmpl'] = os.path.join(output_dir, '%(title)s.mp3'),
        ydl_opts['postprocessors'] = [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', 
            },
            {'key': 'FFmpegMetadata'},
        ]
        ydl_opts['merge_output_format'] = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. Video bilgisini al (Başlığı güvenli dosya adı için)
            info_dict = ydl.extract_info(url, download=False)
            video_title = sanitize_filename(info_dict.get('title', 'Unknown_Video'))
            
            status_callback(
                f"Video Bilgisi Alındı: '{video_title}'. İndirme Başlıyor...", 0
            )

            # 2. İndirme işlemini başlat
            ydl.download([url])

        # Başarılı sonlanma mesajı
        ext = "mp3" if is_audio_only else "mp4"
        final_path = os.path.join(output_dir, f"{video_title}.{ext}")
        
        status_callback(
            f"BAŞARILI: '{video_title}.{ext}' dosyası kaydedildi: {final_path}", 1.0
        )
        return f"İndirme başarıyla tamamlandı: {final_path}"

    except yt_dlp.DownloadError as e:
        msg = f"İndirme Hatası: {e}"
        status_callback(msg, 0)
        return msg
    except Exception as e:
        msg = f"Beklenmeyen Hata: {e}"
        status_callback(msg, 0)
        return msg

# --- GUI Sınıfı (Modern ve Duyarlı Tasarım) ---

class DownloaderGUI:
    def __init__(self, master: tk.Tk, version_msg: str):
        self.master = master
        master.title("YouTube İndirici Atilla (v4) - Python Kod Asistanı Geliştirme")
        
        # Duyarlı Pencere Ayarları
        master.grid_columnconfigure(0, weight=1) 
        master.grid_rowconfigure(0, weight=1) 

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Accent.TButton", font=('Arial', 10, 'bold'), foreground='white', background='#4CAF50')

        # --- Değişkenler ---
        self.video_url = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.getcwd())
        self.selected_resolution = tk.StringVar(value="En Yüksek Kalite (MP4)")
        self.status_text = tk.StringVar(value=f"Hazır. {version_msg.replace('**', '')}")

        # --- Ana Çerçeve ---
        main_frame = ttk.Frame(master, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # 1. URL Girişi
        ttk.Label(main_frame, text="YouTube URL'si:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        url_entry = ttk.Entry(main_frame, textvariable=self.video_url, width=60)
        url_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # 2. Seçenekler (Çözünürlük ve Kayıt Yeri)
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        options_frame.grid_columnconfigure(1, weight=1)

        # Çözünürlük Seçimi (Sol)
        ttk.Label(options_frame, text="Çözünürlük:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        resolution_options = list(RESOLUTIONS.keys())
        resolution_menu = ttk.Combobox(options_frame, textvariable=self.selected_resolution, 
                                       values=resolution_options, state="readonly", width=30)
        resolution_menu.grid(row=1, column=0, sticky="w", padx=(0, 10))
        resolution_menu.current(0) 

        # Kaydedilecek Yer Seçimi (Sağ)
        ttk.Label(options_frame, text="Kaydedilecek Yer:").grid(row=0, column=1, sticky="w")
        dir_entry = ttk.Entry(options_frame, textvariable=self.output_dir, state="readonly")
        dir_entry.grid(row=1, column=1, sticky="ew")

        dir_button = ttk.Button(options_frame, text="Seç", command=self.select_output_dir)
        dir_button.grid(row=1, column=2, sticky="e", padx=(5, 0))

        # 3. Buton ve İlerleme Çubuğu
        download_button = ttk.Button(main_frame, text="İndir", command=self.start_download, style="Accent.TButton")
        download_button.grid(row=3, column=0, sticky="ew", pady=(10, 5))
        self.download_button = download_button

        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=4, column=0, sticky="ew", pady=(0, 5))

        # 4. Durum Etiketi (Anlık Durumu Gösterir)
        status_label = ttk.Label(main_frame, textvariable=self.status_text, wraplength=500, justify="left")
        status_label.grid(row=5, column=0, sticky="w", pady=(5, 0))
        self.status_label = status_label


    def select_output_dir(self):
        """Kullanıcının dosya kaydetme dizinini seçmesini sağlar."""
        new_dir = filedialog.askdirectory(initialdir=self.output_dir.get())
        if new_dir:
            self.output_dir.set(new_dir)
            self.update_status(f"Kaydedilecek dizin ayarlandı: {new_dir}")

    def update_status(self, message: str, progress: Union[float, None] = None):
        """GUI'daki durumu ve ilerleme çubuğunu günceller."""
        self.status_text.set(message)
        if progress is not None:
            self.progress_bar['value'] = int(progress * 100)
            
        if "BAŞARILI" in message or "HATA" in message or "Hazır" in message:
            # Ana thread'de butonu etkinleştirme
            self.master.after(10, lambda: self.download_button.config(state='normal'))
            if "BAŞARILI" in message:
                self.progress_bar['value'] = 100
            elif "HATA" in message:
                 self.progress_bar['value'] = 0

    def start_download(self):
        """İndirme işlemini ayrı bir thread'de başlatır."""
        url = self.video_url.get()
        output_dir = self.output_dir.get()
        resolution = self.selected_resolution.get()

        if not url or ("youtube.com/" not in url and "youtu.be/" not in url):
            messagebox.showerror("Hata", "Lütfen geçerli bir YouTube URL'si girin.")
            return

        self.download_button['state'] = 'disabled'
        self.progress_bar['value'] = 0
        self.update_status("İndirme işlemi başlatılıyor...", 0)

        # Performans için threading
        threading.Thread(
            target=self.run_download_in_thread,
            args=(url, output_dir, resolution),
            daemon=True
        ).start()

    def run_download_in_thread(self, url: str, output_dir: str, resolution: str):
        """İndirme fonksiyonunu çalıştırır ve sonucu GUI'ye bildirir."""
        
        # Durum güncellemelerini GUI thread'inde güvenli bir şekilde yap
        result_msg = indir_video(url, output_dir, resolution, 
                                 lambda msg, p=None: self.master.after(0, self.update_status, msg, p))
        
        if "BAŞARILI" in result_msg:
             self.master.after(0, lambda: messagebox.showinfo("Başarılı", result_msg.replace("BAŞARILI: ", "")))
        elif "Hata" in result_msg:
             self.master.after(0, lambda: messagebox.showerror("Hata", result_msg))
        
        # Son olarak GUI'yi hazır hale getir
        is_ok, status_msg = get_yt_dlp_version()
        self.master.after(100, lambda: self.update_status(f"Hazır. {status_msg.replace('**', '')}"))


# --- Ana Çalıştırma Bloğu (Entry Point için main() fonksiyonu) ---

def main():
    """Uygulamanın başlangıç noktası: CLI veya GUI modunu seçer."""
    is_ok, status_msg = get_yt_dlp_version()

    if not is_ok and "HATA" in status_msg:
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Kurulum Hatası", status_msg.replace('**', ''))
        sys.exit(1)

    if len(sys.argv) > 1:
        # CLI Modu
        print(f"Sürüm Durumu: {status_msg.replace('**', '')}")

        video_url = sys.argv[1]
        print(f"CLI modu: URL '{video_url}' indiriliyor.")

        default_dir = os.getcwd()

        def cli_status_callback(msg: str, progress: Union[float, None] = None):
            """CLI için basit durum geri çağrısı."""
            if "BAŞARILI" in msg or "HATA" in msg:
                print(msg)
            elif progress is not None and "İndiriliyor" in msg:
                 if int(progress * 100) % 10 == 0:
                      print(f"\r{msg.split(' - ')[0]}", end='', flush=True)

        print(indir_video(video_url, default_dir, "En Yüksek Kalite (MP4)", cli_status_callback))
    else:
        # GUI Modu
        root = tk.Tk()
        app = DownloaderGUI(root, status_msg)
        root.mainloop()

if __name__ == "__main__":
    main() # main fonksiyonunu çağırır.