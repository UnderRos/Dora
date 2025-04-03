import numpy as np
import librosa
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import InputLayer
from tensorflow.keras.mixed_precision import Policy
from tensorflow.keras.utils import custom_object_scope

# 감정 라벨 정의
emotion_labels = ['Angry', 'Anxious', 'Embarrassed', 'Happy', 'Hurt', 'Neutrality', 'Sad', 'Neutrality']

# 모델 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, 'models', 'voice_emotion_model.h5')

# 커스텀 InputLayer 클래스
class PatchedInputLayer(InputLayer):
    @classmethod
    def from_config(cls, config):
        if "batch_shape" in config:
            config["batch_input_shape"] = config.pop("batch_shape")
        return super().from_config(config)

# 모델 로딩
with custom_object_scope({
    "InputLayer": PatchedInputLayer,
    "DTypePolicy": Policy
}):
    model = load_model(model_path, compile=False)

# MFCC 전처리 함수
def extract_mfcc(audio_np, sr=16000, max_pad_len=157):
    mfcc = librosa.feature.mfcc(y=audio_np.astype(np.float32), sr=sr, n_mfcc=13)  # ✅ 13으로 변경
    if mfcc.shape[1] < max_pad_len:
        mfcc = np.pad(mfcc, ((0, 0), (0, max_pad_len - mfcc.shape[1])), mode='constant')
    else:
        mfcc = mfcc[:, :max_pad_len]
    mfcc = mfcc.T  # (157, 13)
    return mfcc[np.newaxis, ..., np.newaxis]  # ✅ (1, 157, 13, 1)

# 감정 예측 함수
def predict_emotion(audio_np, sr=16000):
    mfcc_input = extract_mfcc(audio_np, sr)
    pred = model.predict(mfcc_input, verbose=0)[0]
    idx = np.argmax(pred)
    emotion = emotion_labels[idx]
    confidence = pred[idx]
    return emotion, confidence
