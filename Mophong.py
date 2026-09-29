import json
import urllib.request
import math
from datetime import datetime, timezone
import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load

# ==================== CẤU HÌNH ====================
NORAD_ID = 68843
API_KEY = "DMFXXL-MYL5Y8-ARRFUF-5UTJ"  # API Key N2YO
SECONDS_COUNT = 120

OBSERVER_LAT = 21.0285
OBSERVER_LON = 105.8542
OBSERVER_ALT = 0

def break_antimeridian(lons, lats):
    """Ngắt nét vẽ khi qua kinh tuyến 180 độ."""
    lons_clean, lats_clean = [lons[0]], [lats[0]]
    for i in range(1, len(lons)):
        if abs(lons[i] - lons[i-1]) > 180:
            lons_clean.append(np.nan)
            lats_clean.append(np.nan)
        lons_clean.append(lons[i])
        lats_clean.append(lats[i])
    return lons_clean, lats_clean

# 1. TẢI DỮ LIỆU TỪ N2YO (APP)
api_url = (
    f"https://api.n2yo.com/rest/v1/satellite/positions/"
    f"{NORAD_ID}/{OBSERVER_LAT}/{OBSERVER_LON}/{OBSERVER_ALT}/{SECONDS_COUNT}/"
    f"&apiKey={API_KEY}"
)

print(f"Đang lấy dữ liệu {SECONDS_COUNT}s từ N2YO...")
req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    n2yo_data = json.loads(resp.read().decode('utf-8'))

positions = n2yo_data.get("positions", [])
if not positions:
    print("Lỗi từ N2YO:", n2yo_data)
    exit()

sat_name = n2yo_data["info"]["satname"]

# 2. SKYFIELD TÍNH TOÁN QUỸ ĐẠO VÀ VẬN TỐC (LAPTOP)
ts = load.timescale()
tle_url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={NORAD_ID}&FORMAT=TLE"
satellite = load.tle_file(tle_url)[0]

app_lat = np.array([p["satlatitude"] for p in positions])
app_lon = np.array([p["satlongitude"] for p in positions])
app_alt = np.array([p["sataltitude"] for p in positions])
epochs = [p["timestamp"] for p in positions]

lap_lat, lap_lon, lap_alt, lap_speed = [], [], [], []
time_labels = []

for ep in epochs:
    dt = datetime.fromtimestamp(ep, tz=timezone.utc)
    t = ts.from_datetime(dt)
    
    geocentric = satellite.at(t)
    sub = geocentric.subpoint()
    
    lap_lat.append(sub.latitude.degrees)
    lap_lon.append(sub.longitude.degrees)
    lap_alt.append(sub.elevation.km)
    
    vx, vy, vz = geocentric.velocity.km_per_s
    lap_speed.append(math.sqrt(vx**2 + vy**2 + vz**2))
    time_labels.append(dt.strftime('%H:%M:%S'))

lap_lat = np.array(lap_lat)
lap_lon = np.array(lap_lon)
lap_alt = np.array(lap_alt)
lap_speed = np.array(lap_speed)

# 3. TÍNH VẬN TỐC QUÁN TÍNH TỪ N2YO (CHUYỂN ĐỔI ECEF -> ECI THEO CHUẨN VẬT LÝ)
app_speed = []
R_EARTH = 6371.0
OMEGA_EARTH = 7.2921159e-5  # Vận tốc góc tự quay Trái Đất (rad/s)

coords_3d = []
for i in range(len(positions)):
    r = R_EARTH + app_alt[i]
    phi = np.radians(app_lat[i])
    lam = np.radians(app_lon[i])
    x = r * np.cos(phi) * np.cos(lam)
    y = r * np.cos(phi) * np.sin(lam)
    z = r * np.sin(phi)
    coords_3d.append(np.array([x, y, z]))

coords_3d = np.array(coords_3d)

for i in range(len(positions)):
    if 0 < i < len(positions) - 1:
        dt = epochs[i+1] - epochs[i-1]
        v_ecef = (coords_3d[i+1] - coords_3d[i-1]) / dt
    elif i == 0:
        dt = epochs[1] - epochs[0]
        v_ecef = (coords_3d[1] - coords_3d[0]) / dt
    else:
        dt = epochs[-1] - epochs[-2]
        v_ecef = (coords_3d[-1] - coords_3d[-2]) / dt

    # Biến đổi vận tốc sang hệ quán tính ECI: V_eci = V_ecef + (Omega x r)
    v_inertial_x = v_ecef[0] - OMEGA_EARTH * coords_3d[i][1]
    v_inertial_y = v_ecef[1] + OMEGA_EARTH * coords_3d[i][0]
    v_inertial_z = v_ecef[2]

    speed = math.sqrt(v_inertial_x**2 + v_inertial_y**2 + v_inertial_z**2)
    app_speed.append(speed)

app_speed = np.array(app_speed)

# 4. TÍNH ĐỘ LỆCH LỚN NHẤT (MAX ERROR)
max_err_lat = float(np.max(np.abs(lap_lat - app_lat)))

raw_dlon = np.abs(lap_lon - app_lon)
max_err_lon = float(np.max(np.minimum(raw_dlon, 360.0 - raw_dlon)))

max_err_alt = float(np.max(np.abs(lap_alt - app_alt)))
max_err_spd = float(np.max(np.abs(lap_speed - app_speed)))

# 5. XUẤT KẾT QUẢ TỐI GIẢN LÊN TERMINAL
print("\n" + "=" * 55)
print(f"  KẾT QUẢ ĐỐI SOÁT QUY ĐẠO: {sat_name} ({NORAD_ID})")
print("=" * 55)
print(f"{'Thông số':<28} | {'SAI LỆCH LỚN NHẤT (MAX)'}")
print("-" * 55)
print(f"{'Vĩ độ':<28} | {max_err_lat:.4f}°")
print(f"{'Kinh độ':<28} | {max_err_lon:.4f}°")
print(f"{'Độ cao quỹ đạo':<28} | {max_err_alt:.3f} km")
print(f"{'Vận tốc quỹ đạo':<28} | {max_err_spd:.4f} km/s")
print("=" * 55 + "\n")

# 6. VẼ ĐỒ THỊ
plt.figure(figsize=(16, 5))

# Đồ thị 1: Quỹ đạo mặt đất
app_lon_c, app_lat_c = break_antimeridian(app_lon, app_lat)
lap_lon_c, lap_lat_c = break_antimeridian(lap_lon, lap_lat)

plt.subplot(1, 3, 1)
plt.plot(app_lon_c, app_lat_c, 'r--', label='N2YO App', linewidth=2)
plt.plot(lap_lon_c, lap_lat_c, 'b:', label='Laptop Skyfield', linewidth=2)
plt.title(f'1. Quỹ đạo mặt đất (Max lệch Lon: {max_err_lon:.3f}°)')
plt.xlabel('Kinh độ (°)')
plt.ylabel('Vĩ độ (°)')
plt.legend()
plt.grid(True)

# Đồ thị 2: So sánh vận tốc
plt.subplot(1, 3, 2)
step = max(1, len(time_labels) // 5)
plt.plot(time_labels, app_speed, 'r--', label='App ECI (km/s)', linewidth=1.8)
plt.plot(time_labels, lap_speed, 'b:', label='Laptop SGP4 (km/s)', linewidth=1.8)
plt.xticks(time_labels[::step], rotation=35)
plt.title(f'2. Vận tốc quỹ đạo (Max lệch: {max_err_spd:.4f} km/s)')
plt.xlabel('Thời gian UTC')
plt.ylabel('Vận tốc (km/s)')
plt.legend()
plt.grid(True)

# Đồ thị 3: So sánh độ cao
plt.subplot(1, 3, 3)
plt.plot(time_labels, app_alt, 'r--', label='App Alt (km)', linewidth=1.8)
plt.plot(time_labels, lap_alt, 'b:', label='Laptop Alt (km)', linewidth=1.8)
plt.xticks(time_labels[::step], rotation=35)
plt.title(f'3. Độ cao quỹ đạo (Max lệch: {max_err_alt:.2f} km)')
plt.xlabel('Thời gian UTC')
plt.ylabel('Độ cao (km)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()