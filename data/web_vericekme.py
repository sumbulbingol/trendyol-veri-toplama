import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# --- Arama kelimesi ---
arama_kelimesi = "samsung akıllı saat"

# --- Brave tarayıcı ayarları ---
options = Options()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--headless")  # Görünmesin istersen aktif et

# --- ChromeDriver yolu ---
chrome_driver_path = "/Users/sumbul/Downloads/chromedriver-mac-arm64/chromedriver"
service = Service(executable_path=chrome_driver_path)

# --- WebDriver başlat ---
driver = webdriver.Chrome(service=service, options=options)

# --- Sayfayı aç ve bekle ---
url = f"https://www.trendyol.com/sr?q={arama_kelimesi.replace(' ', '%20')}"
driver.get(url)
time.sleep(5)

# --- HTML içeriğini al ve kaydet (inceleme için) ---
html = driver.page_source
with open("sayfa_kaynagi.html", "w", encoding="utf-8") as f:
    f.write(html)

driver.quit()

# --- Gömülü JSON’dan ürün adı ve fiyatı regex ile ayıkla ---
# imageAlt → ürün adı, sellingPrice → fiyat
pattern = re.compile(r'"imageAlt":"([^"]+)".*?"sellingPrice":([\d\.]+)', re.DOTALL)
matches = pattern.findall(html)

urunler = []
for name, price in matches:
    urunler.append({
        "Ürün Adı": name,
        "Fiyat": price
    })

if not urunler:
    print("🚫 Hiç ürün bulunamadı. HTML yapısı değişmiş olabilir.")
    exit()

# --- DataFrame ve dönüşümler ---
df = pd.DataFrame(urunler)
df["Fiyat (TL)"] = df["Fiyat"].astype(float)
df = df.drop(columns=["Fiyat"])

# --- En ucuz / pahalı 5 ürün ---
en_ucuz = df.nsmallest(5, "Fiyat (TL)")
en_pahali = df.nlargest(5, "Fiyat (TL)")

print(f"✅ Toplam ürün sayısı: {len(df)}")
print("\n💰 En Ucuz 5 Ürün:\n", en_ucuz)
print("\n💸 En Pahalı 5 Ürün:\n", en_pahali)

# --- CSV Kaydı ---
df.to_csv("samsung_akilli_saat_trendyol.csv", index=False)
print("\n📄 CSV dosyası başarıyla kaydedildi: samsung_akilli_saat_trendyol.csv")
