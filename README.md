# Atölye Takip Programı

Basit bir CLI uygulaması ile otomobil atölyesi operasyonlarını tek bir dosyada takip etmek için örnek bir araç. Araç giriş/çıkışları, bayi işlemleri, haftalık personel ödemeleri, gelir-gider ve stok hareketleri `workshop_data.json` dosyasına yazılır. Dosya boş veya bozuk olsa bile uygulama güvenli şekilde çalışır; gerekirse yeni bir veri dosyası oluşturulur.

## Çalıştırma
1. Python 3 kurulu olmalı.
2. Depo klasöründe `python main.py` (veya Windows için `py main.py`) komutunu çalıştırın.
3. Menüdeki yönergeleri izleyerek kayıt ekleyin.

### Tek dosya halinde kullanmak isteyenler için
`atolye_takip.py` dosyası, uygulamanın tüm bileşenlerini tek Python dosyasında içerir. 
Kopyalayıp tek başına `python atolye_takip.py` komutu ile çalıştırabilirsiniz; aynı 
`workshop_data.json` dosyasını kullanır.

## Özellikler
- **Araç takibi:** Marka, model, plaka ile giriş kaydı; çıkışta not ekleme.
- **Bayi işlemleri:** Gelir veya borç olarak kayıt; özet raporda toplamlar ve net bakiye.
- **Personel haftalıkları:** Hafta bitiş tarihi ve tutar ile ödeme kaydı.
- **Gelir/gider tablosu:** Kategorili gelir ve gider kayıtları; toplam ve net rapor.
- **Stok takibi:** Ürün bazında miktar güncelleme (artı/eksi) ve listeleme.

## Veri dosyası
Tüm veriler `workshop_data.json` dosyasında saklanır. Dosya yoksa otomatik oluşturulur ve JSON formatındadır; farklı bir konum için `WORKSHOP_DATA_FILE` çevre değişkenini bir yol değeri ile ayarlayabilir (ör. `WORKSHOP_DATA_FILE="D:\\yedek\\veri.json"`), ya da `config.py` içindeki `DATA_FILE` ayarını değiştirebilirsiniz. Dosya bozulmuşsa açılışta onarılır ve geçerli şema ile yeniden yazılır.
