import argparse
import json
import os
import sys
from pathlib import Path

from local_whisper_korean_subtitle_generator.tools.korean_translation_tool import (
    KoreanTranslationTool,
)
from local_whisper_korean_subtitle_generator.tools.srt_formatter_tool import (
    SRTFormatterTool,
)


def translate_and_format(json_path: str, output_path: str) -> int:
    try:
        if not os.path.exists(json_path):
            print(f"Error: JSON not found: {json_path}")
            return 2

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Normalize segments structure
        segments = None
        if isinstance(data, list):
            segments = data
        elif isinstance(data, dict):
            candidate = None
            if isinstance(data.get("segments"), list):
                candidate = data.get("segments")
            elif isinstance(data.get("results"), list):
                candidate = data.get("results")
            if isinstance(candidate, list):
                segments = []
                for seg in candidate:
                    if not isinstance(seg, dict):
                        continue
                    text = seg.get("text", "")
                    start = float(seg.get("start", 0.0)) if seg.get("start") is not None else 0.0
                    end = float(seg.get("end", 0.0)) if seg.get("end") is not None else 0.0
                    segments.append({"text": text, "start": start, "end": end})

        if not isinstance(segments, list):
            print("Error: Input JSON is not a list of segments.")
            return 2

        # Translate
        translator = KoreanTranslationTool()
        translated_json = translator._run(json.dumps(segments, ensure_ascii=False))

        try:
            parsed = json.loads(translated_json) if isinstance(translated_json, str) else translated_json
            if isinstance(parsed, dict) and parsed.get("error"):
                print(f"Translation error: {parsed.get('error')}")
                return 3
            if not isinstance(parsed, list):
                print("Error: Translated result is not a list of segments.")
                return 3
            translated_json = json.dumps(parsed, ensure_ascii=False)
        except Exception as e:
            print(f"Error: Failed to parse translation result - {str(e)}")
            return 3

        # Format to SRT
        srt_tool = SRTFormatterTool()
        srt_content = srt_tool._run(translated_json)

        # Write file
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        print(f"SRT saved: {out_path}")
        return 0
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="srt-generator", description="SRT Generator CLI")
    sub = parser.add_subparsers(dest="command")

    p_tf = sub.add_parser(
        "translate-format",
        help="Translate Whisper JSON to Korean and output SRT",
    )
    p_tf.add_argument("--json", required=True, help="Path to Whisper result JSON")
    p_tf.add_argument("--out", required=True, help="Path to output .srt")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "translate-format":
        code = translate_and_format(args.json, args.out)
        sys.exit(code)

    parser.print_help()
    sys.exit(0)


