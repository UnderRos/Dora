def handle_video_stream_start(payload: dict) -> dict:
    try:
        video_id = payload.get("videoId")
        quality = payload.get("quality", "high")
        fps = payload.get("fps", 15)

        if not video_id:
            return {"resultCode": 4001, "resultMsg": "videoId 누락"}

        return {
            "resultCode": 1000,
            "resultMsg": "SUCCESS",
            "data": {
                "streamPort": 5005,
                "protocol": "UDP",
                "format": "JPEG",
                "quality": quality,
                "fps": fps
            }
        }

    except Exception as e:
        return {"resultCode": 4002, "resultMsg": str(e)}


def handle_stream_stop(payload: dict) -> dict:
    try:
        video_id = payload.get("videoId")
        if not video_id:
            return {"resultCode": 4001, "resultMsg": "videoId 누락"}

        return {
            "resultCode": 1000,
            "resultMsg": "SUCCESS"
        }

    except Exception as e:
        return {"resultCode": 4002, "resultMsg": str(e)}
