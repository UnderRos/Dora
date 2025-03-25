from common.logger import log_to_db

def handle_video_stream_start(payload: dict) -> dict:
    try:
        video_id = payload.get("videoId")
        quality = payload.get("quality", "high")
        fps = payload.get("fps", 15)

        log_to_db(
            user_id=0,
            log_type="video_stream",
            detail=f"[영상 스트리밍 시작] videoId={video_id}, quality={quality}, fps={fps}"
        )

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
        return {
            "resultCode": 4000,
            "resultMsg": str(e)
        }


def handle_stream_stop(payload: dict) -> dict:
    try:
        video_id = payload.get("videoId")
        audio_id = payload.get("audioId")

        if video_id:
            log_to_db(
                user_id=0,
                log_type="stream_stop",
                detail=f"[스트리밍 중지] videoId={video_id}"
            )
        elif audio_id:
            log_to_db(
                user_id=0,
                log_type="stream_stop",
                detail=f"[스트리밍 중지] audioId={audio_id}"
            )

        return {
            "resultCode": 1000,
            "resultMsg": "SUCCESS"
        }

    except Exception as e:
        return {
            "resultCode": 4000,
            "resultMsg": str(e)
        }
