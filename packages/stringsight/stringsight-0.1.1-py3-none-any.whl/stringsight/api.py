"""
Minimal FastAPI app exposing validation and conversation formatting.

Endpoints:
- GET /health
- POST /detect-and-validate   → parse, auto-detect, validate, preview
- POST /conversations         → parse, auto-detect, validate, return traces

This module is isolated from the Gradio app. It can be run independently:
    uvicorn stringsight.api:app --reload --port 8000
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
import io
import os

import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

from stringsight.formatters import (
    Method,
    detect_method,
    validate_required_columns,
    format_conversations,
)
from stringsight.utils.df_utils import explode_score_columns
from stringsight import public as public_api
from stringsight.clusterers import get_clusterer
from stringsight.metrics.cluster_subset import prepare_long_frame, compute_subset_metrics, enrich_clusters_with_metrics, compute_total_conversations_by_model
import threading, uuid
from dataclasses import dataclass, field


def _get_base_browse_dir() -> Path:
    """Return the base directory allowed for server-side browsing.

    Defaults to the current working directory. You can override by setting
    environment variable `BASE_BROWSE_DIR` to an absolute path.
    """
    env = os.environ.get("BASE_BROWSE_DIR")
    base = Path(env).expanduser().resolve() if env else Path.cwd()
    return base


def _resolve_within_base(user_path: str) -> Path:
    """Resolve a user-supplied path and ensure it is within the allowed base.

    Args:
        user_path: Path provided by the client (file or directory)

    Returns:
        Absolute `Path` guaranteed to be within the base directory

    Raises:
        HTTPException: if the path is invalid or escapes the base directory
    """
    base = _get_base_browse_dir()
    target = Path(user_path).expanduser()
    # Treat relative paths as relative to base
    target = (base / target).resolve() if not target.is_absolute() else target.resolve()
    try:
        target.relative_to(base)
    except Exception:
        raise HTTPException(status_code=400, detail="Path is outside the allowed base directory")
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {target}")
    return target


def _read_json_safe(path: Path) -> Any:
    """Read a JSON file from disk into a Python object."""
    import json
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_jsonl_as_list(path: Path, nrows: Optional[int] = None) -> List[Dict[str, Any]]:
    """Read a JSONL file into a list of dicts. Optional row cap."""
    import json
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if nrows is not None and (i + 1) >= nrows:
                break
    return rows

class RowsPayload(BaseModel):
    rows: List[Dict[str, Any]]
    method: Optional[Literal["single_model", "side_by_side"]] = None


class ReadRequest(BaseModel):
    """Request body for reading a dataset from the server filesystem.

    Use with caution – this assumes the server has access to the path.
    """
    path: str
    method: Optional[Literal["single_model", "side_by_side"]] = None
    limit: Optional[int] = None  # return all rows if None


class ListRequest(BaseModel):
    path: str  # directory to list (server-side)
    exts: Optional[List[str]] = None  # e.g., [".jsonl", ".json", ".csv"]


class ResultsLoadRequest(BaseModel):
    """Request to load a results directory from the server filesystem.

    Attributes:
        path: Absolute or base-relative path to the results directory, which must
              be within BASE_BROWSE_DIR (defaults to current working directory).
        max_conversations: Maximum number of conversations to load (default: all).
                          Use this to limit memory usage for large datasets.
        max_properties: Maximum number of properties to load (default: all).
    """
    path: str
    max_conversations: Optional[int] = None
    max_properties: Optional[int] = None


class FlexibleColumnMapping(BaseModel):
    """Column mapping specification for flexible data processing."""
    prompt_col: str
    response_cols: List[str]
    model_cols: Optional[List[str]] = None
    score_cols: Optional[List[str]] = None
    method: Literal["single_model", "side_by_side"] = "single_model"


class FlexibleDataRequest(BaseModel):
    """Request for flexible data processing with user-specified column mapping."""
    rows: List[Dict[str, Any]]
    mapping: FlexibleColumnMapping


class AutoDetectRequest(BaseModel):
    """Request for auto-detecting column mappings."""
    rows: List[Dict[str, Any]]  # Sample of data for detection


# -----------------------------
# Extraction endpoints schemas
# -----------------------------

class ExtractSingleRequest(BaseModel):
    row: Dict[str, Any]
    method: Optional[Literal["single_model", "side_by_side"]] = None
    system_prompt: Optional[str] = None
    task_description: Optional[str] = None
    model_name: Optional[str] = "gpt-4.1"
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    max_tokens: Optional[int] = 16000
    max_workers: Optional[int] = 16
    include_scores_in_prompt: Optional[bool] = True
    use_wandb: Optional[bool] = False
    output_dir: Optional[str] = None
    return_debug: Optional[bool] = False


class ExtractBatchRequest(BaseModel):
    rows: List[Dict[str, Any]]
    method: Optional[Literal["single_model", "side_by_side"]] = None
    system_prompt: Optional[str] = None
    task_description: Optional[str] = None
    model_name: Optional[str] = "gpt-4.1"
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    max_tokens: Optional[int] = 16000
    max_workers: Optional[int] = 16
    include_scores_in_prompt: Optional[bool] = True
    use_wandb: Optional[bool] = False
    output_dir: Optional[str] = None
    return_debug: Optional[bool] = False


# -----------------------------
# DataFrame operation schemas
# -----------------------------

class DFRows(BaseModel):
    rows: List[Dict[str, Any]]


class DFSelectRequest(DFRows):
    include: Dict[str, List[Any]] = {}
    exclude: Dict[str, List[Any]] = {}


class DFGroupPreviewRequest(DFRows):
    by: str
    numeric_cols: Optional[List[str]] = None


class DFGroupRowsRequest(DFRows):
    by: str
    value: Any
    page: int = 1
    page_size: int = 10


class DFCustomRequest(DFRows):
    code: str  # pandas expression using df


def _load_dataframe_from_upload(upload: UploadFile) -> pd.DataFrame:
    filename = (upload.filename or "").lower()
    raw = upload.file.read()
    # Decode text formats
    if filename.endswith(".jsonl"):
        text = raw.decode("utf-8")
        return pd.read_json(io.StringIO(text), lines=True)
    if filename.endswith(".json"):
        text = raw.decode("utf-8")
        return pd.read_json(io.StringIO(text))
    if filename.endswith(".csv"):
        text = raw.decode("utf-8")
        return pd.read_csv(io.StringIO(text))
    raise HTTPException(status_code=400, detail="Unsupported file format. Use JSONL, JSON, or CSV.")


def _load_dataframe_from_rows(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _load_dataframe_from_path(path: str) -> pd.DataFrame:
    p = path.lower()
    if p.endswith(".jsonl"):
        return pd.read_json(path, lines=True)
    if p.endswith(".json"):
        return pd.read_json(path)
    if p.endswith(".csv"):
        return pd.read_csv(path)
    raise HTTPException(status_code=400, detail="Unsupported file format. Use JSONL, JSON, or CSV.")


def _resolve_df_and_method(
    file: UploadFile | None,
    payload: RowsPayload | None,
) -> tuple[pd.DataFrame, Method]:
    if not file and not payload:
        raise HTTPException(status_code=400, detail="Provide either a file upload or a rows payload.")

    if file:
        df = _load_dataframe_from_upload(file)
        detected = detect_method(list(df.columns))
        method = detected or (payload.method if payload else None)  # type: ignore[assignment]
    else:
        assert payload is not None
        df = _load_dataframe_from_rows(payload.rows)
        method = payload.method or detect_method(list(df.columns))

    if method is None:
        raise HTTPException(status_code=422, detail="Unable to detect dataset method from columns.")

    # Validate required columns strictly (no defaults)
    missing = validate_required_columns(df, method)
    if missing:
        raise HTTPException(
            status_code=422,
            detail={
                "error": f"Missing required columns for {method}",
                "missing": missing,
                "available": list(df.columns),
            },
        )

    return df, method


app = FastAPI(title="LMM-Vibes API", version="0.1.0")

# Allow local Vite dev server by default - be permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
)

# Include metrics endpoints (basic file serving)
@app.get("/metrics/summary/{results_dir}")
def get_metrics_summary(results_dir: str) -> Dict[str, Any]:
    """Get basic summary of available metrics files."""
    try:
        from pathlib import Path
        import pandas as pd
        
        base_path = Path("results") / results_dir
        model_cluster_file = base_path / "model_cluster_scores_df.jsonl"
        
        if not model_cluster_file.exists():
            raise HTTPException(status_code=404, detail=f"Metrics data not found for {results_dir}")
        
        # Read a small sample to get basic info
        df = pd.read_json(model_cluster_file, lines=True, nrows=100)
        models = sorted(df['model'].unique().tolist()) if 'model' in df.columns else []
        clusters = df['cluster'].unique().tolist() if 'cluster' in df.columns else []
        
        # Extract quality metrics from column names
        quality_metrics = []
        for col in df.columns:
            if col.startswith('quality_') and not col.endswith(('_delta', '_significant')):
                metric = col.replace('quality_', '')
                if metric not in quality_metrics:
                    quality_metrics.append(metric)
        
        return {
            "source": "jsonl",
            "models": len(models),
            "clusters": len(clusters),
            "total_battles": len(df),
            "has_confidence_intervals": any("_ci_" in col for col in df.columns),
            "quality_metric_names": quality_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading metrics: {str(e)}")


@app.get("/metrics/model-cluster/{results_dir}")  
def get_model_cluster_metrics(results_dir: str) -> Dict[str, Any]:
    """Get model-cluster metrics data."""
    try:
        from pathlib import Path
        import pandas as pd
        
        base_path = Path("results") / results_dir
        model_cluster_file = base_path / "model_cluster_scores_df.jsonl"
        
        if not model_cluster_file.exists():
            raise HTTPException(status_code=404, detail=f"Model-cluster data not found for {results_dir}")
        
        df = pd.read_json(model_cluster_file, lines=True)
        
        models = sorted(df['model'].unique().tolist()) if 'model' in df.columns else []
        clusters = df['cluster'].unique().tolist() if 'cluster' in df.columns else []
        
        return {
            "source": "jsonl",
            "models": models,
            "data": df.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model-cluster data: {str(e)}")


@app.get("/metrics/benchmark/{results_dir}")
def get_benchmark_metrics(results_dir: str) -> Dict[str, Any]:
    """Get benchmark metrics data."""
    try:
        from pathlib import Path
        import pandas as pd
        
        base_path = Path("results") / results_dir
        model_scores_file = base_path / "model_scores_df.jsonl"
        
        if not model_scores_file.exists():
            raise HTTPException(status_code=404, detail=f"Benchmark data not found for {results_dir}")
        
        df = pd.read_json(model_scores_file, lines=True)
        
        models = sorted(df['model'].unique().tolist()) if 'model' in df.columns else []
        
        return {
            "source": "jsonl",
            "models": models,
            "data": df.to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading benchmark data: {str(e)}")


@app.get("/metrics/quality-metrics/{results_dir}")
def get_quality_metrics(results_dir: str) -> Dict[str, Any]:
    """Get available quality metrics."""
    try:
        from pathlib import Path
        import pandas as pd
        
        base_path = Path("results") / results_dir
        model_cluster_file = base_path / "model_cluster_scores_df.jsonl"
        
        if not model_cluster_file.exists():
            raise HTTPException(status_code=404, detail=f"Metrics data not found for {results_dir}")
        
        # Read just the first row to get column names
        df = pd.read_json(model_cluster_file, lines=True, nrows=1)
        
        # Extract quality metrics from column names
        quality_metrics = []
        for col in df.columns:
            if col.startswith('quality_') and not col.endswith(('_delta', '_significant')):
                metric = col.replace('quality_', '')
                if metric not in quality_metrics:
                    quality_metrics.append(metric)
        
        return {"quality_metrics": quality_metrics}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading quality metrics: {str(e)}")


@app.get("/health")
def health() -> Dict[str, bool]:
    print("🟢 BACKEND: Health check called")
    return {"ok": True}


# -----------------------------
# Clustering/metrics – embedding models
# -----------------------------

@app.get("/embedding-models")
def get_embedding_models() -> Dict[str, Any]:
    """Return a curated list of embedding model identifiers.

    Later we can make this dynamic via config/env. Keep it simple for now.
    """
    models = [
        "openai/text-embedding-3-large",
        "openai/text-embedding-3-small",
        "bge-m3",
        "sentence-transformers/all-MiniLM-L6-v2",
    ]
    return {"models": models}

@app.get("/debug")
def debug() -> Dict[str, Any]:
    print("🟢 BACKEND: Debug endpoint called")
    return {"status": "server_running", "message": "Backend is alive!"}

@app.post("/debug/post")
def debug_post(body: Dict[str, Any]) -> Dict[str, Any]:
    print(f"🟢 BACKEND: Debug POST called with keys: {list(body.keys())}")
    return {"status": "post_working", "received_keys": list(body.keys())}


# -----------------------------
# Clustering + Metrics Orchestration (simple contracts)
# -----------------------------

class ClusterRunParams(BaseModel):
    minClusterSize: int | None = None
    embeddingModel: str = "openai/text-embedding-3-large"
    groupBy: Optional[str] = "none"  # none | category | behavior_type


class ClusterRunRequest(BaseModel):
    operationalRows: List[Dict[str, Any]]
    properties: List[Dict[str, Any]]
    params: ClusterRunParams
    output_dir: Optional[str] = None


@app.post("/cluster/run")
def cluster_run(req: ClusterRunRequest) -> Dict[str, Any]:
    """Run clustering directly on existing properties without re-running extraction.
    
    This is much more efficient than the full explain() pipeline since it skips
    the expensive LLM property extraction step and works with already-extracted properties.
    
    Note: Cache is disk-backed and thread-safe; no LMDB toggles required.
    """
    from stringsight.core.data_objects import PropertyDataset, Property, ConversationRecord
    from stringsight.clusterers import get_clusterer
    import os
    
    # No-op: LMDB has been removed; keep structure for future toggles if needed
    original_cache_setting = os.environ.get("STRINGSIGHT_DISABLE_CACHE", "0")
    os.environ["STRINGSIGHT_DISABLE_CACHE"] = original_cache_setting

    # Force-drop any pre-initialized global LMDB caches so this request runs cacheless
    from stringsight.core import llm_utils as _llm_utils
    from stringsight.clusterers import clustering_utils as _cu
    _orig_default_cache = getattr(_llm_utils, "_default_cache", None)
    _orig_default_llm_utils = getattr(_llm_utils, "_default_llm_utils", None)
    _orig_embed_cache = getattr(_cu, "_cache", None)
    try:
        _llm_utils._default_cache = None
        _llm_utils._default_llm_utils = None
    except Exception:
        pass
    try:
        if hasattr(_cu, "_cache"):
            _cu._cache = None
    except Exception:
        pass
    
    try:
        # Convert properties data to Property objects
        properties: List[Property] = []
        for p in req.properties:
            try:
                prop = Property(
                    id=str(p.get("id", "")),
                    question_id=str(p.get("question_id", "")),
                    model=str(p.get("model", "")),
                    property_description=p.get("property_description"),
                    category=p.get("category"),
                    reason=p.get("reason"),
                    evidence=p.get("evidence"),
                    behavior_type=p.get("behavior_type"),
                    raw_response=p.get("raw_response"),
                    contains_errors=p.get("contains_errors"),
                    unexpected_behavior=p.get("unexpected_behavior"),
                    meta=p.get("meta", {})
                )
                properties.append(prop)
            except Exception as e:
                print(f"Warning: Skipping invalid property: {e}")
                continue
        
        if not properties:
            return {"clusters": []}
        
        # Create minimal conversations that match the properties for to_dataframe() to work
        # We need conversations with matching (question_id, model) pairs for the merge to work
        conversations: List[ConversationRecord] = []
        all_models = set()
        
        # Create a set of unique (question_id, model) pairs from properties
        property_keys = {(prop.question_id, prop.model) for prop in properties}
        
        print(f"🔍 DEBUG: Found {len(property_keys)} unique (question_id, model) pairs from {len(properties)} properties")
        
        # Create exactly one conversation per unique (question_id, model) pair
        for question_id, model in property_keys:
            all_models.add(model)
            
            # Find matching operational row for this conversation
            matching_row = None
            for row in req.operationalRows:
                if (str(row.get("question_id", "")) == question_id and 
                    str(row.get("model", "")) == model):
                    matching_row = row
                    break
            
            # Create minimal conversation (use empty data if no matching row found)
            conv = ConversationRecord(
                question_id=question_id,
                model=model,
                prompt=matching_row.get("prompt", "") if matching_row else "",
                responses=matching_row.get("model_response", "") if matching_row else "",
                scores=matching_row.get("score", {}) if matching_row else {},
                meta={}
            )
            conversations.append(conv)
        
        # Create PropertyDataset with matching conversations and properties
        dataset = PropertyDataset(
            conversations=conversations,
            all_models=list(all_models),
            properties=properties,
            clusters=[],  # Will be populated by clustering
            model_stats={}
        )
        
        print(f"🔍 DEBUG: PropertyDataset created with:")
        print(f"  - {len(dataset.properties)} properties")
        print(f"  - {len(dataset.conversations)} conversations") 
        print(f"  - Models: {dataset.all_models}")
        
        if dataset.properties:
            print(f"🔍 DEBUG: Sample properties:")
            for i, prop in enumerate(dataset.properties[:3]):
                print(f"  Property {i}: id={prop.id}, question_id={prop.question_id}, model={prop.model}")
                print(f"    description: {prop.property_description}")
        
        # Run clustering only (no extraction)
        # Convert groupBy parameter to groupby_column (none -> None for no grouping)
        groupby_column = None if req.params.groupBy == "none" else req.params.groupBy
        
        print(f"🔍 DEBUG: Clustering parameters:")
        print(f"  - groupBy from request: {req.params.groupBy}")
        print(f"  - groupby_column for clusterer: {groupby_column}")
        print(f"  - min_cluster_size: {req.params.minClusterSize}")
        print(f"  - embedding_model: {req.params.embeddingModel}")
        
        clusterer = get_clusterer(
            method="hdbscan",
            min_cluster_size=req.params.minClusterSize,
            embedding_model=req.params.embeddingModel,
            hierarchical=False,
            assign_outliers=False,
            include_embeddings=False,
            cache_embeddings=False,
            groupby_column=groupby_column,
        )
        
        # Run clustering
        clustered_dataset = clusterer.run(dataset, column_name="property_description")
        
    finally:
        # Restore original cache/env settings (no-op for DiskCache)
        os.environ["STRINGSIGHT_DISABLE_CACHE"] = original_cache_setting
        # Restore global caches
        try:
            _llm_utils._default_cache = _orig_default_cache
            _llm_utils._default_llm_utils = _orig_default_llm_utils
        except Exception:
            pass
        try:
            if hasattr(_cu, "_cache"):
                _cu._cache = _orig_embed_cache
        except Exception:
            pass

    # Convert clusters to API format
    clusters: List[Dict[str, Any]] = []
    for cluster in clustered_dataset.clusters:
        clusters.append({
            "id": cluster.id,
            "label": cluster.label,
            "size": cluster.size,
            "parent_id": cluster.parent_id,
            "parent_label": cluster.parent_label,
            "property_descriptions": cluster.property_descriptions,
            "property_ids": cluster.property_ids,
            "question_ids": cluster.question_ids,
            "meta": cluster.meta,
        })
    
    # Enrich clusters with metrics using the subset helper
    long_df = prepare_long_frame(clusters=clusters, properties=req.properties, operational_rows=req.operationalRows)
    total_conversations = compute_total_conversations_by_model(req.properties)
    scores = compute_subset_metrics(long_df, total_conversations)
    enriched = enrich_clusters_with_metrics(clusters, scores)

    # Attach overall proportion and per-property model info for UI consumption
    try:
        cluster_scores = scores.get("cluster_scores", {})
        # Build a map of property_id -> { model, property_description }
        prop_by_id: Dict[str, Dict[str, Any]] = {}
        for p in req.properties:
            pid = str(p.get("id"))
            if not pid:
                continue
            prop_by_id[pid] = {
                "property_id": pid,
                "model": str(p.get("model", "")),
                "property_description": p.get("property_description"),
            }
        for c in enriched:
            label = c.get("label")
            cs = cluster_scores.get(label, {}) if isinstance(cluster_scores, dict) else {}
            # Overall proportion across all models (size / total unique convs in subset)
            c_meta = dict(c.get("meta", {}))
            if isinstance(cs.get("proportion"), (int, float)):
                c_meta["proportion_overall"] = float(cs["proportion"])  
            # Attach property_items with model next to each description
            items: List[Dict[str, Any]] = []
            property_ids_list = c.get("property_ids", []) or []
            
            # Debug: Check for duplicates in property_ids
            if len(property_ids_list) != len(set(str(pid) for pid in property_ids_list)):
                print(f"🚨 DEBUG: Cluster {label} has duplicate property_ids!")
                print(f"  - property_ids: {property_ids_list}")
                print(f"  - unique count: {len(set(str(pid) for pid in property_ids_list))}")
                print(f"  - total count: {len(property_ids_list)}")
            
            # Deduplicate property_ids while preserving order
            seen_pids = set()
            for pid in property_ids_list:
                pid_str = str(pid)
                if pid_str not in seen_pids:
                    seen_pids.add(pid_str)
                    rec = prop_by_id.get(pid_str)
                    if rec:
                        items.append(rec)
            if items:
                c_meta["property_items"] = items
            c["meta"] = c_meta
    except Exception:
        # Best-effort enrichment; do not fail clustering if this post-process fails
        pass
    
    # Sort by size desc
    enriched = sorted(enriched, key=lambda c: c.get("size", 0), reverse=True)
    
    # Calculate total unique conversations in the dataset for the frontend
    total_unique_conversations = len(set(str(p.get("question_id", "")) for p in req.properties if p.get("question_id")))
    
    return {
        "clusters": enriched,
        "total_conversations_by_model": total_conversations,
        "total_unique_conversations": total_unique_conversations
    }


class ClusterMetricsRequest(BaseModel):
    clusters: List[Dict[str, Any]]
    properties: List[Dict[str, Any]]
    operationalRows: List[Dict[str, Any]]
    included_property_ids: Optional[List[str]] = None


@app.post("/cluster/metrics")
def cluster_metrics(req: ClusterMetricsRequest) -> Dict[str, Any]:
    """Recompute cluster metrics for a filtered subset without reclustering."""
    long_df = prepare_long_frame(
        clusters=req.clusters,
        properties=req.properties,
        operational_rows=req.operationalRows,
        included_property_ids=req.included_property_ids,
    )
    total_conversations = compute_total_conversations_by_model(req.properties)
    scores = compute_subset_metrics(long_df, total_conversations)
    enriched = enrich_clusters_with_metrics(req.clusters, scores)
    enriched = sorted(enriched, key=lambda c: c.get("size", 0), reverse=True)
    
    # Calculate total unique conversations in the dataset for the frontend
    total_unique_conversations = len(set(str(p.get("question_id", "")) for p in req.properties if p.get("question_id")))
    
    return {
        "clusters": enriched,
        "total_conversations_by_model": total_conversations,
        "total_unique_conversations": total_unique_conversations
    }


@app.post("/detect-and-validate")
def detect_and_validate(
    file: UploadFile | None = File(default=None),
    payload: RowsPayload | None = Body(default=None),
) -> Dict[str, Any]:
    if not file and not payload:
        raise HTTPException(status_code=400, detail="Provide either a file or a rows payload.")

    if file:
        df = _load_dataframe_from_upload(file)
        method = detect_method(list(df.columns))
    else:
        assert payload is not None
        df = _load_dataframe_from_rows(payload.rows)
        method = payload.method or detect_method(list(df.columns))

    columns = list(df.columns)
    if method is None:
        return {
            "method": None,
            "valid": False,
            "missing": [],
            "row_count": int(len(df)),
            "columns": columns,
            "preview": df.head(50).to_dict(orient="records"),
        }

    missing = validate_required_columns(df, method)
    return {
        "method": method,
        "valid": len(missing) == 0,
        "missing": missing,
        "row_count": int(len(df)),
        "columns": columns,
        "preview": df.head(50).to_dict(orient="records"),
    }


@app.post("/conversations")
def conversations(
    file: UploadFile | None = File(default=None),
    payload: RowsPayload | None = Body(default=None),
) -> Dict[str, Any]:
    df, method = _resolve_df_and_method(file, payload)
    # Normalize score columns for convenience in clients
    try:
        df = explode_score_columns(df, method)
    except Exception:
        pass
    traces = format_conversations(df, method)
    return {"method": method, "conversations": traces}


@app.post("/read-path")
def read_path(req: ReadRequest) -> Dict[str, Any]:
    """Read a dataset from a server path, auto-detect/validate, return preview and method."""
    path = _resolve_within_base(req.path)
    if not path.is_file():
        raise HTTPException(status_code=400, detail=f"Not a file: {path}")
    try:
        df = _load_dataframe_from_path(str(path))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    method = req.method or detect_method(list(df.columns))
    if method is None:
        raise HTTPException(status_code=422, detail="Unable to detect dataset method from columns.")

    missing = validate_required_columns(df, method)
    if missing:
        raise HTTPException(status_code=422, detail={"error": f"Missing required columns for {method}", "missing": missing})

    # Optionally flatten scores
    try:
        df = explode_score_columns(df, method)
    except Exception:
        pass

    out_df = df.head(req.limit) if isinstance(req.limit, int) and req.limit > 0 else df
    return {
        "method": method,
        "row_count": int(len(df)),
        "columns": list(df.columns),
        "preview": out_df.to_dict(orient="records"),
    }


@app.post("/list-path")
def list_path(req: ListRequest) -> Dict[str, Any]:
    """List files and folders at a server directory path.

    Returns entries with `name`, `path`, and `type` ("file"|"dir").
    If `exts` is provided, filters files by allowed extensions (case-insensitive).
    """
    base = _resolve_within_base(req.path)
    if not base.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {base}")

    allowed_exts = set(e.lower() for e in (req.exts or []))
    items: List[Dict[str, Any]] = []
    for name in sorted(os.listdir(str(base))):
        if name.startswith('.'):  # hide hidden files/dirs
            continue
        full = base / name
        if full.is_dir():
            items.append({"name": name, "path": str(full), "type": "dir"})
        else:
            ext = full.suffix.lower()
            if allowed_exts and ext not in allowed_exts:
                continue
            items.append({"name": name, "path": str(full), "type": "file"})

    return {"entries": items}


@app.post("/results/load")
def results_load(req: ResultsLoadRequest) -> Dict[str, Any]:
    """Load a results directory and return metrics plus optional dataset.

    Supports both JSON metrics (model_cluster_scores.json, cluster_scores.json,
    model_scores.json) and JSONL DataFrame exports (model_cluster_scores_df.jsonl,
    cluster_scores_df.jsonl, model_scores_df.jsonl). If a `full_dataset.json`
    file is present, returns its `conversations`, `properties`, and `clusters`.

    Request path must be within BASE_BROWSE_DIR (default: current working directory).
    """
    results_dir = _resolve_within_base(req.path)
    if not results_dir.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {results_dir}")

    # Try JSONL first (frontend-ready format), no JSON fallback needed
    model_cluster_scores: Optional[List[Dict[str, Any]]] = None
    cluster_scores: Optional[List[Dict[str, Any]]] = None
    model_scores: Optional[List[Dict[str, Any]]] = None

    # Load JSONL files directly
    p = results_dir / "model_cluster_scores_df.jsonl"
    if p.exists():
        model_cluster_scores = _read_jsonl_as_list(p)
    
    p = results_dir / "cluster_scores_df.jsonl"
    if p.exists():
        cluster_scores = _read_jsonl_as_list(p)
    
    p = results_dir / "model_scores_df.jsonl"
    if p.exists():
        model_scores = _read_jsonl_as_list(p)

    # Load conversations and properties from lightweight JSONL files for better performance
    conversations: List[Dict[str, Any]] = []
    properties: List[Dict[str, Any]] = []
    clusters: List[Dict[str, Any]] = []

    # Try lightweight JSONL first (much faster than full_dataset.json)
    lightweight_conv = results_dir / "clustered_results_lightweight.jsonl"
    if lightweight_conv.exists():
        try:
            conversations = _read_jsonl_as_list(lightweight_conv, nrows=req.max_conversations)
        except Exception as e:
            print(f"Warning: Failed to load lightweight conversations: {e}")

    # Load properties from parsed_properties.jsonl
    props_file = results_dir / "parsed_properties.jsonl"
    if props_file.exists():
        try:
            properties = _read_jsonl_as_list(props_file, nrows=req.max_properties)
        except Exception as e:
            print(f"Warning: Failed to load properties: {e}")

    # Fallback to full_dataset.json only if JSONL files don't exist
    if not conversations and not properties:
        full = results_dir / "full_dataset.json"
        if full.exists():
            payload = _read_json_safe(full)
            if isinstance(payload, dict):
                try:
                    c = payload.get("conversations")
                    p = payload.get("properties")
                    cl = payload.get("clusters")
                    if isinstance(c, list):
                        conversations = c[:req.max_conversations] if req.max_conversations else c
                    if isinstance(p, list):
                        properties = p[:req.max_properties] if req.max_properties else p
                    if isinstance(cl, list):
                        clusters = cl
                except Exception:
                    # Best-effort parsing; do not raise here.
                    pass

    # Load clusters from full_dataset.json if available (clusters are small)
    if not clusters:
        full = results_dir / "full_dataset.json"
        if full.exists():
            try:
                payload = _read_json_safe(full)
                if isinstance(payload, dict):
                    cl = payload.get("clusters")
                    if isinstance(cl, list):
                        clusters = cl
            except Exception:
                pass

    return {
        "path": str(results_dir),
        "model_cluster_scores": model_cluster_scores or [],
        "cluster_scores": cluster_scores or [],
        "model_scores": model_scores or [],
        "conversations": conversations,
        "properties": properties,
        "clusters": clusters,
    }


# -----------------------------
# DataFrame operations
# -----------------------------

def _df_from_rows(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


@app.post("/df/select")
def df_select(req: DFSelectRequest) -> Dict[str, Any]:
    df = _df_from_rows(req.rows)
    # Include filters (AND across columns, OR within column values)
    for col, values in (req.include or {}).items():
        if col in df.columns and values:
            # Be robust to type mismatches by comparing as strings too
            try:
                mask = df[col].isin(values)
            except Exception:
                mask = df[col].astype(str).isin([str(v) for v in values])
            df = df[mask]
    # Exclude filters
    for col, values in (req.exclude or {}).items():
        if col in df.columns and values:
            try:
                mask = ~df[col].isin(values)
            except Exception:
                mask = ~df[col].astype(str).isin([str(v) for v in values])
            df = df[mask]
    return {"rows": df.to_dict(orient="records")}


@app.post("/df/groupby/preview")
def df_groupby_preview(req: DFGroupPreviewRequest) -> Dict[str, Any]:
    try:
        print(f"🟢 BACKEND: df_groupby_preview called with by='{req.by}'")
        print(f"🟢 BACKEND: rows count: {len(req.rows)}")
        print(f"🟢 BACKEND: numeric_cols: {req.numeric_cols}")
        
        df = _df_from_rows(req.rows)
        print(f"🟢 BACKEND: DataFrame shape: {df.shape}")
        print(f"🟢 BACKEND: DataFrame columns: {list(df.columns)}")
        
        if req.by not in df.columns:
            print(f"🔴 BACKEND: Column '{req.by}' not found in data")
            raise HTTPException(status_code=400, detail=f"Column not found: {req.by}")
        
        # Determine numeric columns
        num_cols = req.numeric_cols or [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        print(f"🟢 BACKEND: Numeric columns determined: {num_cols}")
        
        # Aggregate
        print(f"🟢 BACKEND: Grouping by column '{req.by}'")
        grouped = df.groupby(req.by, dropna=False)
        preview = []
        for value, sub in grouped:
            means = {c: float(sub[c].mean()) for c in num_cols if c in sub.columns}
            preview.append({"value": value, "count": int(len(sub)), "means": means})
            print(f"🟢 BACKEND: Group '{value}': {len(sub)} items, means: {means}")
        
        print(f"🟢 BACKEND: Returning {len(preview)} groups")
        return {"groups": preview}
        
    except Exception as e:
        import traceback
        print(f"🔴 BACKEND ERROR in df_groupby_preview:")
        print(f"🔴 Exception type: {type(e).__name__}")
        print(f"🔴 Exception message: {str(e)}")
        print(f"🔴 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/df/groupby/rows")
def df_groupby_rows(req: DFGroupRowsRequest) -> Dict[str, Any]:
    df = _df_from_rows(req.rows)
    if req.by not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column not found: {req.by}")
    sub = df[df[req.by] == req.value]
    start = max((req.page - 1), 0) * max(req.page_size, 1)
    end = start + max(req.page_size, 1)
    return {"total": int(len(sub)), "rows": sub.iloc[start:end].to_dict(orient="records")}


@app.post("/df/custom")
def df_custom(req: DFCustomRequest) -> Dict[str, Any]:
    df = _df_from_rows(req.rows)
    code = (req.code or "").strip()
    if not code:
        return {"rows": req.rows}
    # Whitelist execution environment
    local_env = {"pd": pd, "df": df}
    try:
        result = eval(code, {"__builtins__": {}}, local_env)
        if isinstance(result, pd.DataFrame):
            return {"rows": result.to_dict(orient="records")}
        else:
            return {"error": "Expression must return a pandas DataFrame."}
    except Exception as e:
        return {"error": str(e)}


@app.post("/auto-detect-columns")
def auto_detect_columns(req: AutoDetectRequest) -> Dict[str, Any]:
    """Auto-detect likely column mappings from a sample of data."""
    try:
        from stringsight.core.flexible_data_loader import auto_detect_columns
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(req.rows)
        
        # Run auto-detection
        suggestions = auto_detect_columns(df)
        
        return {
            "success": True,
            "suggestions": suggestions
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestions": {
                'prompt_col': '',
                'response_cols': [],
                'model_cols': [],
                'score_cols': [],
                'method': 'single_model'
            }
        }


@app.post("/validate-flexible-mapping")
def validate_flexible_mapping(req: FlexibleDataRequest) -> Dict[str, Any]:
    """Validate a flexible column mapping against the data."""
    try:
        from stringsight.core.flexible_data_loader import validate_data_format
        
        # Convert to DataFrame for validation
        df = pd.DataFrame(req.rows)
        
        # Validate the mapping
        is_valid, errors = validate_data_format(
            df=df,
            prompt_col=req.mapping.prompt_col,
            response_cols=req.mapping.response_cols,
            model_cols=req.mapping.model_cols,
            score_cols=req.mapping.score_cols
        )
        
        return {
            "valid": is_valid,
            "errors": errors
        }
        
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Validation error: {str(e)}"]
        }


@app.post("/process-flexible-data")
def api_process_flexible_data(req: FlexibleDataRequest) -> Dict[str, Any]:
    """Process data using flexible column mapping and return operational format."""
    try:
        from stringsight.core.flexible_data_loader import process_flexible_data
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(req.rows)
        
        # Process the data
        operational_df = process_flexible_data(
            df=df,
            prompt_col=req.mapping.prompt_col,
            response_cols=req.mapping.response_cols,
            model_cols=req.mapping.model_cols,
            score_cols=req.mapping.score_cols,
            method=req.mapping.method
        )
        
        # Convert back to records
        processed_rows = operational_df.to_dict(orient="records")
        
        return {
            "success": True,
            "rows": processed_rows,
            "method": req.mapping.method,
            "columns": operational_df.columns.tolist()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "rows": [],
            "method": req.mapping.method,
            "columns": []
        }


@app.post("/flexible-conversations")
def flexible_conversations(req: FlexibleDataRequest) -> Dict[str, Any]:
    """Process flexible data and return formatted conversations."""
    try:
        # First process the data to operational format
        process_result = api_process_flexible_data(req)
        
        if not process_result["success"]:
            return process_result
        
        # Now format as conversations using the existing logic
        df = pd.DataFrame(process_result["rows"])
        method = process_result["method"]
        
        # Use existing conversation formatting
        traces = format_conversations(df, method)
        
        return {
            "success": True,
            "method": method,
            "conversations": traces
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "method": req.mapping.method,
            "conversations": []
        }


@app.get("/prompts")
def list_prompts() -> Dict[str, Any]:
    """List available extractor prompts and whether they accept task_description."""
    from stringsight import prompts as _prompts
    from inspect import getmembers
    out: List[Dict[str, Any]] = []
    for name, value in getmembers(_prompts):
        if isinstance(value, str) and "prompt" in name:
            out.append({
                "name": name,
                "label": name.replace("_", " ").replace("prompt", "").strip().title(),
                "has_task_description": "{task_description}" in value,
                "preview": value[:180]
            })
    return {"prompts": out}


@app.get("/prompt-text")
def prompt_text(name: str, task_description: Optional[str] = None) -> Dict[str, Any]:
    """Return the full text of a prompt by name. Optionally formats with task_description."""
    from stringsight import prompts as _prompts
    value = getattr(_prompts, name)
    if not isinstance(value, str):
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' is not a string")
    if "{task_description}" in value and task_description is not None:
        value = value.format(task_description=task_description)
    return {"name": name, "text": value}


@app.post("/extract/single")
def extract_single(req: ExtractSingleRequest) -> Dict[str, Any]:
    """Run extraction→parsing→validation for a single row."""
    # Build a one-row DataFrame
    df = pd.DataFrame([req.row])
    method = req.method or detect_method(list(df.columns))
    if method is None:
        raise HTTPException(status_code=422, detail="Unable to detect dataset method from columns.")

    # Validate required columns for clarity before running
    missing = validate_required_columns(df, method)
    if missing:
        raise HTTPException(status_code=422, detail={
            "error": f"Missing required columns for {method}",
            "missing": missing,
            "available": list(df.columns),
        })

    result = public_api.extract_properties_only(
        df,
        method=method,
        system_prompt=req.system_prompt,
        task_description=req.task_description,
        model_name=req.model_name or "gpt-4.1",
        temperature=req.temperature or 0.7,
        top_p=req.top_p or 0.95,
        max_tokens=req.max_tokens or 16000,
        max_workers=req.max_workers or 16,
        include_scores_in_prompt=True if req.include_scores_in_prompt is None else req.include_scores_in_prompt,
        use_wandb=req.use_wandb or False,
        output_dir=req.output_dir,
        return_debug=req.return_debug or False,
    )

    if isinstance(result, tuple):
        dataset, failures = result
    else:
        dataset, failures = result, []

    # Return parsed properties for this single row
    props = [p.to_dict() for p in dataset.properties]
    return {
        "properties": props,
        "counts": {"properties": len(props)},
        "failures": failures[:5] if req.return_debug else []
    }


@app.post("/extract/batch")
def extract_batch(req: ExtractBatchRequest) -> Dict[str, Any]:
    """Run extraction→parsing→validation for all rows and return properties table."""
    df = pd.DataFrame(req.rows)
    method = req.method or detect_method(list(df.columns))
    if method is None:
        raise HTTPException(status_code=422, detail="Unable to detect dataset method from columns.")

    # Validate required columns for clarity before running
    missing = validate_required_columns(df, method)
    if missing:
        raise HTTPException(status_code=422, detail={
            "error": f"Missing required columns for {method}",
            "missing": missing,
            "available": list(df.columns),
        })

    result = public_api.extract_properties_only(
        df,
        method=method,
        system_prompt=req.system_prompt,
        task_description=req.task_description,
        model_name=req.model_name or "gpt-4.1",
        temperature=req.temperature or 0.7,
        top_p=req.top_p or 0.95,
        max_tokens=req.max_tokens or 16000,
        max_workers=req.max_workers or 16,
        include_scores_in_prompt=True if req.include_scores_in_prompt is None else req.include_scores_in_prompt,
        use_wandb=req.use_wandb or False,
        output_dir=req.output_dir,
        return_debug=req.return_debug or False,
    )
    if isinstance(result, tuple):
        dataset, failures = result
    else:
        dataset, failures = result, []

    # Convert to properties-only table, dropping any failed parses
    props = [p.to_dict() for p in getattr(dataset, 'properties', [])]
    # Enrich with original UI row index by aligning property (question_id, model) with df index and model columns
    try:
        if '__index' in df.columns:
            idx_map: Dict[tuple[str, str], int] = {}
            if method == 'single_model' and 'model' in df.columns:
                for idx, r in df.iterrows():
                    idx_map[(str(idx), str(r.get('model', '')))] = int(r['__index'])
            elif method == 'side_by_side' and 'model_a' in df.columns and 'model_b' in df.columns:
                for idx, r in df.iterrows():
                    ui = int(r['__index'])
                    idx_map[(str(idx), str(r.get('model_a', '')))] = ui
                    idx_map[(str(idx), str(r.get('model_b', '')))] = ui
            for p in props:
                key = (str(p.get('question_id')), str(p.get('model')))
                if key in idx_map:
                    p['row_index'] = idx_map[key]
    except Exception:
        pass
    props_df = pd.DataFrame(props)
    rows = props_df.to_dict(orient="records") if not props_df.empty else []
    columns = props_df.columns.tolist() if not props_df.empty else []

    # Quick stats derived from parsing stage if available
    parse_failures = len(failures)
    empty_lists = 0
    try:
        # LLMJsonParser saves parsing_stats.json when output_dir is set; we keep it best-effort here
        parse_failures = 0
    except Exception:
        pass

    return {
        "rows": rows,
        "columns": columns,
        "counts": {"conversations": int(len(df)), "properties": int(len(rows))},
        "stats": {"parse_failures": parse_failures, "empty_lists": empty_lists},
        "failures": failures[:20] if req.return_debug else []
    }


# -----------------------------
# Async batch job API (in-memory)
# -----------------------------


@dataclass
class ExtractJob:
    id: str
    state: str = "queued"  # queued | running | done | error
    progress: float = 0.0
    count_done: int = 0
    count_total: int = 0
    error: Optional[str] = None
    properties: List[Dict[str, Any]] = field(default_factory=list)


_JOBS_LOCK = threading.Lock()
_JOBS: Dict[str, ExtractJob] = {}


class ExtractJobStartRequest(ExtractBatchRequest):
    chunk_size: Optional[int] = 250


def _run_extract_job(job: ExtractJob, req: ExtractJobStartRequest):
    try:
        with _JOBS_LOCK:
            job.state = "running"
        df = pd.DataFrame(req.rows)
        method = req.method or detect_method(list(df.columns))
        if method is None:
            raise RuntimeError("Unable to detect dataset method from columns.")
        chunk_size = max(1, int(req.chunk_size or 250))
        total = len(df)
        with _JOBS_LOCK:
            job.count_total = total
        props: List[Dict[str, Any]] = []
        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            df_chunk = df.iloc[start:end].copy()
            result = public_api.extract_properties_only(
                df_chunk,
                method=method,
                system_prompt=req.system_prompt,
                task_description=req.task_description,
                model_name=req.model_name or "gpt-4.1",
                temperature=req.temperature or 0.7,
                top_p=req.top_p or 0.95,
                max_tokens=req.max_tokens or 16000,
                max_workers=req.max_workers or 16,
                include_scores_in_prompt=True if req.include_scores_in_prompt is None else req.include_scores_in_prompt,
                use_wandb=req.use_wandb or False,
                output_dir=req.output_dir,
            )
            # result is a PropertyDataset (or (PropertyDataset, failures) in other contexts)
            if isinstance(result, tuple):
                dataset = result[0]
            else:
                dataset = result
            # Drop parsing failures by only including successfully parsed properties
            rows = [p.to_dict() for p in getattr(dataset, 'properties', [])]
            # Add original row index by aligning with df_chunk index and model columns
            try:
                if '__index' in df_chunk.columns:
                    idx_map: Dict[tuple[str, str], int] = {}
                    if method == 'single_model' and 'model' in df_chunk.columns:
                        for ridx, r in df_chunk.iterrows():
                            idx_map[(str(ridx), str(r.get('model', '')))] = int(r['__index'])
                    elif method == 'side_by_side' and 'model_a' in df_chunk.columns and 'model_b' in df_chunk.columns:
                        for ridx, r in df_chunk.iterrows():
                            ui = int(r['__index'])
                            idx_map[(str(ridx), str(r.get('model_a', '')))] = ui
                            idx_map[(str(ridx), str(r.get('model_b', '')))] = ui
                    for p in rows:
                        key = (str(p.get('question_id')), str(p.get('model')))
                        if key in idx_map:
                            p['row_index'] = idx_map[key]
            except Exception:
                pass
            props.extend(rows)
            with _JOBS_LOCK:
                job.count_done = end
                job.progress = min(1.0, job.count_done / max(1, job.count_total))
        with _JOBS_LOCK:
            job.properties = props
            job.state = "done"
            job.progress = 1.0
    except Exception as e:
        with _JOBS_LOCK:
            job.state = "error"
            job.error = str(e)


@app.post("/extract/jobs/start")
def extract_jobs_start(req: ExtractJobStartRequest) -> Dict[str, Any]:
    job_id = str(uuid.uuid4())
    job = ExtractJob(id=job_id)
    with _JOBS_LOCK:
        _JOBS[job_id] = job
    t = threading.Thread(target=_run_extract_job, args=(job, req), daemon=True)
    t.start()
    return {"job_id": job_id}


@app.get("/extract/jobs/status")
def extract_jobs_status(job_id: str) -> Dict[str, Any]:
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        return {
            "job_id": job.id,
            "state": job.state,
            "progress": job.progress,
            "count_done": job.count_done,
            "count_total": job.count_total,
            "error": job.error,
        }


@app.get("/extract/jobs/result")
def extract_jobs_result(job_id: str) -> Dict[str, Any]:
    with _JOBS_LOCK:
        job = _JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        if job.state != "done":
            raise HTTPException(status_code=409, detail="job not done")
        return {"properties": job.properties, "count": len(job.properties)}

