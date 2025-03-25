def handle_audio_stream_start(payload: dict) -> dict:
    try:
        audio_id = payload.get("audioId")
        codec = payload.get("codec", "pcm")
        sample_rate = payload.get("sampleRate", 16000)
        channels = payload.get("channels", 1)
        chunk_size = payload.get("chunkSize", 1024)

        if not audio_id:
            return {"resultCode": 4001, "resultMsg": "audioId 누락"}

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
        return {"resultCode": 4002, "resultMsg": str(e)}
