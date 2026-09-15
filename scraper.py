import os
import time
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

def get_place_details(place_id):
    """Mengambil detail lengkap dari sebuah tempat berdasarkan Place ID."""
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_phone_number,formatted_address,rating,website,url,photos',
        'key': API_KEY
    }
    
    response = requests.get(details_url, params=params)
    if response.status_code == 200:
        return response.json().get('result', {})
    return {}

def build_photo_url(photo_reference):
    """Membuat link langsung ke foto jika tersedia."""
    if not photo_reference:
        return "Tidak ada foto"
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={API_KEY}"

def main():
    if not API_KEY:
        print("Error: GOOGLE_API_KEY belum disetel di Environment Variables.")
        return

    seen_places = load_seen_places()
    extracted_data = []
    
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    print(f"Memulai pengambilan data... Telah mengambil {len(seen_places)} data sebelumnya.")

    # Loop melalui query sampai kita mendapat 100 data baru
    for query in QUERIES:
        if len(extracted_data) >= TARGET_COUNT:
            break
            
        print(f"Mencari dengan query: {query}")
        params = {'query': query, 'key': API_KEY}
        
        while len(extracted_data) < TARGET_COUNT:
            response = requests.get(search_url, params=params)
            data = response.json()
            
            results = data.get('results', [])
            
            for place in results:
                if len(extracted_data) >= TARGET_COUNT:
                    break
                    
                place_id = place.get('place_id')
                
                # Cek jika belum pernah diambil
                if place_id not in seen_places:
                    print(f"Mengambil detail untuk: {place.get('name')}")
                    details = get_place_details(place_id)
                    
                    # Ekstrak data yang diperlukan
                    name = details.get('name', place.get('name'))
                    phone = details.get('formatted_phone_number', 'Tidak ada telepon')
                    address = details.get('formatted_address', place.get('formatted_address'))
                    rating = details.get('rating', 'Tidak ada rating')
                    website = details.get('website', 'Tidak ada website')
                    maps_url = details.get('url', f"https://www.google.com/maps/place/?q=place_id:{place_id}")
                    
                    photos = details.get('photos', [])
                    photo_url = build_photo_url(photos[0]['photo_reference']) if photos else "Tidak ada foto"
                    
                    # Google Maps API tidak menyediakan Email, kita beri placeholder
                    email = "Tidak tersedia di GMaps (Cek Website)"
                    
                    extracted_data.append({
                        "Nama Perusahaan": name,
                        "Telepon / WA": phone,
                        "Email": email,
                        "Alamat": address,
                        "Rating": rating,
                        "Website": website,
                        "Link Google Maps": maps_url,
                        "Link Foto": photo_url
                    })
                    
                    seen_places.add(place_id)
                    save_seen_place(place_id)
            
            next_page_token = data.get('next_page_token')
            if next_page_token and len(extracted_data) < TARGET_COUNT:
                # Google membutuhkan delay singkat sebelum token halaman berikutnya aktif
                print("Menunggu token halaman berikutnya...")
                time.sleep(2.5) 
                params = {'pagetoken': next_page_token, 'key': API_KEY}
            else:
                break # Pindah ke query berikutnya jika tidak ada halaman lagi

    if extracted_data:
        df = pd.DataFrame(extracted_data)
        today_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"Data_Baja_Konstruksi_{today_str}.xlsx"
        
        df.to_excel(filename, index=False)
        print(f"Berhasil menyimpan {len(extracted_data)} data baru ke {filename}")
    else:
        print("Tidak ada data baru yang ditemukan hari ini.")

if __name__ == "__main__":
    main()