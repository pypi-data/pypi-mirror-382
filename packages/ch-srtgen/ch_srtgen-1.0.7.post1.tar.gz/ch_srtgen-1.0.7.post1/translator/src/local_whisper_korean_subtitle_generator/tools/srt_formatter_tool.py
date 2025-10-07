from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Dict, Any
import json

class SRTFormatterToolInput(BaseModel):
    """Input schema for SRT Formatter Tool."""
    translated_data: str = Field(
        ..., 
        description="JSON string containing Korean transcript segments with format [{'text': '...', 'start': 0.0, 'end': 1.5}]"
    )
    output_filename: str = Field(
        default="korean_subtitles.srt",
        description="Optional name for the subtitle file (defaults to 'korean_subtitles.srt')"
    )

class SRTFormatterTool(BaseTool):
    """Tool for converting Korean transcript data to SRT subtitle format."""

    name: str = "SRT Formatter Tool"
    description: str = (
        "Converts translated transcript data in JSON format with Korean text and timestamps "
        "into standard SRT subtitle file format. Takes JSON string input with transcript segments "
        "and returns properly formatted SRT content as a string."
    )
    args_schema: Type[BaseModel] = SRTFormatterToolInput

    def _run(self, translated_data: str, output_filename: str = "korean_subtitles.srt") -> str:
        """
        Convert translated transcript data to SRT format.
        
        Args:
            translated_data: JSON string of Korean transcript segments
            output_filename: Name for the subtitle file (optional)
            
        Returns:
            Complete SRT content as formatted string
        """
        try:
            # Parse the JSON input
            transcript_segments = json.loads(translated_data)
            
            if not isinstance(transcript_segments, list):
                return "Error: Input data must be a JSON array of transcript segments."
            
            # Validate segment structure
            for i, segment in enumerate(transcript_segments):
                if not isinstance(segment, dict):
                    return f"Error: Segment {i+1} must be a dictionary object."
                
                required_fields = ['text', 'start', 'end']
                for field in required_fields:
                    if field not in segment:
                        return f"Error: Segment {i+1} missing required field '{field}'."
                
                # Validate timestamp types
                if not isinstance(segment['start'], (int, float)) or not isinstance(segment['end'], (int, float)):
                    return f"Error: Segment {i+1} timestamps must be numbers (seconds)."
                
                if segment['start'] >= segment['end']:
                    return f"Error: Segment {i+1} start time must be less than end time."
            
            # Generate SRT content
            srt_content = []
            
            for i, segment in enumerate(transcript_segments, 1):
                # Convert timestamps to SRT format
                start_time = self._seconds_to_srt_time(segment['start'])
                end_time = self._seconds_to_srt_time(segment['end'])
                
                # Format SRT entry
                srt_entry = f"{i}\n{start_time} --> {end_time}\n{segment['text']}\n"
                srt_content.append(srt_entry)
            
            # Join all entries with blank lines between them
            complete_srt = '\n'.join(srt_content)
            
            return complete_srt
            
        except json.JSONDecodeError as e:
            return f"Error parsing JSON input: {str(e)}"
        except KeyError as e:
            return f"Error: Missing required field in transcript data: {str(e)}"
        except Exception as e:
            return f"Error processing transcript data: {str(e)}"
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """
        Convert seconds to SRT timestamp format (HH:MM:SS,mmm).
        
        Args:
            seconds: Time in seconds (float)
            
        Returns:
            Formatted timestamp string
        """
        # Convert to integer milliseconds
        total_milliseconds = int(seconds * 1000)
        
        # Extract hours, minutes, seconds, and milliseconds
        hours = total_milliseconds // (1000 * 60 * 60)
        remaining_ms = total_milliseconds % (1000 * 60 * 60)
        
        minutes = remaining_ms // (1000 * 60)
        remaining_ms = remaining_ms % (1000 * 60)
        
        secs = remaining_ms // 1000
        milliseconds = remaining_ms % 1000
        
        # Format as HH:MM:SS,mmm
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"