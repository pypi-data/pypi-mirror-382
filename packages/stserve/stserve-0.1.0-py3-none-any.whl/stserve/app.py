from dataclasses import dataclass

import click
import torch
import uvicorn
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer


def resolve_device(device_override: str | None) -> str:
    if device_override:
        return device_override
    return "cuda" if torch.cuda.is_available() else "cpu"


@dataclass
class ServerConfig:
    model_name: str = "all-MiniLM-L6-v2"
    device: str | None = None
    batch_size: int = 32
    normalize_embeddings: bool = False
    show_progress_bar: bool = False
    host: str = "127.0.0.1"
    port: int = 8501


DEFAULT_CONFIG = ServerConfig()


app = FastAPI()


class Texts(BaseModel):
    texts: list[str]


def configure_application(config: ServerConfig) -> None:
    model = SentenceTransformer(config.model_name, device=config.device)

    app.state.config = config
    app.state.model = model


def _to_serializable(value):
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, (list, tuple)):
        return [_to_serializable(item) for item in value]
    return value


@app.post("/embed")
async def embed(payload: Texts):
    config: ServerConfig = app.state.config
    model: SentenceTransformer = app.state.model

    embeddings = await run_in_threadpool(
        model.encode,
        payload.texts,
        batch_size=config.batch_size,
        convert_to_numpy=True,
        normalize_embeddings=config.normalize_embeddings,
        show_progress_bar=config.show_progress_bar,
        device=config.device,
    )

    return {"embeddings": _to_serializable(embeddings)}


@app.get("/health")
def health():
    config: ServerConfig = app.state.config
    return {
        "model": config.model_name,
        "device": config.device,
        "batch_size": config.batch_size,
        "normalize_embeddings": config.normalize_embeddings,
        "show_progress_bar": config.show_progress_bar,
    }


@click.command()
@click.option(
    "--model",
    "model_name",
    default=DEFAULT_CONFIG.model_name,
    show_default=True,
    help="SentenceTransformer model identifier or local path.",
)
@click.option(
    "--device",
    default=None,
    show_default=False,
    help="Torch device to run inference on. Defaults to CUDA if available, otherwise CPU.",
)
@click.option(
    "--batch-size",
    default=DEFAULT_CONFIG.batch_size,
    show_default=True,
    type=int,
    help="Batch size for encoding requests.",
)
@click.option(
    "--normalize/--no-normalize",
    "normalize_embeddings",
    default=DEFAULT_CONFIG.normalize_embeddings,
    show_default=True,
    help="Toggle L2 normalization on the returned embeddings.",
)
@click.option(
    "--show-progress/--no-show-progress",
    "show_progress_bar",
    default=DEFAULT_CONFIG.show_progress_bar,
    show_default=True,
    help="Toggle the SentenceTransformer progress bar during encoding.",
)
@click.option(
    "--host",
    default=DEFAULT_CONFIG.host,
    show_default=True,
    help="Host interface for the Uvicorn server.",
)
@click.option(
    "--port",
    default=DEFAULT_CONFIG.port,
    show_default=True,
    type=int,
    help="Port for the Uvicorn server.",
)
def main(
    model_name: str,
    device: str | None,
    batch_size: int,
    normalize_embeddings: bool,
    show_progress_bar: bool,
    host: str,
    port: int,
) -> None:
    """Run the sentence transformer inference service."""

    config = ServerConfig(
        model_name=model_name,
        device=resolve_device(device),
        batch_size=batch_size,
        normalize_embeddings=normalize_embeddings,
        show_progress_bar=show_progress_bar,
        host=host,
        port=port,
    )

    configure_application(config)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
