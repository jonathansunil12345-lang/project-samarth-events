"""
Analysis Stage - Performs data analysis based on intent

This is the third stage in the event-driven pipeline.
Input: Parsed query + Loaded datasets
Output: Analysis results
"""
from typing import Any, Dict
import logging
import pandas as pd
import numpy as np
from .base_stage import PipelineStage

logger = logging.getLogger(__name__)


class AnalysisStage(PipelineStage):
    """
    Analyzes data based on query intent.

    Event Flow:
    - Listens to: 'data.loaded'
    - Publishes to: 'analysis.complete'

    TODO: Implement the 4 analysis methods below
    """

    def input_topic(self) -> str:
        return "data.loaded"

    def output_topic(self) -> str:
        return "analysis.complete"

    def process(self, data: Any, metadata: dict) -> Any:
        """
        Route to appropriate analysis method based on intent.

        Args:
            data: Dictionary with 'intent', 'params', and 'datasets'
            metadata: Event metadata

        Returns:
            Analysis results
        """
        intent = data["intent"]
        params = data["params"]
        datasets = data["datasets"]

        logger.info(f"Analyzing data for intent: {intent}")

        # Route to appropriate analysis method
        if intent == "compare_rainfall_and_crops":
            results = self._analyze_compare_rainfall_crops(params, datasets)
        elif intent == "district_extremes":
            results = self._analyze_district_extremes(params, datasets)
        elif intent == "production_trend_with_climate":
            results = self._analyze_production_trend(params, datasets)
        elif intent == "policy_arguments":
            results = self._analyze_policy_arguments(params, datasets)
        else:
            raise ValueError(f"Unknown intent: {intent}")

        return {
            **data,  # Pass along previous data
            "results": results
        }

    def _analyze_compare_rainfall_crops(self, params: Dict, datasets: Dict[str, pd.DataFrame]) -> Dict:
        """Compare rainfall between states and list top crops."""
        state_a = params["state_a"]
        state_b = params["state_b"]
        last_n_years = params.get("years", 5)
        crop_filter = params.get("crop_filter")
        top_m = params.get("top_m", 3)

        rainfall_df = datasets["rainfall"]
        agri_df = datasets["agriculture"]

        # Filter rainfall data
        rainfall = rainfall_df[rainfall_df["state"].isin([state_a, state_b])]
        available_years = sorted(rainfall["year"].unique(), reverse=True)
        n_years = last_n_years if last_n_years else min(len(available_years), 5)
        years_sel = sorted(available_years[:n_years])

        rainfall_subset = rainfall[rainfall["year"].isin(years_sel)]
        rainfall_stats = (
            rainfall_subset.groupby(["state", "year"])["annual_rainfall_mm"]
            .mean()
            .reset_index()
            .sort_values(["year", "state"])
        )

        # Calculate averages
        avg_a = rainfall_subset[rainfall_subset["state"] == state_a]["annual_rainfall_mm"].mean()
        avg_b = rainfall_subset[rainfall_subset["state"] == state_b]["annual_rainfall_mm"].mean()

        # Filter agriculture data
        agri_subset = agri_df[agri_df["state"].isin([state_a, state_b])]
        agri_subset = agri_subset[agri_subset["year"].isin(years_sel)]

        if crop_filter:
            agri_subset = agri_subset[agri_subset["crop"].str.contains(crop_filter, case=False, na=False)]

        # Rank crops
        crop_rankings = (
            agri_subset.groupby(["state", "crop"])["production_tonnes"]
            .sum()
            .reset_index()
        )
        crop_rankings["rank"] = crop_rankings.groupby("state")["production_tonnes"].rank(
            method="first", ascending=False
        )
        crop_rankings = crop_rankings[crop_rankings["rank"] <= top_m]
        crop_rankings = crop_rankings.sort_values(["state", "rank"])

        return {
            "state_a": state_a,
            "state_b": state_b,
            "years": years_sel,
            "rainfall_stats": rainfall_stats,
            "avg_rainfall_a": avg_a,
            "avg_rainfall_b": avg_b,
            "crop_rankings": crop_rankings,
            "crop_filter": crop_filter,
            "top_m": top_m
        }

    def _analyze_district_extremes(self, params: Dict, datasets: Dict[str, pd.DataFrame]) -> Dict:
        """Find districts with highest/lowest production."""
        state_a = params["state_a"]
        state_b = params["state_b"]
        crop = params["crop"]
        year = params.get("year")

        agri_df = datasets["agriculture"]

        # Filter by crop
        subset = agri_df[agri_df["crop"] == crop]

        if year:
            subset = subset[subset["year"] == year]

        if subset.empty:
            raise ValueError("No production data found for the requested crop/year.")

        latest_year = subset["year"].max()
        if not year:
            year = latest_year

        subset = subset[subset["year"] == year]

        # Get data for each state
        state_a_rows = subset[subset["state"] == state_a]
        state_b_rows = subset[subset["state"] == state_b]

        result = {
            "state_a": state_a,
            "state_b": state_b,
            "crop": crop,
            "year": year
        }

        # Process state A (max)
        if state_a_rows.empty:
            result["state_a_max"] = None
        else:
            max_row = state_a_rows.loc[state_a_rows["production_tonnes"].idxmax()]
            result["state_a_max"] = {
                "district": max_row["district"],
                "production": float(max_row["production_tonnes"])
            }

        # Process state B (min)
        if state_b_rows.empty:
            result["state_b_min"] = None
        else:
            min_row = state_b_rows.loc[state_b_rows["production_tonnes"].idxmin()]
            result["state_b_min"] = {
                "district": min_row["district"],
                "production": float(min_row["production_tonnes"])
            }

        return result

    def _analyze_production_trend(self, params: Dict, datasets: Dict[str, pd.DataFrame]) -> Dict:
        """Analyze production trend and correlate with climate."""
        state = params["state"]
        crop = params["crop"]
        n_years = params.get("years", 10)

        agri_df = datasets["agriculture"]
        rainfall_df = datasets["rainfall"]

        # Filter data
        agri = agri_df[(agri_df["state"] == state) & (agri_df["crop"] == crop)]
        if agri.empty:
            raise ValueError("No production data found for the selected region/crop.")

        rainfall = rainfall_df[rainfall_df["state"] == state]
        if rainfall.empty:
            raise ValueError("No rainfall data found for the selected region.")

        # Select years
        years_available = sorted(agri["year"].unique(), reverse=True)
        years_to_use = n_years if n_years else min(len(years_available), 10)
        years_sel = sorted(years_available[:years_to_use])

        agri = agri[agri["year"].isin(years_sel)]
        rainfall = rainfall[rainfall["year"].isin(years_sel)]

        # Aggregate production
        production_series = (
            agri.groupby("year")["production_tonnes"]
            .sum()
            .reset_index()
            .sort_values("year")
        )

        rainfall_series = rainfall.sort_values("year")[["year", "annual_rainfall_mm"]]

        # Merge and calculate correlation
        merged = pd.merge(production_series, rainfall_series, on="year", how="inner")
        corr = merged["production_tonnes"].corr(merged["annual_rainfall_mm"])

        # Calculate growth trend
        trend_pct = self._calc_growth(production_series)

        return {
            "state": state,
            "crop": crop,
            "years": years_sel,
            "merged_data": merged,
            "correlation": corr,
            "trend_pct": trend_pct
        }

    @staticmethod
    def _calc_growth(series: pd.DataFrame) -> float:
        """Calculate percentage growth from first to last value."""
        series = series.sort_values(series.columns[0])
        values = series.iloc[:, -1].astype(float)
        if len(values) < 2 or values.iloc[0] == 0:
            return 0.0
        return ((values.iloc[-1] - values.iloc[0]) / values.iloc[0]) * 100.0

    def _analyze_policy_arguments(self, params: Dict, datasets: Dict[str, pd.DataFrame]) -> Dict:
        """Generate policy arguments for crop shift."""
        state = params["state"]
        current_crop = params["crop_a"]
        proposed_crop = params["crop_b"]
        n_years = params.get("years", 5)

        agri_df = datasets["agriculture"]
        rainfall_df = datasets["rainfall"]

        # Filter agriculture data
        relevant = agri_df[agri_df["state"] == state]
        years_available = sorted(relevant["year"].unique(), reverse=True)
        years_to_use = n_years if n_years else min(len(years_available), 5)
        years_sel = sorted(years_available[:years_to_use])

        subset = relevant[relevant["year"].isin(years_sel)]

        # Aggregate data for both crops
        agg = (
            subset[subset["crop"].isin([current_crop, proposed_crop])]
            .groupby(["crop", "year"])["production_tonnes"]
            .sum()
            .reset_index()
        )

        # Get rainfall data
        rainfall = (
            rainfall_df[(rainfall_df["state"] == state) & (rainfall_df["year"].isin(years_sel))]
            .sort_values("year")
        )

        crop_data = {}
        for crop in [current_crop, proposed_crop]:
            crop_series = agg[agg["crop"] == crop].sort_values("year")
            if not crop_series.empty:
                growth = self._calc_growth(crop_series)
                avg_prod = crop_series["production_tonnes"].mean()
                crop_data[crop] = {
                    "series": crop_series,
                    "growth": growth,
                    "avg_production": avg_prod
                }
            else:
                crop_data[crop] = None

        # Rainfall stats
        rainfall_stats = None
        if not rainfall.empty:
            avg_rain = rainfall["annual_rainfall_mm"].mean()
            rain_trend = self._calc_growth(rainfall)
            rainfall_stats = {
                "data": rainfall,
                "avg_rainfall": avg_rain,
                "trend": rain_trend
            }

        return {
            "state": state,
            "current_crop": current_crop,
            "proposed_crop": proposed_crop,
            "years": years_sel,
            "crop_data": crop_data,
            "rainfall_stats": rainfall_stats
        }
