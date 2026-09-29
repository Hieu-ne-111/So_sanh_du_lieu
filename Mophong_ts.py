import math
import time
from skyfield.api import load

NORAD_ID = 68843
URL = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={NORAD_ID}&FORMAT=TLE"

ts = load.timescale()
print(f"Đang tải TLE cho NORAD ID {NORAD_ID} từ CelesTrak...")
satellites = load.tle_file(URL)
satellite = satellites[0]
print(f"Đang theo dõi: {satellite.name}\n")

# In tiêu đề cố định 1 lần duy nhất
header = f"{'Thời gian (UTC)':<12} | {'Kinh độ (°)':<12} | {'Vĩ độ (°)':<12} | {'Độ cao (km)':<12} | {'Vận tốc (km/s)':<14}"
print(header)
print("-" * len(header))

try:
    while True:
        t = ts.now()
        geocentric = satellite.at(t)
        subpoint = geocentric.subpoint()

        lon = subpoint.longitude.degrees
        lat = subpoint.latitude.degrees
        alt = subpoint.elevation.km

        # Tính độ lớn vận tốc quỹ đạo (km/s)
        vx, vy, vz = geocentric.velocity.km_per_s
        speed_km_s = math.sqrt(vx**2 + vy**2 + vz**2)

        utc_str = t.utc_strftime('%H:%M:%S')

        # Dùng \r ở đầu để đưa con trỏ về đầu dòng hiện tại, end="" để không xuống dòng mới
        data_line = f"\r{utc_str:<12} | {lon:<12.4f} | {lat:<12.4f} | {alt:<12.2f} | {speed_km_s:<14.3f}"
        print(data_line, end="", flush=True)

        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nĐã dừng theo dõi vệ tinh.")