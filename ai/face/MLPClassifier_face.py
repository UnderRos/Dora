import pandas as pd
import os
from deepface import DeepFace
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report
import numpy as np
from tqdm import tqdm

# 숫자 라벨 → 텍스트 감정 라벨 매핑
label_map = {0: "angry", 1: "happy", 2: "neutral", 3: "sad"}

def load_dataset_from_csv(csv_path, img_root, model_name="ArcFace",
                          batch_size=5000, 
                          embeddings_file="embeddings.npy", 
                          labels_file="labels.npy",
                          intermediate_embeddings="embeddings_intermediate.npy",
                          intermediate_labels="labels_intermediate.npy"):
    # CSV 파일 로드: 헤더가 있으면 그대로 사용, 없으면 기본 컬럼명 지정
    df = pd.read_csv(csv_path)
    # CSV 헤더가 "path"로 되어 있다면 "filename"으로 변경
    if "path" in df.columns:
        df.rename(columns={"path": "filename"}, inplace=True)
    elif "filename" not in df.columns:
        df.columns = ["filename", "label"]
    
    X, y = [], []
    total = len(df)
    
    # 중간 저장 파일이 있으면 로드 (부분 진행된 경우)
    if os.path.exists(intermediate_embeddings) and os.path.exists(intermediate_labels):
        print("중간 임베딩 파일을 로드합니다...")
        X = list(np.load(intermediate_embeddings, allow_pickle=True))
        y = list(np.load(intermediate_labels, allow_pickle=True))
        start_index = len(X)
    else:
        start_index = 0

    # 배치 단위로 처리
    for start in tqdm(range(start_index, total, batch_size), desc="배치 처리"):
        end = min(start + batch_size, total)
        batch_df = df.iloc[start:end]
        for _, row in batch_df.iterrows():
            # CSV에 들어있는 경로가 전체 경로일 경우, os.path.basename() 사용
            filename = os.path.basename(row["filename"])
            img_path = os.path.join(img_root, filename)
            if not os.path.exists(img_path):
                print(f"오류: {img_path} → 파일이 존재하지 않습니다.")
                continue
            try:
                embedding = DeepFace.represent(img_path=img_path,
                                               model_name=model_name,
                                               enforce_detection=False)[0]['embedding']
                X.append(embedding)
                y.append(label_map[int(row["label"])])
            except Exception as e:
                print(f"오류: {img_path} → {e}")
                continue
        # 중간 저장 (배치 처리 후마다)
        np.save(intermediate_embeddings, np.array(X, dtype=object))
        np.save(intermediate_labels, np.array(y, dtype=object))
        print(f"배치 [{start}:{end}] 완료, 중간 저장됨.")

    X = np.array(X, dtype=object)
    y = np.array(y, dtype=object)
    # 최종 저장
    np.save(embeddings_file, X)
    np.save(labels_file, y)
    print("임베딩 추출 및 최종 저장 완료!")
    return X, y

# 데이터셋 로드 (배치 처리 및 중간 저장 적용)
X, y = load_dataset_from_csv("color_dataset.csv", "color_dataset", batch_size=5000)

# 데이터 분할 (train: 80%, test: 20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# MLPClassifier로 분류기 학습
clf = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=50, random_state=42, verbose=True)
clf.fit(X_train, y_train)

# 평가
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
