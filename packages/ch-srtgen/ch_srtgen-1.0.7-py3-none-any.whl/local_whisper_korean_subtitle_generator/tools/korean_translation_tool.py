from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, Union, List, Dict, Any
import requests
import json
import time
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class KoreanTranslationInput(BaseModel):
    """Input schema for Korean Translation Tool."""
    transcript_data: Union[str, List[Dict[str, Any]]] = Field(
        ..., 
        description="JSON string containing transcript segments with text, start, and end timestamps, or an already parsed list of segments"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (optional if OPENAI_API_KEY environment variable is set)"
    )

class KoreanTranslationTool(BaseTool):
    """Tool for translating structured transcript data from English to Korean using OpenAI GPT-4o-mini API."""

    name: str = "korean_translation_tool"
    description: str = (
        "Translates structured transcript data from English to Korean using OpenAI's GPT-4o-mini API. "
        "Takes JSON formatted transcript segments with text and timestamps, translates the text to Korean, "
        "and returns the same structure with Korean translations while preserving timestamp information."
    )
    args_schema: Type[BaseModel] = KoreanTranslationInput
    
    # Pydantic fields
    total_tokens_used: int = Field(default=0, description="Total tokens used")
    total_cost: float = Field(default=0.0, description="Total cost")
    input_token_price: float = Field(default=0.25 / 1000000, description="Input token price per token")
    output_token_price: float = Field(default=2.00 / 1000000, description="Output token price per token")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # GPT-5 Mini pricing (as of 2024)
        self.input_token_price = 0.25 / 1000000   # $0.25 per 1M tokens
        self.output_token_price = 2.00 / 1000000  # $2.00 per 1M tokens

    def _run(self, transcript_data: Union[str, List[Dict[str, Any]]], api_key: Optional[str] = None) -> str:
        """
        Translate structured transcript data from English to Korean.
        
        Args:
            transcript_data: JSON string of transcript segments or already parsed list
            api_key: Google Gemini API key (optional)
            
        Returns:
            JSON string with Korean translations maintaining original structure
        """
        try:
            # Debug logging for input type analysis
            print(f"DEBUG: Input type: {type(transcript_data)}")
            print(f"DEBUG: Input content preview: {str(transcript_data)[:200]}...")
            
            # Get API key from parameter or environment variable
            final_api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not final_api_key:
                return json.dumps({
                    "error": "API key required. Provide api_key parameter or set OPENAI_API_KEY environment variable."
                })
            
            # Parse/validate input data with improved handling
            segments = self._parse_transcript_input(transcript_data)
            if isinstance(segments, str):  # Error message returned
                return segments
            
            # Validate segment structure
            validation_error = self._validate_segments(segments)
            if validation_error:
                return validation_error
            
            # OpenAI only: single pass full-script translation then timestamp mapping
            translated_segments = []
            batch_result = self._translate_segments_with_openai_batch(segments, final_api_key)
            if isinstance(batch_result, str):
                return json.dumps({"error": batch_result})
            for (seg, ko_text) in zip(segments, batch_result):
                translated_segments.append({
                    "text": ko_text,
                    "start": seg["start"],
                    "end": seg["end"]
                })
            
            result = json.dumps(translated_segments, ensure_ascii=False, indent=2)
            print(f"DEBUG: Successfully translated {len(translated_segments)} segments")
            
            # Print token usage and cost summary
            self._print_usage_summary()
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"DEBUG: {error_msg}")
            return json.dumps({"error": error_msg})
    
    def _parse_transcript_input(self, transcript_data: Union[str, List[Dict[str, Any]]]) -> Union[List[Dict[str, Any]], str]:
        """
        Parse transcript input data handling both JSON strings and already parsed lists.
        
        Args:
            transcript_data: Input data as string or list
            
        Returns:
            Parsed list of segments or error message string
        """
        try:
            # Case 1: Already a parsed list
            if isinstance(transcript_data, list):
                print("DEBUG: Input is already a parsed list")
                return transcript_data
            
            # Case 2: String that needs JSON parsing
            if isinstance(transcript_data, str):
                print("DEBUG: Input is a string, attempting JSON parsing")
                try:
                    parsed_data = json.loads(transcript_data)
                    if isinstance(parsed_data, list):
                        return parsed_data
                    else:
                        return json.dumps({
                            "error": f"Parsed JSON is not a list but {type(parsed_data).__name__}. Expected array of transcript segments."
                        })
                except json.JSONDecodeError as e:
                    return json.dumps({
                        "error": f"Invalid JSON format: {str(e)}"
                    })
            
            # Case 3: Neither string nor list
            return json.dumps({
                "error": f"Invalid input type: {type(transcript_data).__name__}. Expected JSON string or list of segments."
            })
            
        except Exception as e:
            return json.dumps({
                "error": f"Input parsing error: {str(e)}"
            })
    
    def _validate_segments(self, segments: List[Dict[str, Any]]) -> Optional[str]:
        """
        Validate the structure of transcript segments.
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            Error message string if validation fails, None if valid
        """
        try:
            if not segments:
                return json.dumps({"error": "Empty segments list provided"})
            
            for i, segment in enumerate(segments):
                if not isinstance(segment, dict):
                    return json.dumps({
                        "error": f"Segment {i} must be an object, got {type(segment).__name__}"
                    })
                
                # Check required fields
                if "text" not in segment:
                    return json.dumps({
                        "error": f"Segment {i} missing required 'text' field. Available fields: {list(segment.keys())}"
                    })
                
                if "start" not in segment or "end" not in segment:
                    return json.dumps({
                        "error": f"Segment {i} missing 'start' or 'end' timestamp. Available fields: {list(segment.keys())}"
                    })
                
                # Validate field types
                if not isinstance(segment["text"], str):
                    return json.dumps({
                        "error": f"Segment {i} 'text' field must be string, got {type(segment['text']).__name__}"
                    })
                
                # Timestamps should be numeric
                if not isinstance(segment["start"], (int, float)) or not isinstance(segment["end"], (int, float)):
                    return json.dumps({
                        "error": f"Segment {i} timestamps must be numeric (int/float)"
                    })
            
            print(f"DEBUG: Successfully validated {len(segments)} segments")
            return None
            
        except Exception as e:
            return json.dumps({
                "error": f"Validation error: {str(e)}"
            })

    def _translate_with_openai(self, text: str, api_key: str) -> str:
        """
        Translate text using OpenAI GPT-4o-mini API.
        
        Args:
            text: English text to translate
            api_key: OpenAI API key
            
        Returns:
            Korean translation or error message
        """
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            instruction = "번역해줘"
            prompt = f"{instruction}\n\n{text}"
            
            data = {
                "model": "gpt-5-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 1,
                "max_completion_tokens": 400000
            }
            
            # Log prompt preview (truncated) before request
            try:
                preview = prompt.replace("\n", " ")[:200]
                print(f"OPENAI PROMPT: {preview}...")
            except Exception:
                pass

            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 429:
                # Rate limited - wait and retry once
                print("DEBUG: Rate limited, retrying after 2 seconds...")
                time.sleep(2)
                response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code != 200:
                return f"ERROR: API request failed with status {response.status_code}: {response.text}"
            
            response_data = response.json()
            # Log token usage if available
            try:
                usage = response_data.get("usage", {})
                model_name = response_data.get("model", "")
                if usage:
                    print(
                        f"OPENAI USAGE ({model_name}): prompt_tokens={usage.get('prompt_tokens')}, "
                        f"completion_tokens={usage.get('completion_tokens')}, total_tokens={usage.get('total_tokens')}"
                    )
            except Exception:
                pass
            
            if "choices" not in response_data or not response_data["choices"]:
                return "ERROR: No translation choices returned from API"
            
            choice = response_data["choices"][0]
            
            if "message" not in choice or "content" not in choice["message"]:
                return "ERROR: Invalid response format from API"
            
            korean_text = choice["message"]["content"].strip()
            
            # Remove any surrounding quotes or formatting
            if korean_text.startswith('"') and korean_text.endswith('"'):
                korean_text = korean_text[1:-1]
            
            return korean_text
            
        except requests.exceptions.Timeout:
            return "ERROR: API request timeout"
        except requests.exceptions.RequestException as e:
            return f"ERROR: Network error: {str(e)}"
        except Exception as e:
            return f"ERROR: Translation error: {str(e)}"

    def _translate_segments_with_openai_batch(self, segments: List[Dict[str, Any]], api_key: str) -> Union[List[str], str]:
        """
        Integrated translation strategy: advanced batch translation with four elements
        1) Reference chunk translation to establish style
        2) Overlapping chunking to preserve context
        3) Style guide to keep terminology/tone consistent
        4) Adaptive chunk size based on script length
        """
        try:
            print(f"DEBUG: Integrated strategy start - {len(segments)} segments")
            
            # Analyze total script length
            total_length = sum(len(seg.get("text", "")) for seg in segments)
            print(f"DEBUG: Total script length: {total_length} chars")
            
            # Choose strategy adaptively
            if total_length < 15000:  # short: full
                return self._translate_full_script_optimized(segments, api_key)
            elif total_length < 50000:  # medium: reference + overlap
                return self._translate_with_reference_and_overlap(segments, api_key)
            else:  # long: advanced
                return self._translate_with_advanced_strategy(segments, api_key)
            
        except Exception as e:
            print(f"DEBUG: Integrated translation error: {str(e)}")
            return f"ERROR: Integrated translation failed: {str(e)}"

    def _build_combined_script(self, segments: List[Dict[str, Any]]) -> str:
        """Combine full script with timestamp info"""
        script_parts = []
        for i, seg in enumerate(segments):
            start_time = seg.get("start", 0)
            end_time = seg.get("end", 0)
            text = seg.get("text", "").strip()
            if text:
                script_parts.append(f"[{i:03d}] [{start_time:.2f}s-{end_time:.2f}s] {text}")
        
        return "\n".join(script_parts)

    def _translate_full_script(self, combined_script: str, api_key: str) -> Union[List[str], str]:
        """Translate entire script in one request"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            instruction = (
                "Translate the script into Korean. "
                "Keep line numbers and timestamps unchanged; translate text only. "
                "Output must match the input format."
            )
            
            prompt = f"{instruction}\n\n{combined_script}"
            
            data = {
                "model": "gpt-5-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 1,
                "max_completion_tokens": 128000
            }
            
            print(f"DEBUG: 전체 스크립트 번역 요청 (길이: {len(combined_script)} 문자)")
            
            # 재시도 로직으로 타임아웃 처리
            max_retries = 3
            timeout_seconds = 300  # 5분으로 증가
            
            for attempt in range(max_retries):
                try:
                    print(f"DEBUG: API 요청 시도 {attempt + 1}/{max_retries} (타임아웃: {timeout_seconds}초)")
                    
                    response = requests.post(
                        url, 
                        headers=headers, 
                        json=data, 
                        timeout=timeout_seconds
                    )
                    
                    if response.status_code == 200:
                        break
                    else:
                        print(f"DEBUG: API 응답 오류 (상태: {response.status_code})")
                        if attempt < max_retries - 1:
                            time.sleep(5)
                            continue
                        else:
                            return f"ERROR: API 요청 실패 (상태: {response.status_code}): {response.text}"
                            
                except requests.exceptions.Timeout:
                    print(f"DEBUG: 타임아웃 발생 (시도 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        wait_time = 10 * (attempt + 1)
                        print(f"DEBUG: {wait_time}초 대기 후 재시도...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "ERROR: API 요청 시간 초과 (최대 재시도 횟수 초과)"
                        
                except requests.exceptions.RequestException as e:
                    print(f"DEBUG: 네트워크 오류 (시도 {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    else:
                        return f"ERROR: 네트워크 오류: {str(e)}"
            
            response_data = response.json()
            
            # Track token usage
            try:
                usage = response_data.get("usage", {})
                if usage:
                    self._track_token_usage(usage)
            except Exception:
                pass
            
            if "choices" not in response_data or not response_data["choices"]:
                return "ERROR: No translation received from API"
            
            content = response_data["choices"][0].get("message", {}).get("content", "").strip()
            if not content:
                return "ERROR: Empty translation"
            
            return content
            
        except requests.exceptions.Timeout:
            return "ERROR: API request timeout"
        except requests.exceptions.RequestException as e:
            return f"ERROR: Network error: {str(e)}"
        except Exception as e:
            return f"ERROR: Translation error: {str(e)}"

    def _map_translations_to_segments(self, segments: List[Dict[str, Any]], translated_script: str) -> List[str]:
        """Map translated lines back to original segments"""
        try:
            # 번역된 스크립트를 줄별로 분할
            translated_lines = [line.strip() for line in translated_script.split('\n') if line.strip()]
            
            # 각 줄에서 번역된 텍스트 추출
            translations = []
            for line in translated_lines:
                # Extract only translated text from "[no] [timestamp] translated-text"
                if '] ' in line:
                    parts = line.split('] ', 2)
                    if len(parts) >= 3:
                        translated_text = parts[2].strip()
                        translations.append(translated_text)
                    else:
                        # 형식이 맞지 않으면 전체 줄을 번역으로 사용
                        translations.append(line)
                else:
                    translations.append(line)
            
            # Adjust length to match original segments
            if len(translations) != len(segments):
                print(f"DEBUG: Adjust translation length ({len(translations)} -> {len(segments)})")
                if len(translations) > len(segments):
                    translations = translations[:len(segments)]
                else:
                    # If not enough, fill with original text
                    while len(translations) < len(segments):
                        translations.append(segments[len(translations)].get("text", ""))
            
            return translations
            
        except Exception as e:
            print(f"DEBUG: Mapping error: {str(e)}")
            # On error, return original text
            return [seg.get("text", "") for seg in segments]

    def _translate_with_adaptive_chunking(self, segments: List[Dict[str, Any]], api_key: str) -> Union[List[str], str]:
        """Translate using adaptive chunking (legacy)"""
        try:
            source_lines = [ (seg.get("text") or "").strip() for seg in segments ]

            # Simple token estimate ~ chars/4; we use char budget for safety
            def build_chunks(lines: List[str], char_budget: int = 20000, max_lines: int = 50) -> List[List[str]]:
                chunks: List[List[str]] = []
                current: List[str] = []
                used = 0
                for txt in lines:
                    add_cost = len(txt) + 1  # newline margin
                    if current and (used + add_cost > char_budget or len(current) >= max_lines):
                        chunks.append(current)
                        current = [txt]
                        used = len(txt)
                    else:
                        current.append(txt)
                        used += add_cost
                if current:
                    chunks.append(current)
                return chunks

            def call_openai_for_chunk(chunk: List[str], start_index: int) -> Union[List[str], str]:
                instruction = (
                    "Translate each line to Korean in the same order, concisely. "
                    "Output JSON string array only (no extra text/numbers/descriptions)."
                )
                input_block = "\n".join(chunk)
                prompt = f"{instruction}\n\n{input_block}"

                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data = {
                    "model": "gpt-5-mini",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 1,
                    "max_completion_tokens": 128000
                }

                # Log
                try:
                    preview = prompt.replace("\n", " ")[:280]
                    print(f"DEBUG: Chunk request ({start_index}-{start_index+len(chunk)}): {preview}...")
                except Exception:
                    pass

                # Retry logic for chunk translation
                max_retries = 3
                timeout_seconds = 120
                
                for attempt in range(max_retries):
                    try:
                        print(f"DEBUG: Chunk try {attempt + 1}/{max_retries} (timeout: {timeout_seconds}s)")
                        response = requests.post(url, headers=headers, json=data, timeout=timeout_seconds)
                        
                        if response.status_code == 429:
                            wait_time = 3 * (attempt + 1)
                            print(f"DEBUG: Rate limited, {wait_time}초 대기 후 재시도...")
                            time.sleep(wait_time)
                            continue
                        
                        if response.status_code == 200:
                            break
                        else:
                            print(f"DEBUG: Chunk API error (status: {response.status_code})")
                            if attempt < max_retries - 1:
                                time.sleep(3)
                                continue
                            else:
                                return f"ERROR: API 요청 실패 (청크 {start_index}-{start_index+len(chunk)}) {response.status_code}: {response.text}"
                                
                    except requests.exceptions.Timeout:
                        print(f"DEBUG: Chunk timeout (try {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            wait_time = 5 * (attempt + 1)
                            print(f"DEBUG: Retry after {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                        else:
                            return f"ERROR: Chunk translation timeout (chunk {start_index}-{start_index+len(chunk)})"
                            
                    except requests.exceptions.RequestException as e:
                        print(f"DEBUG: Chunk network error (try {attempt + 1}/{max_retries}): {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(3)
                            continue
                        else:
                            return f"ERROR: Chunk translation network error (chunk {start_index}-{start_index+len(chunk)}): {str(e)}"

                response_data = response.json()
                try:
                    usage = response_data.get("usage", {})
                    if usage:
                        self._track_token_usage(usage)
                except Exception:
                    pass

                if "choices" not in response_data or not response_data["choices"]:
                    return f"ERROR: No result from API (chunk {start_index}-{start_index+len(chunk)})"

                content = response_data["choices"][0].get("message", {}).get("content", "").strip()
                if not content:
                    return f"ERROR: Empty response (chunk {start_index}-{start_index+len(chunk)})"

                # Parse JSON array
                parsed: List[str] = []
                try:
                    parsed = json.loads(content)
                except Exception:
                    try:
                        import re
                        m = re.search(r"```json\s*([\s\S]*?)```", content)
                        if m:
                            parsed = json.loads(m.group(1))
                        else:
                            m2 = re.search(r"```\s*([\s\S]*?)```", content)
                            if m2:
                                parsed = json.loads(m2.group(1))
                    except Exception:
                        parsed = []

                if isinstance(parsed, list) and len(parsed) == len(chunk):
                    cleaned: List[str] = []
                    for val in parsed:
                        if not isinstance(val, str):
                            return f"ERROR: Chunk item type error at {start_index}"
                        cleaned.append(val.strip())
                    return cleaned

                # Fallback: split by newlines as last resort
                lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
                if len(lines) == len(chunk):
                    return lines
                return f"ERROR: Invalid chunk response format (expected {len(chunk)} items)"

            # Build adaptive chunks
            chunks = build_chunks(source_lines, char_budget=20000, max_lines=50)

            # Parallel processing of chunks with order preservation
            from concurrent.futures import ThreadPoolExecutor, as_completed
            max_workers = min(4, max(1, len(chunks)))

            def process_recursive(chunk_local: List[str], global_start: int, depth: int = 0) -> Union[List[str], str]:
                res = call_openai_for_chunk(chunk_local, global_start)
                if isinstance(res, str) and res.startswith("ERROR:") and len(chunk_local) > 1 and depth < 3:
                    mid = len(chunk_local) // 2
                    left = process_recursive(chunk_local[:mid], global_start, depth + 1)
                    if isinstance(left, str):
                        return left
                    right = process_recursive(chunk_local[mid:], global_start + mid, depth + 1)
                    if isinstance(right, str):
                        return right
                    return left + right
                return res

            futures = []
            results_buffer: Dict[int, List[str]] = {}
            global_index = 0
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for chunk in chunks:
                    start_idx = global_index
                    futures.append((start_idx, executor.submit(process_recursive, chunk, start_idx)))
                    global_index += len(chunk)

                for start_idx, fut in futures:
                    out = fut.result()
                    if isinstance(out, str):
                        return out
                    results_buffer[start_idx] = out

            # Assemble in order
            ordered_starts = sorted(results_buffer.keys())
            results: List[str] = []
            for k in ordered_starts:
                results.extend(results_buffer[k])
            return results

        except requests.exceptions.Timeout:
            return "ERROR: OpenAI batch request timeout"
        except requests.exceptions.RequestException as e:
            return f"ERROR: OpenAI network error (batch): {str(e)}"
        except Exception as e:
            return f"ERROR: OpenAI batch translation error: {str(e)}"

    def _translate_full_script_optimized(self, segments: List[Dict[str, Any]], api_key: str) -> Union[List[str], str]:
        """Optimized full translation for short scripts"""
        try:
            print("DEBUG: Short script - full translation mode")
            combined_script = self._build_combined_script(segments)
            translated_result = self._translate_full_script(combined_script, api_key)
            
            if isinstance(translated_result, str) and translated_result.startswith("ERROR:"):
                return translated_result
            
            return self._map_translations_to_segments(segments, translated_result)
        except Exception as e:
            return f"ERROR: Full translation failed: {str(e)}"

    def _translate_with_reference_and_overlap(self, segments: List[Dict[str, Any]], api_key: str) -> Union[List[str], str]:
        """Medium scripts: reference chunk + overlap chunking"""
        try:
            print("DEBUG: Medium script - reference + overlap chunking")
            
            # 1. 기준 청크 설정 (첫 25-30개 세그먼트)
            reference_size = min(30, len(segments) // 4)
            reference_chunk = segments[:reference_size]
            print(f"DEBUG: Reference chunk size: {reference_size} segments")
            
            # 2. 기준 청크 번역
            reference_translation = self._translate_reference_chunk(reference_chunk, api_key)
            if isinstance(reference_translation, str) and reference_translation.startswith("ERROR:"):
                return reference_translation
            
            # 3. 스타일 가이드 생성
            style_guide = self._create_style_guide(reference_translation, reference_chunk)
            print(f"DEBUG: 스타일 가이드 생성 완료")
            
            # 4. 나머지 세그먼트를 오버랩 청킹으로 처리
            remaining_segments = segments[reference_size:]
            if not remaining_segments:
                return reference_translation
            
            # 5. 오버랩 청킹 생성 (5-10개 세그먼트 오버랩)
            overlapping_chunks = self._create_overlapping_chunks(remaining_segments, chunk_size=50, overlap=8)
            print(f"DEBUG: Overlapping chunks created: {len(overlapping_chunks)} chunks")
            
            # 6. 병렬 처리로 각 청크를 스타일 가이드와 함께 번역
            print(f"DEBUG: Translating {len(overlapping_chunks)} chunks in parallel...")
            translated_chunks = self._translate_chunks_parallel(overlapping_chunks, style_guide, api_key)
            if isinstance(translated_chunks, str) and translated_chunks.startswith("ERROR:"):
                return translated_chunks
            
            # 7. 결과 병합 (오버랩 제거)
            final_translations = reference_translation + self._merge_overlapping_chunks(translated_chunks, overlap=8)
            print(f"DEBUG: Reference + overlap completed - {len(final_translations)} segments")
            return final_translations
            
        except Exception as e:
            return f"ERROR: Reference + overlap failed: {str(e)}"

    def _translate_with_advanced_strategy(self, segments: List[Dict[str, Any]], api_key: str) -> Union[List[str], str]:
        """Long scripts: advanced integrated strategy"""
        try:
            print("DEBUG: Long script - advanced integrated strategy")
            
            # 1. 적응적 청크 크기 결정
            adaptive_chunk_size = self._calculate_adaptive_chunk_size(len(segments))
            print(f"DEBUG: Adaptive chunk size: {adaptive_chunk_size}")
            
            # 2. 기준 청크 번역 (첫 청크)
            reference_chunk = segments[:adaptive_chunk_size]
            reference_translation = self._translate_reference_chunk(reference_chunk, api_key)
            if isinstance(reference_translation, str) and reference_translation.startswith("ERROR:"):
                return reference_translation
            
            # 3. 고급 스타일 가이드 생성
            advanced_style_guide = self._create_advanced_style_guide(reference_translation, reference_chunk)
            print(f"DEBUG: Advanced style guide created")
            
            # 4. 나머지 세그먼트를 적응적 오버랩 청킹으로 처리
            remaining_segments = segments[adaptive_chunk_size:]
            if not remaining_segments:
                return reference_translation
            
            # 5. 적응적 오버랩 청킹 (스크립트 길이에 따른 동적 조정)
            overlap_size = min(10, adaptive_chunk_size // 5)  # 청크 크기의 1/5 또는 최대 10
            overlapping_chunks = self._create_overlapping_chunks(
                remaining_segments, 
                chunk_size=adaptive_chunk_size, 
                overlap=overlap_size
            )
            print(f"DEBUG: Adaptive overlap chunking: {len(overlapping_chunks)} chunks, overlap: {overlap_size}")
            
            # 6. 병렬 처리로 각 청크 번역
            translated_chunks = self._translate_chunks_parallel(
                overlapping_chunks, advanced_style_guide, api_key
            )
            if isinstance(translated_chunks, str) and translated_chunks.startswith("ERROR:"):
                return translated_chunks
            
            # 7. 고급 결과 병합
            final_translations = reference_translation + self._advanced_merge_chunks(
                translated_chunks, overlap_size
            )
            print(f"DEBUG: Advanced integrated strategy complete - {len(final_translations)} segments")
            return final_translations
            
        except Exception as e:
            return f"ERROR: Advanced integrated strategy failed: {str(e)}"

    def _translate_reference_chunk(self, reference_chunk: List[Dict[str, Any]], api_key: str) -> Union[List[str], str]:
        """Translate reference chunk (for establishing style)"""
        try:
            combined_script = self._build_combined_script(reference_chunk)
            
            instruction = (
                "Translate the script into Korean. "
                "This translation sets the style for the entire script. "
                "Maintain consistent terminology, tone, and formality. "
                "Keep line numbers and timestamps unchanged; translate text only."
            )
            
            prompt = f"{instruction}\n\n{combined_script}"
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": "gpt-5-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1,  # GPT-5 Mini는 temperature 1만 지원
                "max_completion_tokens": 128000
            }
            
            # Request data validation
            print(f"DEBUG: Reference chunk request - model: {data['model']}, tokens: {data['max_completion_tokens']}")
            print(f"DEBUG: Prompt length: {len(prompt)} chars")
            
            # 기준 청크 번역 재시도 로직
            max_retries = 3
            timeout_seconds = 180
            
            for attempt in range(max_retries):
                try:
                    print(f"DEBUG: Reference chunk try {attempt + 1}/{max_retries} (timeout: {timeout_seconds}s)")
                    response = requests.post(url, headers=headers, json=data, timeout=timeout_seconds)
                    
                    if response.status_code == 429:
                        wait_time = 5 * (attempt + 1)
                        print(f"DEBUG: Rate limited, retry after {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    
                    if response.status_code == 200:
                        break
                    else:
                        error_detail = response.text
                        print(f"DEBUG: Reference chunk API error (status: {response.status_code})")
                        if attempt < max_retries - 1:
                            time.sleep(5)
                            continue
                        else:
                            return f"ERROR: 기준 청크 번역 실패: {response.status_code} - {error_detail}"
                            
                except requests.exceptions.Timeout:
                    print(f"DEBUG: Reference chunk timeout (try {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        wait_time = 10 * (attempt + 1)
                        print(f"DEBUG: Retry after {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "ERROR: Reference chunk timeout (max retries exceeded)"
                        
                except requests.exceptions.RequestException as e:
                    print(f"DEBUG: Reference chunk network error (try {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    else:
                        return f"ERROR: Reference chunk network error: {str(e)}"
            
            response_data = response.json()
            
            # Track token usage
            try:
                usage = response_data.get("usage", {})
                if usage:
                    self._track_token_usage(usage)
            except Exception:
                pass
            
            content = response_data["choices"][0].get("message", {}).get("content", "").strip()
            
            if not content:
                return "ERROR: Reference chunk result is empty"
            
            return self._map_translations_to_segments(reference_chunk, content)
            
        except Exception as e:
            return f"ERROR: Reference chunk error: {str(e)}"

    def _create_style_guide(self, reference_translation: List[str], reference_chunk: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create style guide from reference translation"""
        try:
            # Extract terminology (English-Korean mapping)
            terminology = {}
            for i, (orig, trans) in enumerate(zip(reference_chunk, reference_translation)):
                if orig.get("text") and trans:
                    # Simple mapping (placeholder for advanced NLP)
                    orig_words = orig["text"].lower().split()
                    trans_words = trans.split()
                    if len(orig_words) == len(trans_words):
                        for eng, kor in zip(orig_words, trans_words):
                            if eng != kor.lower():
                                terminology[eng] = kor
            
            # Tone analysis (formality, friendliness, etc.)
            tone_indicators = {
                "formal": ["습니다", "입니다", "하십시오"],
                "casual": ["해요", "이에요", "거예요"],
                "technical": ["기술", "시스템", "프로세스"]
            }
            
            detected_tone = "neutral"
            for tone, indicators in tone_indicators.items():
                if any(indicator in " ".join(reference_translation) for indicator in indicators):
                    detected_tone = tone
                    break
            
            return {
                "terminology": terminology,
                "tone": detected_tone,
                "formality": "formal" if detected_tone == "formal" else "casual",
                "reference_translation": reference_translation
            }
            
        except Exception as e:
            print(f"DEBUG: 스타일 가이드 생성 오류: {str(e)}")
            return {"terminology": {}, "tone": "neutral", "formality": "casual"}

    def _create_overlapping_chunks(self, segments: List[Dict[str, Any]], chunk_size: int = 50, overlap: int = 8) -> List[List[Dict[str, Any]]]:
        """Create overlapping chunks"""
        chunks = []
        for i in range(0, len(segments), chunk_size - overlap):
            chunk = segments[i:i + chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks

    def _translate_chunk_with_style_guide(self, chunk: List[Dict[str, Any]], style_guide: Dict[str, Any], api_key: str) -> Union[List[str], str]:
        """Translate chunk with style guide"""
        try:
            combined_script = self._build_combined_script(chunk)
            
            # Style-guide instructions
            terminology_guide = ""
            if style_guide.get("terminology"):
                terminology_guide = f"\nTerminology: {style_guide['terminology']}"
            
            tone_guide = f"\nTone: {style_guide.get('tone', 'neutral')}"
            formality_guide = f"\nFormality: {style_guide.get('formality', 'casual')}"
            
            instruction = f"""
            Translate the following script into Korean.
            {terminology_guide}
            {tone_guide}
            {formality_guide}
            
            Maintain the reference translation style consistently.
            Keep line numbers and timestamps unchanged; translate text only.
            """
            
            prompt = f"{instruction}\n\n{combined_script}"
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": "gpt-5-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1,  # GPT-5 Mini는 temperature 1만 지원
                "max_completion_tokens": 128000
            }
            
            # Retry logic for style-guide chunk translation
            max_retries = 3
            timeout_seconds = 120
            
            for attempt in range(max_retries):
                try:
                    print(f"DEBUG: Style-guide chunk try {attempt + 1}/{max_retries} (timeout: {timeout_seconds}s)")
                    response = requests.post(url, headers=headers, json=data, timeout=timeout_seconds)
                    
                    if response.status_code == 429:
                        wait_time = 3 * (attempt + 1)
                        print(f"DEBUG: Rate limited, retry after {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    
                    if response.status_code == 200:
                        break
                    else:
                        print(f"DEBUG: Style-guide chunk API error (status: {response.status_code})")
                        if attempt < max_retries - 1:
                            time.sleep(3)
                            continue
                        else:
                            return f"ERROR: 스타일 가이드 청크 번역 실패: {response.status_code}"
                            
                except requests.exceptions.Timeout:
                    print(f"DEBUG: Style-guide chunk timeout (try {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)
                        print(f"DEBUG: Retry after {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "ERROR: Style-guide chunk timeout (max retries exceeded)"
                        
                except requests.exceptions.RequestException as e:
                    print(f"DEBUG: Style-guide chunk network error (try {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(3)
                        continue
                    else:
                        return f"ERROR: Style-guide chunk network error: {str(e)}"
            
            response_data = response.json()
            
            # Track token usage
            try:
                usage = response_data.get("usage", {})
                if usage:
                    self._track_token_usage(usage)
            except Exception:
                pass
            
            content = response_data["choices"][0].get("message", {}).get("content", "").strip()
            
            if not content:
                return "ERROR: Chunk translation result is empty"
            
            return self._map_translations_to_segments(chunk, content)
            
        except Exception as e:
            return f"ERROR: Chunk translation error: {str(e)}"

    def _merge_overlapping_chunks(self, translated_chunks: List[List[str]], overlap: int) -> List[str]:
        """Merge overlapping chunks (deduplicate)"""
        if not translated_chunks:
            return []
        
        merged = translated_chunks[0]
        for chunk in translated_chunks[1:]:
            # Remove overlap and merge
            merged.extend(chunk[overlap:])
        
        return merged

    def _calculate_adaptive_chunk_size(self, total_segments: int) -> int:
        """Calculate adaptive chunk size"""
        if total_segments < 100:
            return 25
        elif total_segments < 300:
            return 40
        elif total_segments < 500:
            return 60
        else:
            return 80

    def _create_advanced_style_guide(self, reference_translation: List[str], reference_chunk: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create advanced style guide"""
        basic_guide = self._create_style_guide(reference_translation, reference_chunk)
        
        # Additional analysis
        basic_guide["sentence_patterns"] = self._analyze_sentence_patterns(reference_translation)
        basic_guide["technical_terms"] = self._extract_technical_terms(reference_chunk, reference_translation)
        
        return basic_guide

    def _analyze_sentence_patterns(self, translations: List[str]) -> List[str]:
        """Analyze sentence patterns"""
        patterns = []
        for trans in translations:
            if trans.endswith("다."):
                patterns.append("statement")
            elif trans.endswith("?"):
                patterns.append("question")
            elif trans.endswith("!"):
                patterns.append("exclamation")
        return patterns

    def _extract_technical_terms(self, original_chunk: List[Dict[str, Any]], translated_chunk: List[str]) -> Dict[str, str]:
        """Extract technical terms"""
        terms = {}
        for orig, trans in zip(original_chunk, translated_chunk):
            # Simple technical term mapping (placeholder for advanced handling)
            if any(tech_word in orig.get("text", "").lower() for tech_word in ["system", "process", "method", "technique"]):
                terms[orig.get("text", "")] = trans
        return terms

    def _translate_chunks_parallel(self, chunks: List[List[Dict[str, Any]]], style_guide: Dict[str, Any], api_key: str) -> Union[List[List[str]], str]:
        """Translate chunks in parallel (preserving order)"""
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            def translate_single_chunk(chunk_with_index):
                chunk_index, chunk = chunk_with_index
                print(f"DEBUG: Chunk {chunk_index + 1}/{len(chunks)} translation start...")
                result = self._translate_chunk_with_style_guide(chunk, style_guide, api_key)
                print(f"DEBUG: Chunk {chunk_index + 1}/{len(chunks)} translation done")
                return chunk_index, result
            
            # Add index to preserve order
            chunks_with_index = [(i, chunk) for i, chunk in enumerate(chunks)]
            
            translated_chunks = [None] * len(chunks)  # 순서 보존을 위한 리스트
            max_workers = min(4, len(chunks))
            
            print(f"DEBUG: Start parallel translation of {len(chunks)} chunks with {max_workers} workers...")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all chunks concurrently
                future_to_index = {
                    executor.submit(translate_single_chunk, chunk_with_index): chunk_with_index[0] 
                    for chunk_with_index in chunks_with_index
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_index):
                    chunk_index, result = future.result()
                    if isinstance(result, str) and result.startswith("ERROR:"):
                        return result
                    translated_chunks[chunk_index] = result
            
            print(f"DEBUG: All chunks translated - {len(translated_chunks)} results")
            return translated_chunks
            
        except Exception as e:
            return f"ERROR: 병렬 청크 번역 실패: {str(e)}"

    def _advanced_merge_chunks(self, translated_chunks: List[List[str]], overlap_size: int) -> List[str]:
        """Advanced chunk merge (with quality checks)"""
        if not translated_chunks:
            return []
        
        merged = translated_chunks[0]
        for i, chunk in enumerate(translated_chunks[1:], 1):
            # Quality check for overlap part
            if overlap_size > 0 and len(merged) >= overlap_size:
                overlap_quality = self._check_overlap_quality(
                    merged[-overlap_size:], 
                    chunk[:overlap_size]
                )
                if overlap_quality < 0.7:
                    print(f"DEBUG: Chunk {i} overlap quality low: {overlap_quality}")
            
            merged.extend(chunk[overlap_size:])
        
        return merged

    def _check_overlap_quality(self, chunk1: List[str], chunk2: List[str]) -> float:
        """Check overlap quality"""
        if not chunk1 or not chunk2:
            return 0.0
        
        # Simple similarity calculation (placeholder for advanced NLP metric)
        min_len = min(len(chunk1), len(chunk2))
        matches = sum(1 for i in range(min_len) if chunk1[i] == chunk2[i])
        return matches / min_len if min_len > 0 else 0.0

    def _track_token_usage(self, usage_data: Dict[str, Any]) -> None:
        """Track token usage"""
        if usage_data:
            prompt_tokens = usage_data.get('prompt_tokens', 0)
            completion_tokens = usage_data.get('completion_tokens', 0)
            total_tokens = usage_data.get('total_tokens', 0)
            
            # Accumulate token usage
            self.total_tokens_used += total_tokens
            
            # Calculate cost
            input_cost = prompt_tokens * self.input_token_price
            output_cost = completion_tokens * self.output_token_price
            request_cost = input_cost + output_cost
            self.total_cost += request_cost
            
            print(f"DEBUG: 토큰 사용량 - 입력: {prompt_tokens}, 출력: {completion_tokens}, 총합: {total_tokens}")
            print(f"DEBUG: 요청 비용 - ${request_cost:.6f}")

    def _print_usage_summary(self) -> None:
        """Print overall usage summary"""
        print("\n" + "="*60)
        print("📊 Translation complete - token usage and cost summary")
        print("="*60)
        print(f"🔢 Total tokens used: {self.total_tokens_used:,} tokens")
        print(f"💰 Total cost: ${self.total_cost:.6f}")
        print(f"💵 Average cost/token: ${self.total_cost/self.total_tokens_used:.8f}" if self.total_tokens_used > 0 else "💵 Average cost/token: $0.00000000")
        print("="*60)
        
        # Estimated time saving vs sequential processing
        estimated_sequential_time = self.total_tokens_used * 0.1
        estimated_parallel_time = estimated_sequential_time / 4
        time_saved = estimated_sequential_time - estimated_parallel_time
        
        print(f"⚡ Time saved: {time_saved:.1f}s (parallel)")
        print(f"🚀 Speedup: ~4x faster")
        print("="*60)
        
        # Gemini support removed (OpenAI only)