# 🎬 YouTube Transcript API

Uma aplicação web moderna e escalável para transcrever vídeos do YouTube de forma **gratuita** e **precisa**. Suporta mais de 500 usuários por dia sem necessidade de API keys.

## ✨ Características

- 🆓 **100% Gratuito** - Sem API keys ou custos
- 🌍 **Multi-idioma** - Suporte para português, inglês, espanhol e mais
- ⚡ **Rápido** - Cache inteligente para respostas instantâneas
- 🎨 **Interface Moderna** - Design premium com dark mode
- 📱 **Responsivo** - Funciona em desktop e mobile
- 🔒 **Rate Limiting** - Proteção contra abuso (100 req/hora)
- 💾 **Export** - Copie ou baixe transcrições em .txt
- ⌨️ **Atalhos** - Navegação rápida via teclado

## 🚀 Instalação Rápida

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. **Clone o repositório** (ou navegue até a pasta):
```bash
cd yt-transcript-api
```

2. **Crie um ambiente virtual** (recomendado):
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

5. **Execute a aplicação**:
```bash
python app.py
```

6. **Acesse no navegador**:
```
http://localhost:5000
```

## 📖 Como Usar

1. Cole a URL de um vídeo do YouTube no campo de entrada
2. (Opcional) Selecione o idioma preferencial
3. (Opcional) Desmarque "incluir timestamps" se desejar apenas o texto
4. Clique em "Obter Transcrição" ou pressione `Ctrl+Enter`
5. Copie ou baixe a transcrição!

### Formatos de URL Suportados

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `VIDEO_ID` (apenas o ID)

### Atalhos de Teclado

- `Ctrl+K` - Focar no campo de URL
- `Ctrl+Enter` - Enviar formulário

## 🏗️ Arquitetura

### Backend (Flask)

- **`app.py`** - Servidor Flask com endpoints da API
- **`transcript_service.py`** - Lógica de extração e formatação
- **Rate Limiting** - 100 requisições/hora por IP
- **Caching** - TTL de 1 hora, máx 1000 entradas

### Frontend

- **HTML5** - Estrutura semântica
- **CSS3** - Design moderno com glassmorphism e gradientes
- **Vanilla JavaScript** - Sem frameworks, leve e rápido

## 📡 API Endpoints

### POST `/api/transcript`

Obter transcrição de um vídeo.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "languages": ["pt", "en"],
  "include_timestamps": true
}
```

**Response (Success):**
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "language": "pt",
  "transcript": "[00:00] Texto da transcrição...",
  "total_segments": 150,
  "cached": false
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Tipo de erro",
  "message": "Mensagem detalhada"
}
```

### GET `/api/languages/<video_id>`

Listar idiomas disponíveis para um vídeo.

**Response:**
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "languages": ["pt", "en", "es"]
}
```

### GET `/api/health`

Health check do servidor.

**Response:**
```json
{
  "status": "healthy",
  "cache_size": 42,
  "cache_maxsize": 1000
}
```

## 🌐 Deploy

### Heroku

```bash
# Criar Procfile
echo "web: python app.py" > Procfile

# Deploy
heroku create sua-app
git push heroku main
```

### Vercel / Railway

Configure o comando de start como `python app.py` e a porta como `5000`.

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
docker build -t yt-transcript .
docker run -p 5000:5000 yt-transcript
```

## ⚙️ Configuração

Edite as constantes em `app.py`:

- **Rate Limit**: Modifique o decorator `@limiter.limit()`
- **Cache TTL**: Altere `ttl` em `TTLCache(maxsize=1000, ttl=3600)`
- **Porta**: Modifique `app.run(port=5000)`

## 🎯 Escalabilidade

Para suportar **500+ usuários/dia**:

✅ **Cache** - Requisições duplicadas retornam instantaneamente  
✅ **Rate Limiting** - Previne abuso (100 req/hora)  
✅ **Lightweight** - Flask + youtube-transcript-api são super eficientes  
✅ **Sem API costs** - YouTube Transcript API é gratuita  

Para **mais de 1000 usuários/dia**, considere:

- Redis para cache distribuído
- PostgreSQL para persistência
- Load balancer (Nginx)
- Múltiplas instâncias com Docker Swarm/Kubernetes

## 🐛 Troubleshooting

### "Transcrições desabilitadas"
O vídeo não possui legendas/transcrições disponíveis.

### "Vídeo indisponível"
O vídeo está privado, foi removido ou não existe.

### "Limite de requisições excedido"
Aguarde algumas horas. O limite é de 100 requisições/hora por IP.

## 📄 Licença

MIT License - Use livremente!

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 🙏 Créditos

Desenvolvido usando:
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - Extração de transcrições
- [Flask-Limiter](https://flask-limiter.readthedocs.io/) - Rate limiting
- [cachetools](https://github.com/tkem/cachetools) - Caching

---

Feito com ❤️ para a comunidade
