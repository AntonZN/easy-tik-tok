from app.core.config import get_settings

settings = get_settings()


def encode_cmd(input_path: str, output_path: str) -> str:
    cmd = [
        settings.FFMPEG_COMMAND,
        "-hide_banner",
        "-loglevel error",
        "-y",
        "-i",
        input_path,
        "-movflags +faststart",
        "-c:v libx264",
        "-filter:v scale=iw/2:ih/2,setsar=1:1",
        "-coder 1",
        "-pix_fmt yuv420p",
        "-profile:v high",
        "-level 4.0",
        "-preset:v veryfast",
        "-tune film",
        "-bf 3",
        "-b_strategy 2",
        "-g 60",
        "-refs 10",
        "-b:v 1.5M",
        "-minrate 1.25M",
        "-maxrate 2.5M",
        "-bufsize 2.5M",
        "-movflags faststart",
        "-b:a 64k",
        "-pass 1",
        output_path,
    ]
    return " ".join(cmd)
