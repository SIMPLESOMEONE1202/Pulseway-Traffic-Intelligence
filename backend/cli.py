import argparse
from pathlib import Path
from app.analytics.engine import process_video


def main():
    parser = argparse.ArgumentParser(description="Headless smart traffic video analytics")
    parser.add_argument("video", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--detector", choices=["auto", "yolo", "motion"], default="auto")
    args = parser.parse_args()
    result = process_video(args.video, args.output, lambda progress, _: print(f"\r{progress:5.1f}%", end=""), detector_mode=args.detector)
    print(f"\nDone: {args.output / 'annotated.mp4'}")
    print(result)


if __name__ == "__main__": main()
