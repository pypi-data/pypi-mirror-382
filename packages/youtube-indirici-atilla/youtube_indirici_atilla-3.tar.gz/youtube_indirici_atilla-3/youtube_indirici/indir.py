import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import sys
import yt_dlp
import threading
import re  # Güvenli dosya adları için

# --- Sabitler ve Ayarlar ---
# yt-dlp'deki format kodlarına karşılık gelen çözünürlükler.
# 'best' ve 'bestvideo[height]+bestaudio' en iyi kaliteyi sağlar.
# Aşağıdakiler, genellikle belirli video yüksekliklerine (p) karşılık gelen
# ve sadece video + sesi birleştirmeyi zorlayan formatlardır.
RESOLUTIONS = {
    "En Yüksek Kalite (MP4)": "bestvideo[ext=mp4]+bestaudio/best[ext=mp4]", # Birleştirme ve MP4'e zorlama
    "1080p (MP4)": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "720p (MP4)": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "480p (MP4)": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "360p (MP4)": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "240p (MP4)": "bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "144p (MP4)": "bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "Sadece Ses (MP3)": "bestaudio/best", # Varsayılan olarak MP3'e dönüştürülür
}

# --- Sürüm Bilgisi Fonksiyonu (Sürüm Kontrolü Kaldırıldı) ---

def get_yt_dlp_version():
    """yt-dlp'nin kurulu sürüm bilgisini döndürür."""
    try:
        # Kurulum hatası vermemesi için sadece sürümü al
        current_version = yt_dlp.version.__version__
        return True, f"Kurulu Sürüm: **{current_version}**"
    except ImportError:
        return False, "**HATA:** 'yt-dlp' modülü kurulu değil. Lütfen 'pip install yt-dlp' komutunu çalıştırın."
    except Exception as e:
        return False, f"**HATA:** Sürüm alınırken beklenmeyen bir hata oluştu: {e}"

# --- İndirme İşlemi ---

def sanitize_filename(title, max_length=100):
    """
    Video başlığını güvenli bir dosya adına dönüştürür.
    Geçersiz karakterleri kaldırır ve uzunluğu sınırlar.
    """
    # Windows'ta dosya adı için geçersiz karakterleri değiştir
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
    # Unicode olmayan karakterleri (örn. emojiler) kaldır
    sanitized = sanitized.encode('ascii', 'ignore').decode('ascii').strip()
    return sanitized[:max_length].strip()

def indir_video(url, output_dir, format_key, status_callback):
    """
    Belirtilen URL'deki videoyu belirtilen çözünürlükte indirir.
    status_callback: GUI'yi güncellemek için bir fonksiyon.
    """
    format_string = RESOLUTIONS.get(format_key, RESOLUTIONS["En Yüksek Kalite (MP4)"])

    # İndirme ilerlemesini yakalamak için hook fonksiyonu
    def progress_hook(d):
        if d['status'] == 'downloading':
            p = d.get('fragment_index', 0) / d.get('n_fragments', 1)
            # İlerleme çubuğunu ve metni güncelle
            speed_str = d.get('_eta_str', 'N/A')
            status_callback(f"İndiriliyor: {d['_percent_str']} - Tahmini Kalan: {speed_str}", p)
        elif d['status'] == 'finished':
            # Dosya birleştirme (post-processing) aşaması
            if 'info_dict' in d:
                # Video başlığını al ve güvenli bir dosya adı oluştur
                video_title = sanitize_filename(d['info_dict']['title'])
                status_callback(f"İndirme Tamamlandı. Dosya İşleniyor: {video_title}.mp4", 1.0)
            else:
                status_callback("İndirme Tamamlandı. Dosya İşleniyor...", 1.0)
        elif d['status'] == 'postprocessing':
            status_callback("Dosya İşleniyor (Video ve Ses Birleştiriliyor)...", 1.0)

    # İndirme seçenekleri
    ydl_opts = {
        'format': format_string,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'), # Dosya adını otomatik al
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4', # Birleştirilmiş çıktı formatı
        'external_downloader': 'ffmpeg', # Hız için harici indirici kullanma (kullanıcının kurulu olması gerekir)
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}
            if "Sadece Ses" in format_key else
            {'key': 'FFmpegVideoRemuxer', 'preferedformat': 'mp4'}
        ],
        'quiet': True,
        'no_warnings': True,
    }

    if "Sadece Ses" in format_key:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['outtmpl'] = os.path.join(output_dir, '%(title)s.%(ext)s')
        ydl_opts['postprocessors'] = [
            {'key': 'FFmpegExtractAudio',
             'preferredcodec': 'mp3',
             'preferredquality': '192'},
            {'key': 'FFmpegMetadata'},
        ]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # İndirme başlamadan önce bilgi al
            info_dict = ydl.extract_info(url, download=False)
            video_title = sanitize_filename(info_dict.get('title', 'Unknown_Video'))
            status_callback(f"Video Bilgisi Alındı: '{video_title}'. İndirme Başlıyor...", 0)

            # İndirme işlemini başlat
            ydl.download([url])

        # Başarılı sonlanma mesajı
        final_path = os.path.join(output_dir, f"{video_title}.mp4")
        if "Sadece Ses" in format_key:
             # Ses için post-processor'daki varsayılan uzantı .mp3'tür.
             final_path = os.path.join(output_dir, f"{video_title}.mp3")
             
        status_callback(f"BAŞARILI: '{video_title}' dosyası buraya kaydedildi: {final_path}", 1.0)
        return f"İndirme başarıyla tamamlandı: {final_path}"

    except yt_dlp.DownloadError as e:
        msg = f"İndirme Hatası: {e}"
        status_callback(msg, 0)
        return msg
    except Exception as e:
        msg = f"Beklenmeyen Hata: {e}"
        status_callback(msg, 0)
        return msg

# --- GUI Sınıfı ---

class DownloaderGUI:
    def __init__(self, master, version_msg):
        self.master = master
        master.title("YouTube İndirici Atilla (Python Kod Asistanı Geliştirme)")
        
        # Pencereyi duyarlı hale getir
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(2, weight=1) # Ana çerçeve için yer aç

        # ttk stilini ayarla (Daha modern bir görünüm için, ttkbootstrap önerilir,
        # ancak standart ttk ile de iyileştirmeler yapabiliriz.)
        style = ttk.Style()
        style.theme_use("clam") # 'clam', 'alt', 'default' deneyin

        # --- Değişkenler ---
        self.video_url = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.getcwd()) # Varsayılan: Mevcut dizin
        self.selected_resolution = tk.StringVar(value="En Yüksek Kalite (MP4)")
        self.status_text = tk.StringVar(value=f"Hazır. {version_msg.replace('**', '')}")

        # --- Ana Çerçeve (Tüm bileşenleri içerir) ---
        main_frame = ttk.Frame(master, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1) # Sütunu duyarlı yap

        # --- 1. Bölüm: URL Girişi ---
        url_label = ttk.Label(main_frame, text="YouTube URL'si:")
        url_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        url_entry = ttk.Entry(main_frame, textvariable=self.video_url, width=50)
        url_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(0, 10))
        
        # --- 2. Bölüm: Çözünürlük ve Çıktı ---
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        options_frame.grid_columnconfigure(1, weight=1) # Dosya yolu girdisini duyarlı yap

        # Çözünürlük Seçimi
        resolution_label = ttk.Label(options_frame, text="Çözünürlük:")
        resolution_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        resolution_options = list(RESOLUTIONS.keys())
        resolution_menu = ttk.Combobox(options_frame, textvariable=self.selected_resolution, values=resolution_options, state="readonly", width=30)
        resolution_menu.grid(row=1, column=0, sticky="w", padx=(0, 10))
        resolution_menu.current(0) # İlk seçeneği varsayılan yap

        # Çıktı Dizini Seçimi
        dir_label = ttk.Label(options_frame, text="Kaydedilecek Yer:")
        dir_label.grid(row=0, column=1, sticky="w")

        dir_entry = ttk.Entry(options_frame, textvariable=self.output_dir, state="readonly")
        dir_entry.grid(row=1, column=1, sticky="ew")

        dir_button = ttk.Button(options_frame, text="Seç", command=self.select_output_dir, width=6)
        dir_button.grid(row=1, column=2, sticky="e", padx=(5, 0))

        # --- 3. Bölüm: İndirme Butonu ve İlerleme ---
        download_button = ttk.Button(main_frame, text="İndir", command=self.start_download, style="Accent.TButton")
        download_button.grid(row=3, column=0, sticky="ew", pady=(10, 5))
        self.download_button = download_button # Durumu güncellemek için referansı sakla

        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.grid(row=4, column=0, sticky="ew", pady=(0, 5))

        # --- 4. Bölüm: Durum Çubuğu ---
        status_label = ttk.Label(main_frame, textvariable=self.status_text, wraplength=400, justify="left")
        status_label.grid(row=5, column=0, sticky="w", pady=(5, 0))
        self.status_label = status_label


    def select_output_dir(self):
        """Kullanıcının dosya kaydetme dizinini seçmesini sağlar."""
        # Burada sadece dizin seçimi yapıyoruz
        new_dir = filedialog.askdirectory(initialdir=self.output_dir.get())
        if new_dir:
            self.output_dir.set(new_dir)
            self.update_status(f"Kaydedilecek dizin ayarlandı: {new_dir}")

    def update_status(self, message, progress=None):
        """GUI'daki durum çubuğunu ve ilerleme çubuğunu günceller."""
        self.status_text.set(message)
        if progress is not None:
            # 0.0 ile 1.0 arasındaki değeri 0-100'e dönüştür
            self.progress_bar['value'] = int(progress * 100)
            
        # Eğer indirme bitmişse (BAŞARILI veya HATA), butonu tekrar etkinleştir
        if "BAŞARILI" in message or "HATA" in message or "Hazır" in message:
            self.download_button['state'] = 'normal'
            if "BAŞARILI" in message:
                self.progress_bar['value'] = 100
            elif "HATA" in message:
                 self.progress_bar['value'] = 0


    def start_download(self):
        """İndirme işlemini ayrı bir thread'de başlatır."""
        url = self.video_url.get()
        output_dir = self.output_dir.get()
        resolution = self.selected_resolution.get()

        if not url:
            messagebox.showerror("Hata", "Lütfen bir YouTube URL'si girin.")
            return

        # URL geçerliliği için basit bir kontrol
        if "youtube.com/" not in url and "youtu.be/" not in url:
             messagebox.showerror("Hata", "Geçersiz YouTube URL'si.")
             return

        # İndirme işlemini devre dışı bırak
        self.download_button['state'] = 'disabled'
        self.progress_bar['value'] = 0
        self.update_status("İndirme işlemi başlatılıyor...", 0)

        # Threading ile GUI'nin donmasını önle
        threading.Thread(
            target=self.run_download_in_thread,
            args=(url, output_dir, resolution),
            daemon=True
        ).start()

    def run_download_in_thread(self, url, output_dir, resolution):
        """İndirme fonksiyonunu çalıştırır ve sonucu GUI'ya bildirir."""
        # indir_video, durum güncellemeleri için update_status'u kullanacak
        result_msg = indir_video(url, output_dir, resolution, self.update_status)
        
        # İşlem bittiğinde son mesajı göster
        if "BAŞARILI" in result_msg:
             messagebox.showinfo("Başarılı", result_msg.replace("BAŞARILI: ", ""))
        elif "Hata" in result_msg:
             messagebox.showerror("Hata", result_msg)
        
        # Son olarak GUI'yi hazır hale getir
        is_ok, status_msg = get_yt_dlp_version()
        self.master.after(100, lambda: self.update_status(f"Hazır. {status_msg.replace('**', '')}"))


# --- Ana Çalıştırma Bloğu ---

if __name__ == "__main__":
    is_ok, status_msg = get_yt_dlp_version()

    # Hata durumunda (Modül kurulu değilse) Tkinter messagebox ile bilgi ver
    if not is_ok and "HATA" in status_msg:
        temp_root = tk.Tk()
        temp_root.withdraw()  # Ana pencereyi gizle
        messagebox.showerror("Kurulum Hatası", status_msg.replace('**', ''))
        sys.exit(1)

    # Eğer argüman varsa CLI modunda çalış
    if len(sys.argv) > 1:
        # CLI Modunda da sürüm bilgisini yaz
        print(f"Sürüm Durumu: {status_msg.replace('**', '')}")

        video_url = sys.argv[1]
        print(f"CLI modu: URL '{video_url}' indiriliyor.")

        # CLI'da varsayılan dosya yolu: mevcut dizin
        default_dir = os.getcwd()

        # CLI için basit bir durum geri çağrısı
        def cli_status_callback(msg, progress=None):
            if "BAŞARILI" in msg or "HATA" in msg:
                print(msg)
            elif progress is not None and progress > 0.0:
                 # Yüksek detaylı ilerleme mesajlarını CLI'da bastırma
                 if "İndiriliyor" in msg:
                      # Sadece önemli anları veya daha az sıklıkta olanları yazdır.
                      if progress * 100 % 10 < 0.1: # Her %10'da bir
                           print(f"\r{msg.split(' - ')[0]}", end='', flush=True)

        print(indir_video(video_url, default_dir, "En Yüksek Kalite (MP4)", cli_status_callback))
    else:
        # Argüman yoksa GUI'yi başlat
        root = tk.Tk()
        app = DownloaderGUI(root, status_msg)
        root.mainloop()