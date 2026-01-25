import customtkinter as ctk
import socket
import threading
import time
import struct
from collections import deque

# --- CONFIGURATION ---
class AppConfig:
    UDP_IP: str = "127.0.0.1"
    UDP_PORT: int = 5005
    WINDOW_SIZE: str = "1000x700" 
    
    # Modern Renk Paleti (Cyberpunk / Aviation)
    COLOR_BG = "#0B0B0B"        
    COLOR_PANEL = "#171717"     
    COLOR_ACCENT = "#00ADB5"    # Cyan
    COLOR_TEXT = "#EEEEEE"      
    COLOR_SUCCESS = "#00FF41"   # Yeşil
    COLOR_WARNING = "#FFB100"   # Sarı
    COLOR_DANGER = "#FF2E2E"    # Kırmızı
    
    FONT_MAIN = "Roboto"
    FONT_DIGITAL = "Orbitron"   
    FONT_MONO = "Consolas"

class FlightApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Pencere Hep Üstte (Video kaydı için)
        self.attributes('-topmost', True) 
        
        # Pencere Ayarları
        self.title("FLIGHT TELEMETRY SYSTEM - PRO")
        self.geometry(AppConfig.WINDOW_SIZE)
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=AppConfig.COLOR_BG)

        # Veri Yapıları
        self.graph_data = deque([0]*60, maxlen=60) 
        self.running = True
        
        # Arayüzü Kur
        self.setup_ui()
        
        # Bağlantı
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((AppConfig.UDP_IP, AppConfig.UDP_PORT))
        self.sock.settimeout(0.05) 
        
        self.thread = threading.Thread(target=self.listen_udp, daemon=True)
        self.thread.start()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=3) # Sol taraf geniş
        self.grid_columnconfigure(1, weight=1) # Sağ taraf dar
        self.grid_rowconfigure(0, weight=1)

        # --- SOL PANEL (Grafik ve Loglar) ---
        self.frame_left = ctk.CTkFrame(self, fg_color=AppConfig.COLOR_PANEL, corner_radius=15)
        self.frame_left.grid(row=0, column=0, sticky="nswe", padx=15, pady=15)
        
        # Başlık
        ctk.CTkLabel(self.frame_left, text="VERTICAL PROFILE ANALYZER", 
                     font=(AppConfig.FONT_DIGITAL, 20, "bold"), text_color=AppConfig.COLOR_ACCENT).pack(pady=(20, 10))
        
        # Grafik Alanı
        self.canvas_bg = "#0f111a"
        self.canvas = ctk.CTkCanvas(self.frame_left, bg=self.canvas_bg, height=350, highlightthickness=0)
        self.canvas.pack(fill="x", padx=20, pady=10)
        
        # Log Terminali
        ctk.CTkLabel(self.frame_left, text="SYSTEM EVENTS / LOGS", 
                     font=(AppConfig.FONT_MAIN, 12, "bold"), text_color="gray", anchor="w").pack(pady=(20,5), padx=20, fill="x")
        
        self.log_box = ctk.CTkTextbox(self.frame_left, height=150, 
                                      fg_color="#000000", text_color=AppConfig.COLOR_SUCCESS, 
                                      font=(AppConfig.FONT_MONO, 12), border_width=1, border_color="#333333")
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # --- SAĞ PANEL (Telemetri Kartları) ---
        self.frame_right = ctk.CTkFrame(self, fg_color=AppConfig.COLOR_PANEL, corner_radius=15)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=(0, 15), pady=15)

        ctk.CTkLabel(self.frame_right, text="LIVE DATA", font=(AppConfig.FONT_DIGITAL, 24, "bold"), text_color="white").pack(pady=25)

        # Kartlar
        self.lbl_vspeed = self.create_modern_card(self.frame_right, "V-SPEED (FPM)", AppConfig.COLOR_ACCENT)
        self.lbl_radio = self.create_modern_card(self.frame_right, "RADIO ALT (FT)", AppConfig.COLOR_WARNING)
        self.lbl_gforce = self.create_modern_card(self.frame_right, "G-FORCE LOAD", "#E056FD")
        
        # --- DURUM VE PUAN ALANI (Burayı değiştirdik) ---
        
        # 1. Uçuş Durumu (Kutu Şeklinde)
        self.lbl_flight_state = ctk.CTkLabel(self.frame_right, text="PARKED", 
                                             font=(AppConfig.FONT_MAIN, 16, "bold"), 
                                             fg_color="#333333", text_color="white", corner_radius=8, width=150, height=35)
        self.lbl_flight_state.pack(pady=(40, 5)) # Alt boşluğu azalttık

        # 2. PUAN (Hemen Altına)
        # Başlangıçta boş veya çizgi olacak
        self.lbl_score_title = ctk.CTkLabel(self.frame_right, text="LANDING GRADE", font=(AppConfig.FONT_MAIN, 10), text_color="gray")
        self.lbl_score_title.pack(pady=(0,0))
        
        self.lbl_score = ctk.CTkLabel(self.frame_right, text="---", 
                                       font=(AppConfig.FONT_DIGITAL, 36, "bold"), text_color="gray")
        self.lbl_score.pack(pady=(0, 20))

        # İlk çizim
        self.draw_grid()

    def create_modern_card(self, parent, title, color):
        frame = ctk.CTkFrame(parent, fg_color="#222222", border_width=1, border_color="#333333", corner_radius=10)
        frame.pack(pady=10, padx=15, fill="x")
        ctk.CTkLabel(frame, text=title, font=(AppConfig.FONT_MAIN, 11), text_color="gray").pack(pady=(10,0))
        label = ctk.CTkLabel(frame, text="---", font=(AppConfig.FONT_DIGITAL, 32, "bold"), text_color=color)
        label.pack(pady=(0, 10))
        return label

    def log_message(self, msg):
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")

    def draw_grid(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10: w, h = 600, 300 

        self.canvas.delete("grid")
        for i in range(1, 5):
            y = i * (h / 5)
            self.canvas.create_line(0, y, w, y, fill="#2A2A2A", width=1, dash=(2, 4), tags="grid")
        for i in range(1, 10):
            x = i * (w / 10)
            self.canvas.create_line(x, 0, x, h, fill="#2A2A2A", width=1, dash=(2, 4), tags="grid")
        self.canvas.create_line(0, h/2, w, h/2, fill="#444444", width=2, tags="grid")

    def draw_graph(self):
        self.canvas.delete("line")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        mid_y = h / 2
        step_x = w / 60 
        points = []
        for i, val in enumerate(self.graph_data):
            x = i * step_x
            y = mid_y - (val / 10) 
            y = max(0, min(h, y))
            points.append(x)
            points.append(y)
        
        if len(points) >= 4:
            last_val = self.graph_data[-1]
            line_color = AppConfig.COLOR_DANGER if last_val < -500 else AppConfig.COLOR_ACCENT
            self.canvas.create_line(points, fill=line_color, width=2, tags="line", smooth=True)

    def calculate_score(self, rate):
        rate = abs(rate)
        if rate < 50: return 10.0, "BUTTER 🧈", AppConfig.COLOR_SUCCESS
        elif rate < 150: return 9.0, "EXCELLENT", "#2ecc71"
        elif rate < 300: return 7.0, "ACCEPTABLE", AppConfig.COLOR_WARNING
        elif rate < 500: return 4.0, "HARD", "#e67e22"
        else: return 0.0, "CRASH", AppConfig.COLOR_DANGER

    def update_ui(self, vspeed, radio_alt, gforce, on_ground):
        self.draw_grid() 
        self.lbl_vspeed.configure(text=f"{int(vspeed)}")
        self.lbl_radio.configure(text=f"{int(radio_alt)}")
        self.lbl_gforce.configure(text=f"{gforce:.2f}")
        
        if vspeed < -600: self.lbl_vspeed.configure(text_color=AppConfig.COLOR_DANGER)
        else: self.lbl_vspeed.configure(text_color=AppConfig.COLOR_ACCENT)

        self.graph_data.append(vspeed)
        self.draw_graph()
        
        if on_ground:
            self.lbl_flight_state.configure(text="ON GROUND", fg_color="#333333", text_color="gray")
        else:
            self.lbl_flight_state.configure(text="AIRBORNE", fg_color=AppConfig.COLOR_ACCENT, text_color="black")
            # Havalanınca puanı sıfırla/gizle
            self.lbl_score.configure(text="---", text_color="gray")

    def listen_udp(self):
        self.log_message("SYSTEM INITIALIZED. LISTENING...")
        was_on_ground = True 
        
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                
                if len(data) == 32:
                    vspeed, radio_alt, gforce, on_ground_double = struct.unpack('dddd', data)
                    is_on_ground = (on_ground_double > 0.5)
                else:
                    continue

                if was_on_ground == False and is_on_ground == True:
                    print(f"!!! TOUCHDOWN !!! Hız: {vspeed}")
                    score, comment, color = self.calculate_score(vspeed)
                    
                    # --- PUANI GÜNCELLE ---
                    self.lbl_score.configure(text=f"{score:.1f}/10", text_color=color)
                    # ----------------------
                    
                    self.log_message(f"🛬 TOUCHDOWN: {int(vspeed)} fpm")
                    self.log_message(f"   GRADE: {score}/10 ({comment})")

                was_on_ground = is_on_ground
                self.after(0, self.update_ui, vspeed, radio_alt, gforce, is_on_ground)

            except socket.timeout:
                pass
            except Exception as e:
                print(e)
            
            time.sleep(0.016)

if __name__ == "__main__":
    app = FlightApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.running = False