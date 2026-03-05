# ✈️ Flight Telemetry & Landing Analysis System

![Dashboard Preview](assets/Screenshot%202026-01-24%20011252.png)

##  Proje Özeti
Bu proje, **Microsoft Flight Simulator** için geliştirilmiş profesyonel bir gerçek zamanlı iniş analiz sistemidir. C++ (Backend) ve Python (Frontend) hibrit mimarisi kullanılarak geliştirilmiştir.

Uçaktan gelen **Dikey Hız (Vertical Speed)**, **Radar İrtifası** ve **G-Kuvveti** verilerini saniyenin altında gecikmeyle işler ve iniş kalitesini (Puanlama) otomatik olarak hesaplar.

##  Temel Özellikler
* **Hibrit Mimari:** Performans için C++ SimConnect SDK, Modern Arayüz için Python CustomTkinter.
* **UDP Haberleşmesi:** İki modül arasında kayıpsız ve hızlı veri aktarımı.
* **Akıllı Algoritmalar:** "Touchdown" (Teker koyma) anını algılayan ve gürültüyü filtreleyen özel durum makineleri.
* **İniş Analizi:** İniş sertliğine göre (Butter, Hard, Crash) otomatik puanlama sistemi.

##  Teknolojiler
* **Backend:** C++ (SimConnect SDK, Windows Socket API)
* **Frontend:** Python (CustomTkinter, Threading)
* **Protokol:** UDP Network Socket
* **Veri Yapısı:** Struct Padding & Binary Unpacking

##  Kurulum ve Kullanım
1.  Repoyu klonlayın veya indirin.
2.  C++ kodunu derleyin ve MSFS açıkken çalıştırın.
3.  Python arayüzünü başlatın:
    ```bash
    python main.py
    ```
4.  İnişinizi gerçekleştirin ve analizi izleyin!

---
*Geliştirici: Muhammed Emin Fidan*
