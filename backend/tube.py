from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import yt_dlp

app = FastAPI()

video_id = 'n0fW88BMBno'
URL = f'https://www.youtube.com/watch?v={video_id}'


@app.get("/")
async def read_root():
    return {"message": "Welcome to the YouTube Video Downloader. Use /download?url=<video_url>"}


@app.get("/download")
async def download_video():
    ydl_opts = {
        'format': 'best',  # You can specify other formats if needed
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '-',  # Output to stdout
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(URL, download=False)
        video_url = info_dict['formats'][0]['url']  # Get the direct video URL
        filename = f"{info_dict['title']}.mp4"  # Use video title for filename

        print(info_dict)

        # Create a streaming response
        response = StreamingResponse(ydl.download(
            [video_url]), media_type="video/mp4")
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
