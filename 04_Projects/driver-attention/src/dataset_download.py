import math
from huggingface_hub import HfApi, snapshot_download

# 1. Cấu hình tham số
repo_id = "dfki-av/drivergaze360"
repo_type = "dataset"
save_dir = "./drivergaze360_subset"

# 2. Quét danh sách file trên Hugging Face
api = HfApi()
all_files = api.list_repo_files(repo_id=repo_id, repo_type=repo_type)

# Phân tích cấu trúc thư mục từ danh sách file
# Định dạng: dataset/train/C001/001/001-1/rgb.mp4
train_participants = set()
val_participants = set()
test_participants = set()

recording_map = {}

for file_path in all_files:
    parts = file_path.split('/')
    if len(parts) >= 5 and parts[0] == "dataset":
        split_type = parts[1] # train, val, hoặc test
        driver_id = parts[2]  # C001, C002, ...
        recording_id = parts[3] # 001, 002, ...
        sub_rec = parts[4] # 001-1, ...

        rec_path = f"{split_type}/{driver_id}/{recording_id}/{sub_rec}"

        if split_type == "train":
            train_participants.add(driver_id)
        elif split_type == "val":
            val_participants.add(driver_id)
        elif split_type == "test":
            test_participants.add(driver_id)

        if driver_id not in recording_map:
            recording_map[driver_id] = []
        if rec_path not in recording_map[driver_id]:
            recording_map[driver_id].append(rec_path)

# Sắp xếp danh sách tài xế
train_list = sorted(list(train_participants))
val_list = sorted(list(val_participants))
test_list = sorted(list(test_participants))

# Bước 1: Chọn 9 tài xế theo phương án Cân bằng (6 Train, 2 Val, 1 Test)
selected_train = train_list[:6]

# Đảm bảo không trùng lặp tài xế giữa các tập dữ liệu
selected_val = [d for d in val_list if d not in selected_train][:2]
# Nếu tập test_list trống, chúng ta có thể dự phòng chọn từ các tập khác chưa được sử dụng
selected_test = [d for d in test_list if d not in selected_train and d not in selected_val][:1]
if not selected_test:
    # Dự phòng chọn tài xế bất kỳ chưa được phân vào Train và Val
    all_drivers = sorted(list(recording_map.keys()))
    potential_test = [d for d in all_drivers if d not in selected_train and d not in selected_val]
    if potential_test:
        selected_test = [potential_test[0]]

print(f"Tài xế chọn cho Train (6): {selected_train}")
print(f"Tài xế chọn cho Val (2): {selected_val}")
print(f"Tài xế chọn cho Test (1): {selected_test}")

# Bước 2 & 4: Chỉ lấy đúng 1 recording đại diện cho mỗi tài xế và chỉ lấy rgb.mp4 + saliency.mp4
allow_patterns = []

all_selected_drivers = selected_train + selected_val + selected_test
for driver in all_selected_drivers:
    recs = sorted(recording_map.get(driver, []))
    if recs:
        # Chọn recording đầu tiên làm đại diện
        chosen_rec = recs[0]
        print(f"-> Tài xế {driver} chọn recording đại diện: {chosen_rec}")
        allow_patterns.append(f"dataset/{chosen_rec}/rgb.mp4")
        allow_patterns.append(f"dataset/{chosen_rec}/saliency.mp4")

# 5. Tải dữ liệu chính xác theo cấu hình tối ưu
print("\nĐang tải tập subset tối ưu từ Hugging Face...")
snapshot_download(
    repo_id=repo_id,
    repo_type=repo_type,
    allow_patterns=allow_patterns,
    local_dir=save_dir
)
print("Hoàn tất tải dữ liệu subset!")