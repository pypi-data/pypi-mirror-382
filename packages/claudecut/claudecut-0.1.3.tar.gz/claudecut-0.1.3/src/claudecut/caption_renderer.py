"""
Caption renderer using Playwright to burn captions into video.
Progressive word highlighting using HTML/CSS.
"""

import asyncio
import math
import shutil
import subprocess
from pathlib import Path

import pysrt
from playwright.async_api import async_playwright
from pydantic import BaseModel


class Word(BaseModel):
    """Single word with timing information"""

    text: str
    start: float  # seconds
    end: float  # seconds


class Segment(BaseModel):
    """Group of words to display together"""

    words: list[Word]
    start: float
    end: float


def load_srt_file(srt_path: str) -> list[Word]:
    """Load word-level SRT file into Word objects"""
    srt_file = pysrt.open(srt_path)
    words = []

    for item in srt_file:
        word = Word(
            text=item.text.strip(),
            start=item.start.ordinal / 1000.0,  # ms to seconds
            end=item.end.ordinal / 1000.0,
        )
        words.append(word)

    return words


def group_words_into_segments(
    words: list[Word], words_per_group: int = 4
) -> list[Segment]:
    """Group words into segments for display"""
    segments = []

    for i in range(0, len(words), words_per_group):
        chunk = words[i : i + words_per_group]
        if chunk:
            segment = Segment(words=chunk, start=chunk[0].start, end=chunk[-1].end)
            segments.append(segment)

    return segments


def get_video_info(video_path: str) -> dict:
    """Get video duration, fps, and dimensions using ffprobe"""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate,duration",
        "-of",
        "csv=p=0",
        video_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    width, height, fps_str, duration = result.stdout.strip().split(",")

    # Parse FPS (format: "30/1" or "30000/1001")
    num, denom = map(int, fps_str.split("/"))
    fps = num / denom

    return {
        "width": int(width),
        "height": int(height),
        "fps": fps,
        "duration": float(duration),
    }


def generate_html(
    segment: Segment, current_time: float, video_width: int, video_height: int
) -> str:
    """Generate HTML for a segment with progressive highlighting"""

    # Generate word HTML with appropriate classes
    words_html: list[str] = []
    for word in segment.words:
        if current_time < word.start:
            css_class = "word word-not-narrated-yet"
        elif word.start <= current_time <= word.end:
            css_class = "word word-being-narrated"
        else:
            css_class = "word word-already-narrated"

        span = '<span class="' + css_class + '">' + word.text + "</span>"
        words_html.append(span)

    words_joined = "\n            ".join(words_html)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            width: {video_width}px;
            height: {video_height}px;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: transparent;
        }}

        .caption-container {{
            position: absolute;
            bottom: 160px;
            left: 50%;
            transform: translateX(-50%);
            display: inline-block;
        }}

        .segment {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            gap: 10px;
            padding: 14px 18px;
            background-color: rgba(0, 0, 0, 0.75);
            border-radius: 20px;
            backdrop-filter: blur(8px);
            width: fit-content;
        }}

        .word {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                'Roboto', 'Helvetica Neue', sans-serif;
            font-weight: 700;
            font-size: 64px;
            color: #888888;
            padding: 4px 6px;
            text-shadow:
                -2px -2px 0 #000,
                2px -2px 0 #000,
                -2px 2px 0 #000,
                2px 2px 0 #000,
                4px 4px 8px rgba(0, 0, 0, 0.9);
            transition: color 0.2s ease-in, transform 0.15s ease-out;
            white-space: nowrap;
        }}

        .word-not-narrated-yet {{
            color: #888888;
            transform: scale(1.0);
        }}

        .word-being-narrated {{
            color: #FFFFFF;
            transform: scale(1.08);
        }}

        .word-already-narrated {{
            color: #FFFFFF;
            transform: scale(1.0);
        }}
    </style>
</head>
<body>
    <div class="caption-container">
        <div class="segment">
            {words_joined}
        </div>
    </div>
</body>
</html>"""


async def render_frame_batch(
    browser,
    frame_numbers: list[int],
    segments: list[Segment],
    fps: float,
    video_info: dict,
    output_path: Path,
) -> None:
    """Render a batch of frames using a single browser context"""
    page = await browser.new_page(
        viewport={"width": video_info["width"], "height": video_info["height"]}
    )

    for frame_num in frame_numbers:
        current_time = frame_num / fps

        # Find active segment
        active_segment = None
        for segment in segments:
            if segment.start <= current_time <= segment.end:
                active_segment = segment
                break

        if active_segment:
            html = generate_html(
                active_segment,
                current_time,
                video_info["width"],
                video_info["height"],
            )
            await page.set_content(html)
        else:
            # No caption - create transparent frame
            await page.set_content(f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            width: {video_info["width"]}px;
            height: {video_info["height"]}px;
            margin: 0;
            background: transparent;
        }}
    </style>
</head>
<body></body>
</html>""")

        screenshot_path = output_path / f"frame_{frame_num:06d}.png"
        await page.screenshot(path=str(screenshot_path), omit_background=True)

    await page.close()


async def render_captions_to_frames(
    video_path: str,
    srt_path: str,
    output_dir: str,
    words_per_group: int = 4,
    num_workers: int = 4,
) -> dict:
    """Render caption frames using Playwright with parallel workers"""

    print(f"Loading SRT file: {srt_path}")
    words = load_srt_file(srt_path)
    print(f"Loaded {len(words)} words")

    segments = group_words_into_segments(words, words_per_group)
    print(f"Created {len(segments)} segments")

    print(f"Getting video info: {video_path}")
    video_info = get_video_info(video_path)
    info = video_info
    print(
        f"Video: {info['width']}x{info['height']} "
        f"@ {info['fps']:.2f}fps, {info['duration']:.2f}s"
    )

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Calculate frames
    fps = video_info["fps"]
    duration = video_info["duration"]
    total_frames = math.ceil(duration * fps)

    print(f"Rendering {total_frames} frames with {num_workers} workers...")

    # Split frames into batches for parallel processing
    frames = list(range(total_frames))
    batch_size = math.ceil(total_frames / num_workers)
    batches = [frames[i : i + batch_size] for i in range(0, total_frames, batch_size)]

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Progress tracking
        rendered_count = [0]
        progress_lock = asyncio.Lock()

        async def render_with_progress(batch):
            await render_frame_batch(
                browser, batch, segments, fps, video_info, output_path
            )
            async with progress_lock:
                rendered_count[0] += len(batch)
                if rendered_count[0] % 100 < len(batch):
                    print(f"  Rendered {rendered_count[0]}/{total_frames} frames...")

        # Render all batches in parallel
        await asyncio.gather(*[render_with_progress(batch) for batch in batches])

        await browser.close()

    print(f"✅ Rendered all {total_frames} frames to {output_dir}")
    return video_info


def overlay_captions_on_video(
    video_path: str, frames_dir: str, output_path: str, video_info: dict
) -> None:
    """Combine original video with caption frames using ffmpeg"""

    print("Overlaying captions on video...")

    fps = video_info["fps"]

    # FFmpeg command to overlay captions
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-i",
        video_path,  # Input video
        "-framerate",
        str(fps),
        "-i",
        f"{frames_dir}/frame_%06d.png",  # Caption frames
        "-filter_complex",
        "[0:v][1:v]overlay=0:0",  # Overlay captions
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",  # High quality
        "-c:a",
        "copy",  # Copy audio
        output_path,
    ]

    subprocess.run(cmd, check=True)
    print(f"✅ Video saved to: {output_path}")


async def create_video_with_captions(
    video_path: str,
    srt_path: str,
    output_path: str | None = None,
    words_per_group: int = 4,
    temp_dir: str = "./temp_frames",
    num_workers: int = 4,
    cleanup: bool = True,
) -> str:
    """Main function to create video with progressive word highlighting"""

    if output_path is None:
        output_path = video_path.replace(".mp4", "_captioned.mp4")

    try:
        # Render caption frames
        video_info = await render_captions_to_frames(
            video_path=video_path,
            srt_path=srt_path,
            output_dir=temp_dir,
            words_per_group=words_per_group,
            num_workers=num_workers,
        )

        # Overlay on video
        overlay_captions_on_video(
            video_path=video_path,
            frames_dir=temp_dir,
            output_path=output_path,
            video_info=video_info,
        )

        print(f"\n✅ Done! Output saved to: {output_path}")

    finally:
        # Cleanup temporary frames
        if cleanup and Path(temp_dir).exists():
            print(f"🧹 Cleaning up temporary frames in {temp_dir}...")
            shutil.rmtree(temp_dir)
            print("✅ Cleanup complete")

    return output_path
