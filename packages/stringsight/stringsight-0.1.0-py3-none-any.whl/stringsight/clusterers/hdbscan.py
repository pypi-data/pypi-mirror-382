"""
HDBSCAN-based clustering stages.

This module migrates the clustering logic from clustering/hierarchical_clustering.py
into pipeline stages.
"""

from typing import Optional
import pandas as pd

from .base import BaseClusterer
from ..core.data_objects import PropertyDataset
from ..core.mixins import LoggingMixin, TimingMixin, WandbMixin

# Unified config
try:
    from .config import ClusterConfig
except ImportError:
    from config import ClusterConfig

try:
    from stringsight.clusterers.hierarchical_clustering import (
        hdbscan_cluster_categories,
    )
except ImportError:
    from .hierarchical_clustering import (  # type: ignore
        hdbscan_cluster_categories,
    )

class HDBSCANClusterer(BaseClusterer):
    """
    HDBSCAN clustering stage.

    This stage migrates the hdbscan_cluster_categories function from
    clustering/hierarchical_clustering.py into the pipeline architecture.
    """

    def __init__(
        self,
        min_cluster_size: int | None = None,
        embedding_model: str = "text-embedding-3-small",
        hierarchical: bool = False,
        assign_outliers: bool = False,
        include_embeddings: bool = True,
        use_wandb: bool = False,
        wandb_project: Optional[str] = None,
        max_coarse_clusters: int = 25,
        output_dir: Optional[str] = None,
        # Additional explicit configuration parameters
        min_samples: Optional[int] = None,
        cluster_selection_epsilon: float = 0.0,
        disable_dim_reduction: bool = False,
        dim_reduction_method: str = "adaptive",
        umap_n_components: int = 100,
        umap_n_neighbors: int = 30,
        umap_min_dist: float = 0.1,
        umap_metric: str = "cosine",
        context: Optional[str] = None,
        groupby_column: Optional[str] = None,
        precomputed_embeddings: Optional[object] = None,
        cache_embeddings: bool = True,
        input_model_name: Optional[str] = None,
        summary_model: str = "gpt-4.1",
        cluster_assignment_model: str = "gpt-4.1-mini",
        verbose: bool = True,
        **kwargs,
    ):
        """Initialize the HDBSCAN clusterer with explicit, overridable parameters."""
        super().__init__(
            output_dir=output_dir,
            include_embeddings=include_embeddings,
            use_wandb=use_wandb,
            wandb_project=wandb_project,
            hierarchical=hierarchical,
            **kwargs,
        )

        # Build a unified ClusterConfig (no hardcoded values)
        self.config = ClusterConfig(
            # core
            min_cluster_size=min_cluster_size,
            verbose=verbose,
            include_embeddings=include_embeddings,
            context=context,
            precomputed_embeddings=precomputed_embeddings,
            disable_dim_reduction=disable_dim_reduction,
            assign_outliers=assign_outliers,
            hierarchical=hierarchical,
            max_coarse_clusters=max_coarse_clusters,
            input_model_name=input_model_name,
            min_samples=min_samples,
            cluster_selection_epsilon=cluster_selection_epsilon,
            cache_embeddings=cache_embeddings,
            # models
            embedding_model=embedding_model,
            summary_model=summary_model,
            cluster_assignment_model=cluster_assignment_model,
            # dim reduction
            dim_reduction_method=dim_reduction_method,
            umap_n_components=umap_n_components,
            umap_n_neighbors=umap_n_neighbors,
            umap_min_dist=umap_min_dist,
            umap_metric=umap_metric,
            # groupby
            groupby_column=groupby_column,
            # wandb
            use_wandb=use_wandb,
            wandb_project=wandb_project,
        )


    def cluster(self, data: PropertyDataset, column_name: str) -> pd.DataFrame:
        """Cluster the dataset.

        If ``self.config.groupby_column`` is provided and present in the data, the
        input DataFrame is first partitioned by that column and each partition is
        clustered independently (stratified clustering). Results are then
        concatenated back together. Otherwise, the entire dataset is clustered
        at once.
        """

        df = data.to_dataframe(type="properties")
        
        print(f"🔍 DEBUG: DataFrame shape after to_dataframe: {df.shape}")
        print(f"🔍 DEBUG: DataFrame columns: {list(df.columns)}")
        print(f"🔍 DEBUG: DataFrame head:")
        print(df.head())
        
        if column_name in df.columns:
            print(f"🔍 DEBUG: {column_name} unique values: {df[column_name].nunique()}")
            print(f"🔍 DEBUG: {column_name} value counts:")
            print(df[column_name].value_counts())
            print(f"🔍 DEBUG: Sample {column_name} values: {df[column_name].head().tolist()}")
        else:
            print(f"❌ ERROR: Column '{column_name}' not found in DataFrame!")

        group_col = getattr(self.config, "groupby_column", None)

        if group_col is not None and group_col in df.columns:
            clustered_parts = []
            for group, group_df in df.groupby(group_col):
                print("--------------------------------")
                print(f"Clustering group {group}")
                print("--------------------------------")
                part = hdbscan_cluster_categories(
                    group_df,
                    column_name=column_name,
                    config=self.config,
                )
                # Add meta column with group information as a dictionary
                part["meta"] = [{"group": group}] * len(part)
                clustered_parts.append(part)
            clustered_df = pd.concat(clustered_parts, ignore_index=True)
        else:
            clustered_df = hdbscan_cluster_categories(
                df,
                column_name=column_name,
                config=self.config,
            )

        return clustered_df

    def postprocess_clustered_df(self, df: pd.DataFrame, column_name: str, prettify_labels: bool = False) -> pd.DataFrame:
        """Standard post-processing plus stratified ID re-assignment when needed."""

        fine_label_col = f"{column_name}_fine_cluster_label"
        fine_id_col = f"{column_name}_fine_cluster_id"

        df = super().postprocess_clustered_df(df, fine_label_col, prettify_labels)

        # 1️⃣  Move tiny clusters to Outliers
        label_counts = df[fine_label_col].value_counts()
        min_size_threshold = int((getattr(self.config, "min_cluster_size", 1) or 1))
        too_small_labels = label_counts[label_counts < min_size_threshold].index
        for label in too_small_labels:
            mask = df[fine_label_col] == label
            cid = df.loc[mask, fine_id_col].iloc[0] if not df.loc[mask].empty else None
            self.log(
                f"Assigning cluster {cid} (label '{label}') to Outliers because it has {label_counts[label]} items"
            )
            
            # Check if we're using groupby and assign group-specific outlier labels
            group_col = getattr(self.config, "groupby_column", None)
            if group_col is not None and group_col in df.columns:
                # Assign group-specific outlier labels
                for group_value in df.loc[mask, group_col].unique():
                    group_mask = mask & (df[group_col] == group_value)
                    outlier_label = f"Outliers - {group_value}"
                    df.loc[group_mask, fine_label_col] = outlier_label
                    df.loc[group_mask, fine_id_col] = -1
            else:
                # Standard outlier assignment
                df.loc[mask, fine_label_col] = "Outliers"
                df.loc[mask, fine_id_col] = -1

        # 2️⃣  For stratified mode: ensure cluster IDs are unique across partitions
        group_col = getattr(self.config, "groupby_column", None)
        if group_col is not None and group_col in df.columns:
            # Handle group-specific outlier labels
            outlier_mask = df[fine_label_col].str.startswith("Outliers - ") if df[fine_label_col].dtype == 'object' else df[fine_label_col] == "Outliers"
            non_outlier_mask = ~outlier_mask
            
            unique_pairs = (
                df.loc[non_outlier_mask, [group_col, fine_label_col]]
                .drop_duplicates()
                .reset_index(drop=True)
            )
            pair_to_new_id = {
                (row[group_col], row[fine_label_col]): idx for idx, row in unique_pairs.iterrows()
            }
            for (gval, lbl), new_id in pair_to_new_id.items():
                pair_mask = (df[group_col] == gval) & (df[fine_label_col] == lbl) & non_outlier_mask
                df.loc[pair_mask, fine_id_col] = new_id

            # Handle group-specific outliers: assign unique IDs to each outlier group
            if outlier_mask.any():
                # Get unique outlier labels
                unique_outlier_labels = df.loc[outlier_mask, fine_label_col].unique()
                
                # Assign unique IDs to each outlier group, starting from a high negative number
                # to avoid conflicts with regular cluster IDs
                outlier_id_start = -1000
                for i, outlier_label in enumerate(unique_outlier_labels):
                    outlier_label_mask = df[fine_label_col] == outlier_label
                    unique_outlier_id = outlier_id_start - i
                    df.loc[outlier_label_mask, fine_id_col] = unique_outlier_id

        return df

    # ------------------------------------------------------------------
    # 🏷️  Cluster construction helper with group metadata
    # ------------------------------------------------------------------
    def _build_clusters_from_df(self, df: pd.DataFrame, column_name: str):
        """Build clusters and, in stratified mode, add group info to metadata."""

        clusters = super()._build_clusters_from_df(df, column_name)

        group_col = getattr(self.config, "groupby_column", None)
        if group_col is not None and group_col in df.columns:
            fine_id_col = f"{column_name}_fine_cluster_id"
            id_to_group = (
                df.loc[df[fine_id_col].notna(), [fine_id_col, group_col]]
                .dropna()
                .groupby(fine_id_col)[group_col]
                .agg(lambda s: s.iloc[0])
                .to_dict()
            )
            for c in clusters:
                cid = getattr(c, "id", None)
                if cid in id_to_group:
                    c.meta = dict(c.meta or {})
                    c.meta["group"] = id_to_group[cid]

        return clusters


class LLMOnlyClusterer(HDBSCANClusterer):
    """
    HDBSCAN clustering stage.

    This stage migrates the hdbscan_cluster_categories function from
    clustering/hierarchical_clustering.py into the pipeline architecture.
    """

    def run(self, data: PropertyDataset, column_name: str = "property_description") -> PropertyDataset:
        """Cluster properties using HDBSCAN (delegates to base)."""
        return super().run(data, column_name)