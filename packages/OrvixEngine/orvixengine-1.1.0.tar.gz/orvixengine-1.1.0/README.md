# OrvixEngine

**OrvixEngine: Modüler 2D Oyun Çerçevesi (Framework)**

OrvixEngine, Pygame'in gücünü temel alan, büyük ölçekli ve kurumsal 2D oyun projeleri için organize edilmiş, tam teşekküllü bir **Geliştirme Çatısıdır (Framework)**. Geliştiricinin karmaşık düşük seviye Pygame kodları yerine doğrudan yüksek seviye oyun mantığına odaklanmasını sağlar.

### 🌐 Resmi Dokümantasyon ve Kaynak

Detaylı kullanım kılavuzları, API referansları ve son geliştirme notları için lütfen resmi web sitemizi ziyaret edin:

[https://orvixgames.com/modul/orvix-engine-sdk/](https://orvixgames.com/modul/orvix-engine-sdk/)

---

## ✨ Kapsamlı Özellikler (Sürüm 1.1.0 Yapılandırması)

### I. Gelişmiş Organizasyon ve Mimari

1.  **Grup Bazlı Çarpışma Filtreleme:** **`collision_mask`** kullanarak, hangi nesne gruplarının birbiriyle etkileşime gireceğini hassas bir şekilde ayarlayın.
2.  **Otomatik Yaşam Döngüsü:** Nesneler `GameObject.destroy()` metodu çağrıldığında sahnede **güvenli ve otomatik** olarak kaldırılır (`Auto-Cleanup`).
3.  **Harici Seviye Yükleyici:** **`LevelLoader`** modülü ile tüm dünya nesnelerini harici **JSON dosyalarından** tek bir komutla sahneye yükleyin.
4.  **Performans Profilleme:** **`Profiler`** modülü ile motorun `Update` ve `Render` döngülerinin süresini milisaniye cinsinden izleyerek darboğazları tespit edin.

### II. Kurulum ve Bakım (Developer Flow)

**OrvixEngine** ile projelerinizi başlatmak ve güncel tutmak son derece kolaydır:

### Kurulum Komutu

Motoru kurmak ve tüm özellik setine anında erişim sağlamak için terminalinizi kullanın:

```bash
pip install OrvixEngine

# Güncelleme
pip install --upgrade OrvixEngine