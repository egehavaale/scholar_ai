import subprocess
import sys

if __name__ == "__main__":
    print("[ScholarAI] main.py üzerinden app.py başlatılıyor...")
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n[ScholarAI] Uygulama kullanıcı tarafından kapatıldı.")
    except Exception as e:
        print(f"[ScholarAI] Hata oluştu: {e}")