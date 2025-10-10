"""
Video editing utilities using ffmpeg-python
"""

import logging
from pathlib import Path

import ffmpeg

logger = logging.getLogger(__name__)


def split_and_merge_video(
    input_path: str | Path,
    output_path: str | Path,
    ranges: list[tuple[float, float]],
    crossfade_duration: float = 0.1,
) -> None:
    """
    Extract specific time ranges from a video and merge with audio crossfades.

    Args:
        input_path: Path to input video file (e.g., 'input.mp4')
        output_path: Path to output video file (e.g., 'output.mp4')
        ranges: List of (start, end) time tuples in seconds to keep.
                Example: [(0.5, 3.2), (5.0, 8.5), (10.0, 15.0)]
        crossfade_duration: Audio crossfade duration in seconds (default 0.1)

    Example:
        >>> split_and_merge_video(
        ...     "test_video.mp4",
        ...     "output_edited.mp4",
        ...     [(0.0, 5.0), (10.0, 15.0), (20.0, 25.0)]
        ... )
    """
    if not ranges:
        raise ValueError("At least one time range must be provided")

    # Validate ranges
    for i, (start, end) in enumerate(ranges):
        if start >= end:
            raise ValueError(
                f"Range {i}: start ({start}) must be less than end ({end})"
            )
        if start < 0:
            raise ValueError(f"Range {i}: start time cannot be negative")

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    logger.info(f"Processing {len(ranges)} segments from {input_path}")

    # Create temporary segments
    segment_files = []
    temp_dir = output_path.parent / ".temp_segments"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Extract each segment with audio fade in/out for smooth transitions
        for i, (start, end) in enumerate(ranges):
            segment_path = temp_dir / f"segment_{i:03d}.mp4"
            duration = end - start
            logger.info(
                f"Extracting segment {i + 1}/{len(ranges)}: {start:.2f}s - {end:.2f}s"
            )

            # Add fade in at start and fade out at end for smooth audio
            fade_duration = min(crossfade_duration, duration / 2)

            # Create audio filter for fade in/out
            audio_filter = (
                f"afade=t=in:st=0:d={fade_duration},"
                f"afade=t=out:st={duration - fade_duration}:d={fade_duration}"
            )

            (
                ffmpeg.input(str(input_path), ss=start, t=duration)
                .output(
                    str(segment_path),
                    vcodec="libx264",
                    acodec="aac",
                    audio_bitrate="192k",
                    af=audio_filter,
                )
                .overwrite_output()
                .run(quiet=True)
            )
            segment_files.append(segment_path)

        logger.info(f"Merging {len(segment_files)} segments into {output_path}")

        # If only one segment, just copy it
        if len(segment_files) == 1:
            (
                ffmpeg.input(str(segment_files[0]))
                .output(str(output_path), c="copy")
                .overwrite_output()
                .run(quiet=True)
            )
        else:
            # Concatenate segments (audio fades applied per segment)
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, "w") as f:
                for segment_file in segment_files:
                    f.write(f"file '{segment_file.absolute()}'\n")

            (
                ffmpeg.input(str(concat_file), format="concat", safe=0)
                .output(
                    str(output_path),
                    c="copy",
                )
                .overwrite_output()
                .run(quiet=True)
            )

        logger.info(f"Successfully created {output_path}")

    finally:
        # Cleanup temporary files
        for segment_file in segment_files:
            if segment_file.exists():
                segment_file.unlink()
        if temp_dir.exists():
            concat_file = temp_dir / "concat.txt"
            if concat_file.exists():
                concat_file.unlink()
            temp_dir.rmdir()


def get_video_duration(video_path: str | Path) -> float:
    """
    Get the duration of a video in seconds.

    Args:
        video_path: Path to the video file

    Returns:
        Duration in seconds
    """
    probe = ffmpeg.probe(str(video_path))
    duration = float(probe["format"]["duration"])
    return duration
