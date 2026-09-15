import os
import requests
import pandas as pd
from datetime import datetime

API_KEY = os.getenv('GOOGLE_API_KEY')
# File untuk melacak Place ID agar data tidak duplikat di hari berikutnya
HISTORY_FILE = 'seen_places.txt'
# Target jumlah data per hari
TARGET_COUNT = 100

# Daftar query yang dirotasi agar pencarian mencakup seluruh Jabodetabek
QUERIES = [
    "perusahaan baja di Jakarta", "konstruksi baja di Jakarta",
    "perusahaan baja di Bogor", "kontraktor konstruksi di Bogor",
    "perusahaan baja di Depok", "baja ringan dan berat di Depok",
    "perusahaan baja di Tangerang", "pabrik baja di Tangerang",
    "perusahaan baja di Bekasi", "konstruksi baja di Bekasi",
    "distributor besi dan baja Jabodetabek", "bengkel konstruksi baja Jabodetabek"
]

def load_seen_places():
    """Memuat daftar Place ID yang sudah pernah diambil sebelumnya."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return set(line.strip() for line in f.readlines())
    return set()

def save_seen_place(place_id):
    """Menyimpan Place ID baru ke file history."""
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{place_id}\n")

def build_photo_url(photo_name):
    """Membuat link langsung ke foto menggunakan format API (New)."""
    if not photo_name:
        return "Tidak ada foto"
    # Format baru: photo_name sudah berupa string seperti 'places/xxx/photos/yyy'
    return f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=400&key={API_KEY}"

def main():
    if not API_KEY:
        print("Error: GOOGLE_API_KEY belum disetel di Environment Variables.")
        return

    seen_places = load_seen_places()
    extracted_data = []
    
    # URL dan Header untuk Places API (New)
    search_url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': API_KEY,
        # Field yang ingin kita tarik sekaligus
        'X-Goog-FieldMask': 'places.id,places.displayName,places.nationalPhoneNumber,places.formattedAddress,places.rating,places.websiteUri,places.googleMapsUri,places.photos'
    }
    
    print(f"Memulai pengambilan data dengan API Baru... Telah mengambil {len(seen_places)} data sebelumnya.")

    for query in QUERIES:
        if len(extracted_data) >= TARGET_COUNT:
            break
            
        print(f"\nMencari dengan query: {query}")
        
        # Payload format API Baru
        payload = {
            "textQuery": query,
            "pageSize": 20 # Google API New mengambil maks 20 per halaman
        }
        
        response = requests.post(search_url, json=payload, headers=headers)
        
        # Cek jika ada error
        if response.status_
