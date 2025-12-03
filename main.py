from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)

app = FastAPI()

# CORS – libera para qualquer origem (depois você pode restringir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois troca pelo domínio do seu app Dyad, se quiser
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_video_id(url: str) -> str:
    """
    Extrai o ID do vídeo de vários formatos de URL do YouTube.
    Ex: https://www.youtube.com/watch?v=ID
        https://youtu.be/ID
        ou só o próprio ID.
    """
    import urllib.parse as urlparse

    # se já for só o ID, retorna direto
    if "http" not in url and "youtu" not in url:
        return url

    parsed = urlparse.urlparse(url)
    if "youtu.be" in parsed.netloc:
        # formato curto: youtu.be/ID
        return parsed.path.lstrip("/")

    # formato normal: youtube.com/watch?v=ID
    query = urlparse.parse_qs(parsed.query)
    video_id = query.get("v", [None])[0]
    if not video_id:
        raise ValueError("Não foi possível extrair o ID do vídeo.")
    return video_id


@app.get("/transcript")
def get_transcript(url: str):
    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # 🔥 NOVO JEITO: instanciar a API e usar .fetch()
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(
            video_id,
            languages=["pt", "pt-BR", "en"],  # prioridade de idiomas
        )

        # fetched é um FetchedTranscript, vamos pegar o "raw"
        raw_transcript = fetched.to_raw_data()

    except NoTranscriptFound:
        raise HTTPException(
            status_code=404,
            detail="Não há transcrição disponível para esse vídeo.",
        )
    except TranscriptsDisabled:
        raise HTTPException(
            status_code=403,
            detail="As transcrições estão desativadas para esse vídeo.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar transcrição: {e}",
        )

    # junta todos os trechos de texto em uma string única
    full_text = " ".join(entry["text"] for entry in raw_transcript)

    return {"transcription": full_text}
