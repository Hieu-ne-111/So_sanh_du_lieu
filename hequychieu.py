import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure(figsize=(11, 11))
ax = fig.add_subplot(111, projection='3d')

# 1. Khung Trái Đất bán kính R = 1
u = np.linspace(0, 2 * np.pi, 60)
v = np.linspace(0, np.pi, 30)
x_sphere = np.outer(np.cos(u), np.sin(v))
y_sphere = np.outer(np.sin(u), np.sin(v))
z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
ax.plot_wireframe(x_sphere, y_sphere, z_sphere, color='lightblue', alpha=0.3, linewidth=0.5)

# 2. Xích đạo (Vĩ độ 0°)
theta = np.linspace(0, 2 * np.pi, 100)
ax.plot(np.cos(theta), np.sin(theta), 0, color='darkorange', linewidth=2.5, label='Xich dao (Vi do 0°)')

# 3. Kinh tuyến gốc (0° Kinh độ)
phi = np.linspace(-np.pi/2, np.pi/2, 100)
ax.plot(np.cos(phi), 0, np.sin(phi), color='crimson', linewidth=2.5, label='Kinh tuyen goc 0°')

# 4. Trục toạ độ ECEF (chiều dương nét liền, chiều âm nét đứt)
scale = 1.35
# Trục X: Đâm qua (0° Lat, 0° Lon) và đối lưng là 180° Lon
ax.quiver(0, 0, 0, scale, 0, 0, color='red', linewidth=2, arrow_length_ratio=0.06)
ax.quiver(0, 0, 0, -scale, 0, 0, color='red', linestyle='dashed', linewidth=1.5, arrow_length_ratio=0.06)

# Trục Y: Đâm qua +90°E (Đông) và -90°W (Tây)
ax.quiver(0, 0, 0, 0, scale, 0, color='green', linewidth=2, arrow_length_ratio=0.06)
ax.quiver(0, 0, 0, 0, -scale, 0, color='green', linestyle='dashed', linewidth=1.5, arrow_length_ratio=0.06)

# Trục Z: Đâm qua +90°N (Cực Bắc) và -90°S (Cực Nam)
ax.quiver(0, 0, 0, 0, 0, scale, color='blue', linewidth=2, arrow_length_ratio=0.06)
ax.quiver(0, 0, 0, 0, 0, -scale, color='blue', linestyle='dashed', linewidth=1.5, arrow_length_ratio=0.06)

# 5. Các điểm mốc cụ thể
# Gốc (0° Lat, 0° Lon)
ax.scatter([1.0], [0.0], [0.0], color='red', s=70, zorder=10)
ax.text(scale + 0.05, 0, 0, '+X: Goc (0° Lat, 0° Lon)', color='red', fontsize=10, weight='bold')

# Điểm mặt sau: Kinh độ 180° (Xích đạo)
ax.scatter([-1.0], [0.0], [0.0], color='darkred', s=70, zorder=10)
ax.text(-scale - 0.55, 0, 0, '-X: Kinh do ±180°\n(Duong doi ngay QT)', color='darkred', fontsize=10, weight='bold')

# Bán cầu Đông (+90°E) & Bán cầu Tây (-90°W)
ax.scatter([0.0], [1.0], [0.0], color='green', s=70, zorder=10)
ax.text(0, scale + 0.05, 0, '+Y: Kinh do +90°E (Dong)', color='green', fontsize=10, weight='bold')

ax.scatter([0.0], [-1.0], [0.0], color='darkgreen', s=70, zorder=10)
ax.text(0, -scale - 0.45, 0, '-Y: Kinh do -90°W (Tay)', color='darkgreen', fontsize=10, weight='bold')

# Cực Bắc (+90° Lat) & Cực Nam (-90° Lat)
ax.scatter([0.0], [0.0], [1.0], color='blue', s=70, zorder=10)
ax.text(0, 0, scale + 0.05, '+Z: Cuc Bac (+90° Lat)', color='blue', fontsize=10, weight='bold')

ax.scatter([0.0], [0.0], [-1.0], color='darkblue', s=70, zorder=10)
ax.text(0, 0, -scale - 0.2, '-Z: Cuc Nam (-90° Lat)', color='darkblue', fontsize=10, weight='bold')

# Đánh dấu đài thiên văn Greenwich (Nước Anh)
lat_uk = np.radians(51.48)
x_uk = np.cos(lat_uk)
z_uk = np.sin(lat_uk)
ax.scatter([x_uk], [0.0], [z_uk], color='purple', s=70, zorder=10)
ax.text(x_uk + 0.05, 0, z_uk + 0.05, 'Dai thien van Greenwich\n(+51.5° Lat, 0° Lon)', 
        color='purple', fontsize=9, weight='bold')

# Tinh chỉnh hiển thị
ax.set_box_aspect([1, 1, 1])
ax.set_xlim([-1.4, 1.4])
ax.set_ylim([-1.4, 1.4])
ax.set_zlim([-1.4, 1.4])
ax.view_init(elev=20, azim=40)
ax.axis('off')

plt.title('Hệ trục toạ độ Trái Đất (ECEF / WGS84)\nĐầy đủ các cực: Lat (±90°), Lon (±90°, ±180°)', 
          fontsize=12, weight='bold', pad=15)
plt.legend(loc='lower left')
plt.tight_layout()
plt.show()