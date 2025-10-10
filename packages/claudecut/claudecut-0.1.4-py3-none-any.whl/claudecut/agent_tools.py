"""
Agent tools for subtitle generation and video editing.
"""

import json
import logging
from pathlib import Path

import whisper_timestamped as whisper
from claude_agent_sdk import tool
from whisper_timestamped import make_subtitles

from claudecut.caption_renderer import create_video_with_captions
from claudecut.video_editor import get_video_duration, split_and_merge_video

logger = logging.getLogger(__name__)


def _extract_words_from_segments(segments: list) -> list[dict]:
    """Extract all words from segments into a flat list."""
    words = []
    for segment in segments:
        if "words" in segment:
            for word in segment["words"]:
                words.append(
                    {"start": word["start"], "end": word["end"], "text": word["text"]}
                )
    return words


@tool(
    "generate_subtitles",
    "Transcribe video and generate word and sentence caption files (SRT format)",
    {"video_path": str},
)
async def generate_subtitles(args: dict) -> dict:
    """
    Transcribe video and automatically generate both word and sentence caption files.

    Args:
        video_path: Path to the video file (REQUIRED)

    Returns:
        Success message with paths to both generated caption files
    """
    video_path = args.get("video_path")
    if not video_path:
        return {"content": [{"type": "text", "text": "Error: video_path is required"}]}

    # Generate default paths based on video filename
    video_stem = Path(video_path).stem
    video_dir = Path(video_path).parent

    word_srt_path = str(video_dir / f"{video_stem}_word.srt")
    sentence_srt_path = str(video_dir / f"{video_stem}_sentence.srt")
    transcript_txt_path = str(video_dir / f"{video_stem}_transcript.txt")

    language = "en"

    try:
        logger.info(f"Transcribing {video_path} with Whisper")
        audio = whisper.load_audio(video_path)
        model = whisper.load_model("large-v3-turbo", device="cpu")
        result = whisper.transcribe_timestamped(
            model, audio, language=language, vad=True
        )

        # Generate word-level SRT
        words = _extract_words_from_segments(result["segments"])
        word_segments = [
            {"start": w["start"], "end": w["end"], "text": w["text"]} for w in words
        ]
        with open(word_srt_path, "w", encoding="utf-8") as f:
            make_subtitles.write_srt(word_segments, f)
        logger.info(f"Generated word-level SRT: {word_srt_path}")

        # Generate sentence-level SRT - use Whisper's natural segments with VAD
        sentence_segments = [
            {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
            for seg in result["segments"]
        ]
        with open(sentence_srt_path, "w", encoding="utf-8") as f:
            make_subtitles.write_srt(sentence_segments, f)
        logger.info(f"Generated sentence-level SRT: {sentence_srt_path}")

        # Generate plain text transcript with line breaks matching sentences
        with open(transcript_txt_path, "w", encoding="utf-8") as f:
            for seg in result["segments"]:
                f.write(seg["text"].strip() + "\n")
        logger.info(f"Generated plain text transcript: {transcript_txt_path}")

        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Successfully transcribed {video_path}\n\n"
                        f"Generated files:\n"
                        f"- Word-level SRT: {word_srt_path} ({len(words)} words)\n"
                        f"- Sentence-level SRT: {sentence_srt_path} "
                        f"({len(sentence_segments)} segments)\n"
                        f"- Plain text transcript: {transcript_txt_path}\n\n"
                        f"Full transcription:\n{result.get('text', '')[:300]}..."
                    ),
                }
            ]
        }
    except Exception as e:
        logger.error(f"Subtitle generation failed: {e}")
        return {
            "content": [
                {"type": "text", "text": f"Error generating subtitles: {str(e)}"}
            ]
        }


def _parse_srt_timestamps(srt_path: str) -> list[tuple[float, float]]:
    """Parse SRT file and extract start/end timestamps."""
    segments = []
    with open(srt_path, encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Look for timestamp line (format: 00:00:00,000 --> 00:00:00,000)
        if " --> " in line:
            parts = line.split(" --> ")
            start = _srt_time_to_seconds(parts[0])
            end = _srt_time_to_seconds(parts[1])
            segments.append((start, end))
        i += 1
    return segments


def _srt_time_to_seconds(time_str: str) -> float:
    """Convert SRT timestamp to seconds."""
    time_str = time_str.replace(",", ".")
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


@tool(
    "analyze_silences",
    "Find silence gaps in caption file",
    {"srt_path": str, "min_gap": float},
)
async def analyze_silences(args: dict) -> dict:
    """Find gaps/silences between caption segments with buffering."""
    srt_path = args.get("srt_path")
    min_gap = max(args.get("min_gap", 0.4), 0.4)  # Minimum 0.4s gap enforced
    buffer = 0.2  # Hard-coded 0.2s buffer on each side

    if not srt_path:
        return {"content": [{"type": "text", "text": "Error: srt_path required"}]}

    try:
        segments = _parse_srt_timestamps(srt_path)
        silences = []

        for i in range(len(segments) - 1):
            gap_start = segments[i][1]
            gap_end = segments[i + 1][0]
            gap_duration = gap_end - gap_start

            if gap_duration >= min_gap:
                # Add buffer to both sides to avoid cutting into speech
                buffered_start = gap_start + buffer
                buffered_end = gap_end - buffer

                # Only include if there's still a gap after buffering
                if buffered_end > buffered_start:
                    silences.append([buffered_start, buffered_end])

        buffer_info = f"(>={min_gap}s, {buffer}s buffer)"
        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Found {len(silences)} silences {buffer_info}:\n"
                        + "\n".join(
                            f"- {s[0]:.2f}s to {s[1]:.2f}s ({s[1] - s[0]:.2f}s)"
                            for s in silences
                        )
                    ),
                }
            ]
        }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


@tool(
    "cut_video",
    "Cut and merge video segments based on time ranges",
    {"input_path": str, "output_path": str, "ranges": list},
)
async def cut_video(args: dict) -> dict:
    """
    Cut specific time ranges from a video and merge them.

    Args:
        input_path: Path to input video file (REQUIRED)
        output_path: Path for output video (default: output_edited.mp4)
        ranges: List of [start, end] time pairs in seconds (floats supported).
                Example: [[0, 5.5], [10.2, 15.8]] keeps 0-5.5s and 10.2-15.8s

    Returns:
        Success message with path to edited video
    """
    input_path = args.get("input_path")
    output_path = args.get("output_path", "output_edited.mp4")
    ranges = args.get("ranges", [])

    if not input_path:
        return {"content": [{"type": "text", "text": "Error: input_path is required"}]}

    if not ranges:
        return {"content": [{"type": "text", "text": "Error: ranges is required"}]}

    try:
        if isinstance(ranges, str):
            try:
                ranges = json.loads(ranges)
            except json.JSONDecodeError as e:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Error: ranges must be valid JSON. "
                                f"Got: {ranges}\nError: {e}"
                            ),
                        }
                    ]
                }

        # Validate ranges format
        range_tuples = []
        for i, r in enumerate(ranges):
            if not isinstance(r, (list, tuple)) or len(r) != 2:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Error: Invalid range format at index {i}. "
                                f"Expected [start, end] with 2 numbers, got: {r}"
                            ),
                        }
                    ]
                }
            range_tuples.append((float(r[0]), float(r[1])))

        logger.info(f"Cutting video {input_path} with {len(range_tuples)} segments")
        split_and_merge_video(input_path, output_path, range_tuples)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Successfully cut and merged video: {output_path}\n"
                    f"Segments: {range_tuples}",
                }
            ]
        }
    except Exception as e:
        logger.error(f"Video cutting failed: {e}")
        logger.exception("Full traceback:")
        return {"content": [{"type": "text", "text": f"Error cutting video: {str(e)}"}]}


@tool(
    "get_video_info",
    "Get information about a video file",
    {
        "video_path": str,
    },
)
async def get_video_info(args: dict) -> dict:
    """
    Get video duration and basic information.

    Args:
        video_path: Path to the video file

    Returns:
        Video information including duration
    """
    video_path = args.get("video_path")

    if not video_path:
        return {"content": [{"type": "text", "text": "Error: video_path is required"}]}

    try:
        duration = get_video_duration(video_path)
        file_size = Path(video_path).stat().st_size / (1024 * 1024)  # MB

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Video: {video_path}\n"
                    f"Duration: {duration:.2f} seconds ({duration / 60:.2f} minutes)\n"
                    f"File size: {file_size:.2f} MB",
                }
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        return {
            "content": [{"type": "text", "text": f"Error getting video info: {str(e)}"}]
        }


@tool(
    "add_captions",
    "Burn word-level captions into video with progressive highlighting effect",
    {
        "video_path": str,
        "word_srt_path": str,
        "output_path": str,
    },
)
async def add_captions(args: dict) -> dict:
    """
    Add burned-in captions to video with progressive word highlighting.

    IMPORTANT: Requires a WORD-LEVEL SRT file (not sentence-level).
    Use the word SRT generated by generate_subtitles (e.g., *_word.srt).

    Args:
        video_path: Path to input video file (REQUIRED)
        word_srt_path: Path to word-level SRT file (REQUIRED)
        output_path: Path for output video (default: input_captioned.mp4)

    Returns:
        Success message with path to captioned video

    Styling:
    - Modern system font, 64px
    - Progressive highlighting: gray → white with smooth fade
    - Words grow slightly when spoken
    - 4 words displayed per group
    - Rounded background box with transparency
    """
    video_path = args.get("video_path")
    word_srt_path = args.get("word_srt_path")
    output_path = args.get("output_path")

    if not video_path:
        return {"content": [{"type": "text", "text": "Error: video_path is required"}]}

    if not word_srt_path:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "Error: word_srt_path is required. "
                    "Must be a word-level SRT file (e.g., *_word.srt)",
                }
            ]
        }

    # Generate default output path if not provided
    if not output_path:
        video_stem = Path(video_path).stem
        video_dir = Path(video_path).parent
        output_path = str(video_dir / f"{video_stem}_captioned.mp4")

    try:
        # Validate inputs exist
        if not Path(video_path).exists():
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: Video file not found: {video_path}",
                    }
                ]
            }

        if not Path(word_srt_path).exists():
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: SRT file not found: {word_srt_path}",
                    }
                ]
            }

        logger.info(f"Adding captions to {video_path} using {word_srt_path}")

        # Run the async caption rendering
        result_path = await create_video_with_captions(
            video_path=video_path,
            srt_path=word_srt_path,
            output_path=output_path,
            words_per_group=4,
            num_workers=8,
            cleanup=True,
        )

        output_size = Path(result_path).stat().st_size / (1024 * 1024)

        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Successfully added captions to video!\n\n"
                        f"Input: {video_path}\n"
                        f"Captions: {word_srt_path}\n"
                        f"Output: {result_path}\n"
                        f"Output size: {output_size:.2f} MB\n\n"
                        f"Caption style: Progressive word highlighting, "
                        f"4 words per group"
                    ),
                }
            ]
        }
    except Exception as e:
        logger.error(f"Caption rendering failed: {e}")
        logger.exception("Full traceback:")
        return {
            "content": [{"type": "text", "text": f"Error adding captions: {str(e)}"}]
        }
