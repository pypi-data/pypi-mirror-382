"""
FastAPI endpoints for metrics data.

This module provides REST API endpoints for the React frontend to access
metrics data in a type-safe, performant way.

Endpoints:
- GET /metrics/summary - Get summary statistics about available metrics
- GET /metrics/model-cluster - Get model-cluster data for main metrics view
- GET /metrics/benchmark - Get per-model benchmark data 
- GET /metrics/quality-metrics - Get list of available quality metrics
- POST /metrics/compute - Trigger metrics computation for a dataset
"""

from fastapi import APIRouter, HTTPException, Query, Path as FastAPIPath
from typing import List, Optional, Dict, Any
from pathlib import Path
import json

from ..metrics.frontend_adapters import (
    MetricsDataAdapter,
    ModelClusterPayload, 
    ModelBenchmarkPayload,
    create_adapter
)

# Create router for metrics endpoints
router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary/{results_dir}")
async def get_metrics_summary(
    results_dir: str = FastAPIPath(..., description="Results directory name")
) -> Dict[str, Any]:
    """
    Get summary statistics about available metrics data.
    
    Returns overview information like number of models, clusters, battles,
    quality metrics, and data source information.
    """
    try:
        # Construct full path (assumes results are in ./results/ directory)
        full_path = Path("results") / results_dir
        adapter = create_adapter(full_path)
        return adapter.get_summary_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading metrics summary: {str(e)}")


@router.get("/model-cluster/{results_dir}")
async def get_model_cluster_metrics(
    results_dir: str = FastAPIPath(..., description="Results directory name"),
    models: Optional[List[str]] = Query(None, description="Filter by specific models"),
    quality_metric: Optional[str] = Query(None, description="Filter by quality metric"),
    significant_only: Optional[bool] = Query(False, description="Show only significant differences")
) -> ModelClusterPayload:
    """
    Get model-cluster metrics data for the main metrics view.
    
    This endpoint provides the core data for the React metrics tab,
    including frequency and quality metrics per model-cluster combination.
    """
    try:
        full_path = Path("results") / results_dir
        adapter = create_adapter(full_path)
        payload = adapter.get_frontend_payload()
        
        # Apply filters if specified
        if models or quality_metric or significant_only:
            filtered_data = _apply_filters(
                payload.data, 
                models=models,
                quality_metric=quality_metric, 
                significant_only=significant_only
            )
            
            # Update payload with filtered data
            payload.data = filtered_data
            if models:
                payload.models = [m for m in payload.models if m in models]
        
        return payload
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model-cluster metrics: {str(e)}")


@router.get("/benchmark/{results_dir}")
async def get_benchmark_metrics(
    results_dir: str = FastAPIPath(..., description="Results directory name"),
    models: Optional[List[str]] = Query(None, description="Filter by specific models")
) -> ModelBenchmarkPayload:
    """
    Get per-model benchmark metrics.
    
    Returns aggregated quality scores for each model across all clusters,
    useful for model comparison charts.
    """
    try:
        full_path = Path("results") / results_dir
        adapter = create_adapter(full_path)
        payload = adapter.get_benchmark_payload()
        
        # Apply model filter if specified
        if models:
            filtered_data = [row for row in payload.data if row.get('model') in models]
            payload.data = filtered_data
            payload.models = [m for m in payload.models if m in models]
        
        return payload
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading benchmark metrics: {str(e)}")


@router.get("/quality-metrics/{results_dir}")
async def get_available_quality_metrics(
    results_dir: str = FastAPIPath(..., description="Results directory name")
) -> Dict[str, List[str]]:
    """Get list of available quality metrics for the dataset."""
    try:
        full_path = Path("results") / results_dir
        adapter = create_adapter(full_path)
        metrics = adapter.get_available_quality_metrics()
        return {"quality_metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading quality metrics: {str(e)}")


@router.get("/legacy/{results_dir}")
async def get_legacy_format(
    results_dir: str = FastAPIPath(..., description="Results directory name")
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Get metrics in legacy nested JSON format.
    
    This endpoint provides backwards compatibility for existing dashboard code
    that expects the nested structure. New code should use the other endpoints.
    """
    try:
        full_path = Path("results") / results_dir
        adapter = create_adapter(full_path)
        return adapter.get_legacy_format()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading legacy format: {str(e)}")


@router.post("/compute/{results_dir}")
async def compute_metrics(
    results_dir: str = FastAPIPath(..., description="Results directory name"),
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Trigger metrics computation for a dataset.
    
    This endpoint can be used to recompute metrics when the underlying
    data has changed. Returns a status message.
    
    Note: This is a placeholder for future implementation.
    The actual computation would need to be integrated with the 
    existing FunctionalMetrics pipeline.
    """
    # TODO: Implement actual metrics computation
    # This would need to:
    # 1. Load the raw clustered data from results_dir
    # 2. Run FunctionalMetrics.compute() 
    # 3. Save the results
    # 4. Return status
    
    return {
        "status": "not_implemented",
        "message": f"Metrics computation for {results_dir} is not yet implemented"
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for metrics API."""
    return {"status": "healthy", "service": "metrics_api"}


def _apply_filters(
    data: List[Dict[str, Any]], 
    models: Optional[List[str]] = None,
    quality_metric: Optional[str] = None,
    significant_only: bool = False
) -> List[Dict[str, Any]]:
    """Apply filters to metrics data."""
    filtered_data = data
    
    # Filter by models
    if models:
        filtered_data = [row for row in filtered_data if row.get('model') in models]
    
    # Filter by significance
    if significant_only:
        filtered_data = [
            row for row in filtered_data 
            if (row.get('proportion_delta_significant', False) or 
                any(row.get(f'quality_delta_{quality_metric}_significant', False) 
                    for metric in [quality_metric] if metric))
        ]
    
    return filtered_data


def get_metrics_router() -> APIRouter:
    """Get the configured metrics router."""
    return router