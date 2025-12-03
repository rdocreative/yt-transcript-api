"""
YouTube Transcript Service
Core logic for extracting and formatting YouTube video transcripts
"""

import re
from typing import Dict, List, Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    InvalidVideoId
)


class TranscriptService:
    """Service for extracting YouTube video transcripts"""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        
        Supported formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        - VIDEO_ID (direct ID)
        """
        # Direct video ID (11 characters)
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        # Standard youtube.com/watch?v=
        match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        
        # youtu.be short links
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        
        return None
    
    @staticmethod
    def get_transcript(
        video_id: str, 
        languages: Optional[List[str]] = None
    ) -> Tuple[List[Dict], str]:
        """
        Fetch transcript for a YouTube video
        Compatible with youtube-transcript-api 1.2.3+
        
        Args:
            video_id: YouTube video ID
            languages: List of language codes to try (e.g., ['pt', 'en'])
        
        Returns:
            Tuple of (transcript_list, language_used)
        
        Raises:
            Various YouTubeTranscriptApi exceptions
        """
        try:
            # Add custom headers to avoid blocking
            import youtube_transcript_api._api
            youtube_transcript_api._api.HEADERS = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Create API instance
            api = YouTubeTranscriptApi()
            
            # Helper function to convert FetchedTranscript to list of dicts
            def convert_transcript(fetched_transcript):
                return [
                    {
                        'text': snippet.text,
                        'start': snippet.start,
                        'duration': snippet.duration
                    }
                    for snippet in fetched_transcript
                ]
            
            # If specific languages requested, try to fetch with those
            if languages and len(languages) > 0:
                try:
                    fetched = api.fetch(video_id, languages=languages)
                    return convert_transcript(fetched), languages[0]
                except:
                    pass  # Continue to fallback
            
            # Try default languages in order
            default_languages = ['pt', 'en', 'es', 'fr', 'de']
            
            for lang in default_languages:
                try:
                    fetched = api.fetch(video_id, languages=[lang])
                    return convert_transcript(fetched), lang
                except:
                    continue
            
            # Last resort: get any available transcript
            try:
                # List available transcripts
                available_transcripts = api.list(video_id)
                if available_transcripts and len(available_transcripts) > 0:
                    first_transcript = available_transcripts[0]
                    fetched = api.fetch(video_id, languages=[first_transcript.language_code])
                    return convert_transcript(fetched), first_transcript.language_code
            except:
                pass
            
            # If all fails, raise error
            raise NoTranscriptFound(
                video_id,
                [],
                "No transcripts found for this video"
            )
            
        except Exception as e:
            raise e
    
    @staticmethod
    def format_transcript(
        transcript_list: List[Dict], 
        include_timestamps: bool = True
    ) -> str:
        """
        Format transcript list into readable text
        
        Args:
            transcript_list: List of transcript segments from YouTubeTranscriptApi
            include_timestamps: Whether to include timestamps in output
        
        Returns:
            Formatted transcript string
        """
        if not transcript_list:
            return ""
        
        formatted_lines = []
        
        for segment in transcript_list:
            text = segment.get('text', '').strip()
            if not text:
                continue
            
            if include_timestamps:
                start_seconds = segment.get('start', 0)
                timestamp = TranscriptService._seconds_to_timestamp(start_seconds)
                formatted_lines.append(f"[{timestamp}] {text}")
            else:
                formatted_lines.append(text)
        
        return "\n".join(formatted_lines)
    
    @staticmethod
    def _seconds_to_timestamp(seconds: float) -> str:
        """Convert seconds to MM:SS or HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def get_available_languages(video_id: str) -> List[str]:
        """Get list of available transcript languages for a video"""
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            return [t.language_code for t in transcript_list]
        except Exception:
            return []
    
    @staticmethod
    def get_error_message(error: Exception) -> Dict[str, str]:
        """Convert exception to user-friendly error message"""
        if isinstance(error, TranscriptsDisabled):
            return {
                "error": "Transcrições desabilitadas",
                "message": "Este vídeo não possui transcrições disponíveis."
            }
        elif isinstance(error, NoTranscriptFound):
            return {
                "error": "Transcrição não encontrada",
                "message": "Não foi possível encontrar uma transcrição no idioma solicitado."
            }
        elif isinstance(error, VideoUnavailable):
            return {
                "error": "Vídeo indisponível",
                "message": "O vídeo está privado, foi removido ou não existe."
            }
        elif isinstance(error, InvalidVideoId):
            return {
                "error": "ID de vídeo inválido",
                "message": "O link do YouTube fornecido é inválido."
            }
        else:
            return {
                "error": "Erro ao processar",
                "message": f"Ocorreu um erro inesperado: {str(error)}"
            }
