from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from .service import list_providers, redaction_by_name, mise_en_forme_by_name

# OpenAPI / Swagger metadata
tags_metadata = [
    {
        "name": "providers",
        "description": "Lister et découvrir les providers configurés.",
    },
    {
        "name": "rédaction",
        "description": "Endpoints pour générer du contenu rédigé via un provider IA.",
    },
    {
        "name": "mise_en_forme",
        "description": "Endpoints pour transformer un texte en HTML accessible.",
    },
]

app = FastAPI(
    title="MCP Rédactionnel HTTP API",
    version="0.1.0",
    description=(
        "Service local pour générer et mettre en forme du contenu via providers d'IA "
        "(Mistral, Ollama, ...). Utilise `config.yaml` pour configurer les providers."
    ),
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Allow local clients (Postman/Bruno) to call the API conveniently
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProviderListResponse(BaseModel):
    providers: List[str] = Field(..., example=["mistral_api", "ollama_local"])


class RedactionRequest(BaseModel):
    provider: str = Field(..., example="mistral_api")
    sujet: str = Field(..., example="Qu'est-ce que l'économie circulaire ?")
    sources: Optional[List[str]] = Field(
        None, example=["https://example.com/article"]
    )
    meta: Optional[dict] = Field(
        None, example={"tone": "formel", "length": "400"}
    )
    format: Optional[str] = Field(
        'text',
        example='text',
        description=(
            "Output format: 'text' (plain French article: "
            "paragraphs, no HTML/Markdown, respects meta like "
            "length/tone) or 'html' (accessible HTML fragment). "
            "Default 'text'."
        ),
    )

    class Config:
        schema_extra = {
            "example": {
                "provider": "mistral_api",
                "sujet": "Qu'est-ce que l'économie circulaire ?",
                "sources": ["https://example.com/article"],
                "meta": {"tone": "formel"},
                "format": "html"
            }
        }


class RedactionResponse(BaseModel):
    result: str = Field(..., example="<article>...</article>")


class MiseEnFormeRequest(BaseModel):
    provider: str = Field(..., example="mistral_api")
    texte: str = Field(..., example="Texte à mettre en forme...")

    class Config:
        schema_extra = {
            "example": {"provider": "mistral_api", "texte": "Un texte à formater"}
        }


class MiseEnFormeResponse(BaseModel):
    result: str = Field(..., example="<article>...</article>")


@app.get(
    "/providers",
    response_model=ProviderListResponse,
    tags=["providers"],
    summary="Liste des providers",
    description=(
        "Retourne la liste des providers définis dans le fichier "
        "de configuration (par défaut `config.yaml`)."
    ),
)
def get_providers(config: str = 'config.yaml'):
    """Obtenir la liste des providers configurés.

    - config: chemin vers le fichier de configuration YAML
    """
    return {"providers": list_providers(config)}


@app.post(
    "/redaction",
    response_model=RedactionResponse,
    tags=["rédaction"],
    summary="Demander une rédaction",
    description=(
        "Demande à un provider de rédiger un texte. "
        "Utilise le prompt configuré (texte ou HTML accessible)."
    ),
)
def post_redaction(req: RedactionRequest, config: str = 'config.yaml'):
    """Lance une rédaction via le provider indiqué.

    Exemple d'utilisation depuis Postman/Bruno:

    POST /redaction
    Content-Type: application/json
    Body: {"provider":"mistral_api","sujet":"Sujet"}
    """
    try:
        out = redaction_by_name(
            req.provider,
            req.sujet,
            sources=req.sources,
            meta=req.meta,
            config_path=config,
            format=(req.format or 'text'),
        )
        return {"result": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/mise_en_forme",
    response_model=MiseEnFormeResponse,
    tags=["mise_en_forme"],
    summary="Demander une mise en forme HTML",
    description=(
        "Demande à un provider de transformer un texte en HTML accessible "
        "(balises sémantiques, ARIA, structure)."
    ),
)
def post_mise_en_forme(req: MiseEnFormeRequest, config: str = 'config.yaml'):
    """Lance la mise en forme d'un texte en HTML accessible.

    Exemple:
    POST /mise_en_forme
    Body: {"provider":"mistral_api","texte":"Mon texte"}
    """
    try:
        out = mise_en_forme_by_name(req.provider, req.texte, config_path=config)
        return {"result": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
