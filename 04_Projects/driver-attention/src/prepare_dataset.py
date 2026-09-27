import os
import subprocess

root_dir = "./drivergaze360_subset"
print(f"Searching for video files in {root_dir}...")

target_pairs = [("rgb.mp4", "rgb"), ("saliency.mp4", "saliency")]
processed_count = 0

# Thiết lập FPS trích xuất (1 FPS đại diện theo hướng dẫn tối ưu hóa bước 3)
TARGET_FPS = 1

for root, dirs, files in os.walk(root_dir):
    # Duyệt qua các file trong thư mục hiện tại
    for file_name in files:
        for video_name, out_folder_name in target_pairs:
            # So khớp không phân biệt chữ hoa chữ thường để tránh lỗi cấu trúc đường dẫn hệ thống
            if file_name.lower() == video_name.lower():
                video_path = os.path.join(root, file_name)
                output_dir = os.path.join(root, out_folder_name)

                # Bỏ qua nếu thư mục đích đã có sẵn các khung hình trích xuất
                if os.path.exists(output_dir) and len([f for f in os.listdir(output_dir) if f.lower().endswith('.jpg')]) > 0:
                    print(f"Already extracted: {output_dir}")
                    continue

                print(f"Extracting: {video_path} -> {output_dir} (Sampling rate: {TARGET_FPS} FPS)")
                os.makedirs(output_dir, exist_ok=True)

                # Trích xuất với cấu hình FPS thấp (-r 1) để giảm kích thước lưu trữ của tập dữ liệu
                cmd = f"ffmpeg -y -i \"{video_path}\" -r {TARGET_FPS} -q:v 1 -qmin 1 -start_number 1 \"{output_dir}/%06d.jpg\""
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if res.returncode == 0:
                    extracted_count = len([f for f in os.listdir(output_dir) if f.lower().endswith('.jpg')])
                    print(f"Successfully extracted {extracted_count} frames.")
                    processed_count += 1
                else:
                    print(f"Error extracting {video_path}: {res.stderr}")

print(f"\nAll done! Processed {processed_count} video files with downsampled rate.")