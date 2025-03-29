import pandas as pd
import os
from deepface import DeepFace
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import numpy as np
from tqdm import tqdm

# 숫자 라벨 → 텍스트 감정 라벨로 매핑
label_map = {0: "angry", 1: "happy", 2: "neutral", 3: "sad"}

def load_dataset_from_csv(csv_path, img_root, model_name="ArcFace"):
    df = pd.read_csv(csv_path, header=None, names=["filename", "label"])
    X, y = [], []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        filename = os.path.basename(row["filename"])  # 경로 제거
        img_path = os.path.join(img_root, filename)
        try:
            embedding = DeepFace.represent(img_path=img_path,
                                           model_name=model_name,
                                           enforce_detection=False)[0]['embedding']
            X.append(embedding)
            y.append(label_map[int(row["label"])])
        except Exception as e:
            print(f"❌ 오류: {img_path} → {e}")
            continue

    return np.array(X), np.array(y)

# 데이터 불러오기
X, y = load_dataset_from_csv("color_dataset.csv", "color_dataset")

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 분류기 학습
clf = SVC(kernel="rbf", probability=True)
clf.fit(X_train, y_train)

# 평가
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
