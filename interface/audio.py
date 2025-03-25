from common.logger import log_to_db

def handle_audio_stream_start(payload: dict) -> dict:
    try:
        audio_id = payload.get("audioId")
        codec = payload.get("codec", "pcm")
        sample_rate = payload.get("sampleRate", 16000)
        channels = payload.get("channels", 1)
        chunk_size = payload.get("chunkSize", 1024)

        log_to_db(
            user_id=0,
            log_type="audio_stream",
            detail=f"[오디오 스트리밍 시작] audioId={audio_id}, codec={codec}, rate={sample_rate}, ch={channels}, chunk={chunk_size}"
        )

        return {
            "resultCode": 1000,
            "resultMsg": "SUCCESS",
            "data": {
                "streamPort": 5010,
                "protocol": "UDP",
                "codec": codec,
                "sampleRate": sample_rate,
                "channels": channels,
                "chunkSize": chunk_size
            }
        }

    except Exception as e:
        return {
            "resultCode": 4000,
            "resultMsg": str(e)
        }
