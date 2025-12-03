"""
YouTube Transcript API - Flask Application
Scalable web service for transcribing YouTube videos
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cachetools import TTLCache
import hashlib
from transcript_service import TranscriptService

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)

# Rate limiting: 100 requests per hour per IP
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Cache: Store transcripts for 1 hour (3600 seconds)
# Max 1000 entries to prevent memory overflow
transcript_cache = TTLCache(maxsize=1000, ttl=3600)

# Initialize transcript service
transcript_service = TranscriptService()


@app.route('/')
def index():
    """Serve the main application page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/transcript', methods=['POST'])
@limiter.limit("50 per hour")  # More restrictive for API endpoint
def get_transcript():
    """
    API endpoint to fetch YouTube video transcript
    
    Request body:
    {
        "url": "YouTube video URL or ID",
        "languages": ["pt", "en"],  // optional
        "include_timestamps": true   // optional, default true
    }
    
    Response:
    {
        "success": true,
        "video_id": "VIDEO_ID",
        "language": "pt",
        "transcript": "formatted transcript text",
        "cached": false
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL obrigatória',
                'message': 'Por favor, forneça uma URL ou ID de vídeo do YouTube.'
            }), 400
        
        url = data['url'].strip()
        languages = data.get('languages', None)
        include_timestamps = data.get('include_timestamps', True)
        
        # Extract video ID
        video_id = transcript_service.extract_video_id(url)
        
        if not video_id:
            return jsonify({
                'success': False,
                'error': 'URL inválida',
                'message': 'Não foi possível extrair o ID do vídeo. Verifique se a URL está correta.'
            }), 400
        
        # Create cache key
        cache_key = hashlib.md5(
            f"{video_id}:{languages}:{include_timestamps}".encode()
        ).hexdigest()
        
        # Check cache first
        if cache_key in transcript_cache:
            cached_result = transcript_cache[cache_key]
            cached_result['cached'] = True
            return jsonify(cached_result), 200
        
        # Fetch transcript
        try:
            transcript_list, language = transcript_service.get_transcript(
                video_id, 
                languages=languages
            )
            
            # Format transcript
            formatted_transcript = transcript_service.format_transcript(
                transcript_list,
                include_timestamps=include_timestamps
            )
            
            # Prepare response
            result = {
                'success': True,
                'video_id': video_id,
                'language': language,
                'transcript': formatted_transcript,
                'total_segments': len(transcript_list),
                'cached': False
            }
            
            # Store in cache
            transcript_cache[cache_key] = result
            
            return jsonify(result), 200
            
        except Exception as e:
            error_info = transcript_service.get_error_message(e)
            return jsonify({
                'success': False,
                **error_info
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro interno',
            'message': f'Erro ao processar requisição: {str(e)}'
        }), 500


@app.route('/api/languages/<video_id>', methods=['GET'])
@limiter.limit("100 per hour")
def get_languages(video_id):
    """
    Get available transcript languages for a video
    
    Response:
    {
        "success": true,
        "video_id": "VIDEO_ID",
        "languages": ["pt", "en", "es"]
    }
    """
    try:
        languages = transcript_service.get_available_languages(video_id)
        
        return jsonify({
            'success': True,
            'video_id': video_id,
            'languages': languages
        }), 200
        
    except Exception as e:
        error_info = transcript_service.get_error_message(e)
        return jsonify({
            'success': False,
            **error_info
        }), 400


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'cache_size': len(transcript_cache),
        'cache_maxsize': transcript_cache.maxsize
    }), 200


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors"""
    return jsonify({
        'success': False,
        'error': 'Limite de requisições excedido',
        'message': 'Você atingiu o limite de requisições. Por favor, aguarde um momento.'
    }), 429


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 YouTube Transcript API iniciando...")
    print(f"📍 Servidor rodando em: http://0.0.0.0:{port}")
    print("📊 Rate limit: 100 requisições/hora")
    print("💾 Cache: 1 hora TTL, max 1000 entradas")
    app.run(debug=False, host='0.0.0.0', port=port)
