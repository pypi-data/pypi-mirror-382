# Copyright (c) 2025 Apple Inc. Licensed under MIT License.

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .utils import Hasher, cache_path, logger


@dataclass
class Projection:
    # Array with shape (N, embedding_dim), the high-dimensional embedding
    projection: np.ndarray

    knn_indices: np.ndarray
    knn_distances: np.ndarray

    @staticmethod
    def exists(path: Path):
        return (
            path.with_suffix(".projection.npy").exists()
            and path.with_suffix(".knn_indices.npy").exists()
            and path.with_suffix(".knn_distances.npy").exists()
        )

    @staticmethod
    def save(path: Path, value: "Projection"):
        np.save(
            path.with_suffix(".projection.npy"),
            value.projection,
            allow_pickle=False,
        )
        np.save(
            path.with_suffix(".knn_indices.npy"),
            value.knn_indices,
            allow_pickle=False,
        )
        np.save(
            path.with_suffix(".knn_distances.npy"),
            value.knn_distances,
            allow_pickle=False,
        )

    @staticmethod
    def load(path: Path) -> "Projection":
        return Projection(
            projection=np.load(
                path.with_suffix(".projection.npy"),
                allow_pickle=False,
            ),
            knn_indices=np.load(
                path.with_suffix(".knn_indices.npy"),
                allow_pickle=False,
            ),
            knn_distances=np.load(
                path.with_suffix(".knn_distances.npy"),
                allow_pickle=False,
            ),
        )


def _run_umap(
    hidden_vectors: np.ndarray,
    umap_args: dict = {},
) -> Projection:
    logger.info("Running UMAP for input with shape %s...", str(hidden_vectors.shape))  # type: ignore

    import umap
    from umap.umap_ import nearest_neighbors

    metric = umap_args.get("metric", "cosine")
    n_neighbors = umap_args.get("n_neighbors", 15)

    knn = nearest_neighbors(
        hidden_vectors,
        n_neighbors=n_neighbors,
        metric=metric,
        metric_kwds=None,
        angular=False,
        random_state=None,
    )

    proj = umap.UMAP(**umap_args, precomputed_knn=knn)
    result: np.ndarray = proj.fit_transform(hidden_vectors)  # type: ignore

    return Projection(projection=result, knn_indices=knn[0], knn_distances=knn[1])


def _projection_for_texts(
    texts: list[str],
    model: str | None = None,
    trust_remote_code: bool = False,
    batch_size: int | None = None,
    umap_args: dict = {},
) -> Projection:
    if model is None:
        model = "all-MiniLM-L6-v2"
    hasher = Hasher()
    hasher.update(
        {
            "version": 1,
            "texts": texts,
            "model": model,
            "batch_size": batch_size,
            "umap_args": umap_args,
        }
    )
    digest = hasher.hexdigest()
    cpath = cache_path("projections") / digest

    if Projection.exists(cpath):
        logger.info("Using cached projection from %s", str(cpath))
        return Projection.load(cpath)

    # Import on demand.
    from sentence_transformers import SentenceTransformer

    # Set default batch size if not provided
    if batch_size is None:
        batch_size = 32
        logger.info("Using default batch size of %d for text. Adjust with --batch-size if you encounter memory issues or want to speed up processing.", batch_size)

    logger.info("Loading model %s...", model)
    transformer = SentenceTransformer(model, trust_remote_code=trust_remote_code)

    logger.info("Running embedding for %d texts with batch size %d...", len(texts), batch_size)
    hidden_vectors = transformer.encode(texts, batch_size=batch_size)

    result = _run_umap(hidden_vectors, umap_args)
    Projection.save(cpath, result)
    return result


def _projection_for_images(
    images: list,
    model: str | None = None,
    trust_remote_code: bool = False,
    batch_size: int | None = None,
    umap_args: dict = {},
) -> Projection:
    if model is None:
        model = "google/vit-base-patch16-384"
    hasher = Hasher()
    hasher.update(
        {
            "version": 1,
            "images": images,
            "model": model,
            "batch_size": batch_size,
            "umap_args": umap_args,
        }
    )
    digest = hasher.hexdigest()
    cpath = cache_path("projections") / (digest + ".npy")

    if Projection.exists(cpath):
        logger.info("Using cached projection from %s", str(cpath))
        return Projection.load(cpath)

    # Import on demand.
    from io import BytesIO

    import torch
    import tqdm
    from PIL import Image
    from transformers import pipeline

    def load_image(value):
        if isinstance(value, bytes):
            return Image.open(BytesIO(value)).convert("RGB")
        elif isinstance(value, dict) and "bytes" in value:
            return Image.open(BytesIO(value["bytes"])).convert("RGB")
        else:
            raise ValueError("invalid image value")

    logger.info("Loading model %s...", model)

    pipe = pipeline("image-feature-extraction", model=model, device_map="auto")

    # Set default batch size if not provided
    if batch_size is None:
        batch_size = 16
        logger.info("Using default batch size of %d for images. Adjust with --batch-size if you encounter memory issues or want to speed up processing.", batch_size)
    
    logger.info("Running embedding for %d images with batch size %d...", len(images), batch_size)
    tensors = []

    current_batch = []

    @torch.no_grad()
    def process_batch():
        rs: torch.Tensor = pipe(current_batch, return_tensors=True)  # type: ignore
        current_batch.clear()
        for r in rs:
            if len(r.shape) == 3:
                r = r.mean(1)
            assert len(r.shape) == 2
            tensors.append(r)

    for image in tqdm.tqdm(images, smoothing=0.1):
        current_batch.append(load_image(image))
        if len(current_batch) >= batch_size:
            process_batch()
    process_batch()

    hidden_vectors = torch.concat(tensors).to(torch.float32).cpu().numpy()

    result = _run_umap(hidden_vectors, umap_args)
    Projection.save(cpath, result)
    return result


def compute_text_projection(
    data_frame: pd.DataFrame,
    text: str,
    x: str = "projection_x",
    y: str = "projection_y",
    neighbors: str | None = "neighbors",
    model: str | None = None,
    trust_remote_code: bool = False,
    batch_size: int | None = None,
    umap_args: dict = {},
):
    """
    Compute text embeddings and generate 2D projections using UMAP.

    This function processes text data by creating embeddings using a SentenceTransformer
    model and then reducing the dimensionality to 2D coordinates using UMAP for
    visualization purposes.

    Args:
        data_frame: pandas DataFrame containing the text data to process.
        text: str, column name containing the texts to embed.
        x: str, column name where the UMAP X coordinates will be stored.
        y: str, column name where the UMAP Y coordinates will be stored.
        neighbors: str, column name where the nearest neighbor indices will be stored.
        model: str, name or path of the SentenceTransformer model to use for embedding.
        trust_remote_code: bool, whether to trust and execute remote code when loading
            the model from HuggingFace Hub. Default is False.
        batch_size: int, batch size for processing embeddings. Larger values use more 
            memory but may be faster. Default is 32.
        umap_args: dict, additional keyword arguments to pass to the UMAP algorithm
            (e.g., n_neighbors, min_dist, metric).

    Returns:
        The input DataFrame with added columns for X, Y coordinates and nearest neighbors.
    """

    text_series = data_frame[text].astype(str).fillna("")
    proj = _projection_for_texts(
        list(text_series),
        model=model,
        trust_remote_code=trust_remote_code,
        batch_size=batch_size,
        umap_args=umap_args,
    )
    data_frame[x] = proj.projection[:, 0]
    data_frame[y] = proj.projection[:, 1]
    if neighbors is not None:
        data_frame[neighbors] = [
            {"distances": b, "ids": a}  # ID is always the same as the row index.
            for a, b in zip(proj.knn_indices, proj.knn_distances)
        ]


def compute_vector_projection(
    data_frame: pd.DataFrame,
    vector: str,
    x: str = "projection_x",
    y: str = "projection_y",
    neighbors: str | None = "neighbors",
    umap_args: dict = {},
):
    """
    Generate 2D projections from pre-existing vector embeddings using UMAP.

    This function takes pre-computed vector embeddings and reduces their dimensionality
    to 2D coordinates using UMAP for visualization purposes.

    Args:
        data_frame: pandas DataFrame containing the vector data to process.
        vector: str, column name containing the pre-computed vector embeddings.
                Each entry should be a list or numpy array of numbers.
        x: str, column name where the UMAP X coordinates will be stored.
        y: str, column name where the UMAP Y coordinates will be stored.
        neighbors: str, column name where the nearest neighbor indices will be stored.
        umap_args: dict, additional keyword arguments to pass to the UMAP algorithm
            (e.g., n_neighbors, min_dist, metric).

    Returns:
        The input DataFrame with added columns for X, Y coordinates and nearest neighbors.
    """
    # Convert vector column to numpy array
    vector_series = data_frame[vector]

    # Convert each vector entry to numpy array and stack them
    vector_list = []
    for vector in vector_series:
        if isinstance(vector, list):
            vector_array = np.array(vector)
        elif isinstance(vector, np.ndarray):
            vector_array = vector
        else:
            # Try to convert to numpy array
            vector_array = np.array(vector)
        vector_list.append(vector_array)

    # Stack all vectors into a single numpy array
    hidden_vectors = np.stack(vector_list)

    # Run UMAP on the pre-existing vectors
    proj = _run_umap(hidden_vectors, umap_args)

    # Add projection results to dataframe
    data_frame[x] = proj.projection[:, 0]
    data_frame[y] = proj.projection[:, 1]
    if neighbors is not None:
        data_frame[neighbors] = [
            {"distances": b, "ids": a}  # ID is always the same as the row index.
            for a, b in zip(proj.knn_indices, proj.knn_distances)
        ]


def compute_image_projection(
    data_frame: pd.DataFrame,
    image: str,
    x: str = "projection_x",
    y: str = "projection_y",
    neighbors: str | None = "neighbors",
    model: str | None = None,
    trust_remote_code: bool = False,
    batch_size: int | None = None,
    umap_args: dict = {},
):
    """
    Compute image embeddings and generate 2D projections using UMAP.

    This function processes image data by creating embeddings using a model and
    then reducing the dimensionality to 2D coordinates using UMAP for
    visualization purposes.

    Args:
        data_frame: pandas DataFrame containing the image data to process.
        image: str, column name containing the images to embed.
        x: str, column name where the UMAP X coordinates will be stored.
        y: str, column name where the UMAP Y coordinates will be stored.
        neighbors: str, column name where the nearest neighbor indices will be stored.
        model: str, name or path of the model to use for embedding.
        trust_remote_code: bool, whether to trust and execute remote code when loading
            the model from HuggingFace Hub. Default is False.
        batch_size: int, batch size for processing images. Larger values use more 
            memory but may be faster. Default is 16.
        umap_args: dict, additional keyword arguments to pass to the UMAP algorithm
            (e.g., n_neighbors, min_dist, metric).

    Returns:
        The input DataFrame with added columns for X, Y coordinates and nearest neighbors.
    """

    image_series = data_frame[image]
    proj = _projection_for_images(
        list(image_series),
        model=model,
        trust_remote_code=trust_remote_code,
        batch_size=batch_size,
        umap_args=umap_args,
    )
    data_frame[x] = proj.projection[:, 0]
    data_frame[y] = proj.projection[:, 1]
    if neighbors is not None:
        data_frame[neighbors] = [
            {"distances": b, "ids": a}  # ID is always the same as the row index.
            for a, b in zip(proj.knn_indices, proj.knn_distances)
        ]
