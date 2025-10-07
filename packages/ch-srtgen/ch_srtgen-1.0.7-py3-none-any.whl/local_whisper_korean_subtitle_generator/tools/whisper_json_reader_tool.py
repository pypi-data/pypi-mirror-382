from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Dict, Any
import json
import os


class WhisperJsonReaderInput(BaseModel):
	"""Input schema for Whisper JSON Reader Tool."""
	json_path: str = Field(..., description="Absolute or relative path to Whisper transcription JSON file")


class WhisperJsonReaderTool(BaseTool):
	"""Deterministically read Whisper JSON and extract segments [text, start, end]."""

	name: str = "whisper_json_reader_tool"
	description: str = (
		"Reads a Whisper transcription JSON file from disk and returns a JSON array of "
		"segments in the form [{'text': str, 'start': float, 'end': float}]."
	)
	args_schema: Type[BaseModel] = WhisperJsonReaderInput

	def _run(self, json_path: str) -> str:
		try:
			# Resolve path
			resolved_path = os.path.abspath(json_path)
			if not os.path.exists(resolved_path):
				return json.dumps({"error": f"File not found: {resolved_path}"})

			with open(resolved_path, 'r', encoding='utf-8') as f:
				data = json.load(f)

			segments: List[Dict[str, Any]] = []

			# Whisper output may have 'segments' list with 'text', 'start', 'end'
			if isinstance(data, dict) and isinstance(data.get('segments'), list):
				for seg in data['segments']:
					text = seg.get('text', '')
					start = float(seg.get('start', 0.0)) if seg.get('start') is not None else 0.0
					end = float(seg.get('end', 0.0)) if seg.get('end') is not None else 0.0
					segments.append({"text": text, "start": start, "end": end})
			# Some Whisper libs may store as list already
			elif isinstance(data, list):
				# Validate items
				for i, seg in enumerate(data):
					if not isinstance(seg, dict):
						return json.dumps({"error": f"Invalid segment at index {i}: expected object"})
					text = seg.get('text', '')
					start = float(seg.get('start', 0.0)) if seg.get('start') is not None else 0.0
					end = float(seg.get('end', 0.0)) if seg.get('end') is not None else 0.0
					segments.append({"text": text, "start": start, "end": end})
			else:
				# Try common alternative keys
				alts = data.get('results') if isinstance(data, dict) else None
				if isinstance(alts, list):
					for seg in alts:
						text = seg.get('text', '')
						start = float(seg.get('start', 0.0)) if seg.get('start') is not None else 0.0
						end = float(seg.get('end', 0.0)) if seg.get('end') is not None else 0.0
						segments.append({"text": text, "start": start, "end": end})
				else:
					return json.dumps({"error": "Unsupported Whisper JSON structure: expected 'segments' array"})

			return json.dumps(segments, ensure_ascii=False, indent=2)

		except Exception as e:
			return json.dumps({"error": f"Failed to read Whisper JSON: {str(e)}"})


