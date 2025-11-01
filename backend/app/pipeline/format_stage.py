"""
Format Stage - Formats analysis results into final response

This is the final stage in the event-driven pipeline.
Input: Analysis results
Output: Formatted response with answer, tables, and citations
"""
from typing import Any, Dict, List
import logging
import numpy as np
from .base_stage import PipelineStage

logger = logging.getLogger(__name__)


class FormatStage(PipelineStage):
    """
    Formats analysis results into user-friendly response.

    Event Flow:
    - Listens to: 'analysis.complete'
    - Publishes to: 'response.ready'

    TODO: Implement the formatting methods
    """

    def input_topic(self) -> str:
        return "analysis.complete"

    def output_topic(self) -> str:
        return "response.ready"

    def process(self, data: Any, metadata: dict) -> Any:
        """
        Format the analysis results.

        Args:
            data: Dictionary with 'intent', 'params', 'results'
            metadata: Event metadata

        Returns:
            Formatted response dictionary
        """
        intent = data["intent"]
        results = data["results"]

        logger.info(f"Formatting results for intent: {intent}")

        # Route to appropriate formatter
        if intent == "compare_rainfall_and_crops":
            formatted = self._format_compare_rainfall_crops(results)
        elif intent == "district_extremes":
            formatted = self._format_district_extremes(results)
        elif intent == "production_trend_with_climate":
            formatted = self._format_production_trend(results)
        elif intent == "policy_arguments":
            formatted = self._format_policy_arguments(results)
        else:
            raise ValueError(f"Unknown intent: {intent}")

        return {
            "answer": formatted["answer"],
            "tables": formatted["tables"],
            "citations": formatted["citations"],
            "debug": {
                "intent": intent,
                "params": data["params"]
            }
        }

    def _format_compare_rainfall_crops(self, results: Dict) -> Dict:
        """Format rainfall comparison results."""
        state_a = results["state_a"]
        state_b = results["state_b"]
        years = results["years"]
        rainfall_stats = results["rainfall_stats"]
        avg_a = results["avg_rainfall_a"]
        avg_b = results["avg_rainfall_b"]
        crop_rankings = results["crop_rankings"]
        crop_filter = results["crop_filter"]
        top_m = results["top_m"]

        # Create rainfall table
        pivot = rainfall_stats.pivot(index="year", columns="state", values="annual_rainfall_mm")
        rainfall_rows = []
        for year in years:
            row = [int(year)]
            for state in [state_a, state_b]:
                value = pivot.get(state, {}).get(year, None)
                row.append(float(round(float(value), 1)) if value is not None else None)
            rainfall_rows.append(row)

        rainfall_table = {
            "title": "Average annual rainfall (mm)",
            "headers": ["Year", state_a, state_b],
            "rows": rainfall_rows
        }

        # Create crop table
        crop_rows = []
        for state in [state_a, state_b]:
            subset = crop_rankings[crop_rankings["state"] == state]
            if subset.empty:
                crop_rows.append([state, "No data", "—"])
                continue
            for _, row in subset.iterrows():
                crop_rows.append([
                    state,
                    row["crop"],
                    float(round(float(row["production_tonnes"]), 2))
                ])

        crop_table = {
            "title": f"Top {top_m} crops by production" + (f" (filter: {crop_filter})" if crop_filter else ""),
            "headers": ["State", "Crop", "Production (tonnes)"],
            "rows": crop_rows
        }

        # Generate answer
        answer = (
            f"Compared rainfall for {state_a} and {state_b} over {len(years)} year(s). "
            f"{state_a} averaged {avg_a:.1f} mm while {state_b} averaged {avg_b:.1f} mm."
        )
        if crop_filter:
            answer += f" Filtered crop category: {crop_filter}."

        # Citations
        citations = [
            {
                "dataset": "rainfall",
                "source": "https://data.gov.in/resources/rainfall-sub-division-wise-distribution",
                "resource_id": "cca5f77c-68b3-43df-bd01-beb3b69204ed"
            },
            {
                "dataset": "agriculture",
                "source": "https://data.gov.in/resources/district-wise-crop-production-statistics",
                "resource_id": "9ef84268-d588-465a-a308-a864a43d0070"
            }
        ]

        return {
            "answer": answer,
            "tables": [rainfall_table, crop_table],
            "citations": citations
        }

    def _format_district_extremes(self, results: Dict) -> Dict:
        """Format district extremes results."""
        state_a = results["state_a"]
        state_b = results["state_b"]
        crop = results["crop"]
        year = results["year"]
        state_a_max = results["state_a_max"]
        state_b_min = results["state_b_min"]

        # Create table
        rows = []
        parts = []

        # State A (max)
        if state_a_max is None:
            rows.append([state_a, "No records", "—"])
            parts.append(f"{state_a} did not report {crop} production in {year}.")
        else:
            rows.append([
                state_a,
                state_a_max["district"],
                float(round(state_a_max["production"], 2))
            ])
            parts.append(
                f"{state_a}'s peak output came from {state_a_max['district']} "
                f"with {state_a_max['production']:.1f} tonnes."
            )

        # State B (min)
        if state_b_min is None:
            rows.append([state_b, "No records", "—"])
            parts.append(f"{state_b} did not report {crop} production in {year}.")
        else:
            rows.append([
                state_b,
                state_b_min["district"],
                float(round(state_b_min["production"], 2))
            ])
            parts.append(
                f"{state_b}'s lowest output was {state_b_min['district']} "
                f"at {state_b_min['production']:.1f} tonnes."
            )

        table = {
            "title": f"District extremes for {crop} in {year}",
            "headers": ["State", "District", "Production (tonnes)"],
            "rows": rows
        }

        answer = " ".join(parts)

        citations = [{
            "dataset": "agriculture",
            "source": "https://data.gov.in/resources/district-wise-crop-production-statistics",
            "resource_id": "9ef84268-d588-465a-a308-a864a43d0070"
        }]

        return {
            "answer": answer,
            "tables": [table],
            "citations": citations
        }

    def _format_production_trend(self, results: Dict) -> Dict:
        """Format production trend results."""
        state = results["state"]
        crop = results["crop"]
        years = results["years"]
        merged_data = results["merged_data"]
        correlation = results["correlation"]
        trend_pct = results["trend_pct"]

        # Interpret correlation
        corr_text = self._interpret_correlation(correlation)

        # Create table
        table = {
            "title": f"{state} {crop} vs rainfall",
            "headers": ["Year", "Production (tonnes)", "Rainfall (mm)"],
            "rows": [
                [
                    int(row["year"]),
                    float(round(float(row["production_tonnes"]), 2)),
                    float(round(float(row["annual_rainfall_mm"]), 1))
                ]
                for _, row in merged_data.iterrows()
            ]
        }

        # Generate answer
        answer = (
            f"{state} recorded a {trend_pct:.1f}% change in {crop} production over {len(years)} year(s). "
            f"Rainfall correlation indicates {corr_text} (r={correlation:.2f})."
        )

        # Citations
        citations = [
            {
                "dataset": "agriculture",
                "source": "https://data.gov.in/resources/district-wise-crop-production-statistics",
                "resource_id": "9ef84268-d588-465a-a308-a864a43d0070"
            },
            {
                "dataset": "rainfall",
                "source": "https://data.gov.in/resources/rainfall-sub-division-wise-distribution",
                "resource_id": "cca5f77c-68b3-43df-bd01-beb3b69204ed"
            }
        ]

        return {
            "answer": answer,
            "tables": [table],
            "citations": citations
        }

    @staticmethod
    def _interpret_correlation(coefficient: float) -> str:
        """Interpret correlation coefficient."""
        if np.isnan(coefficient):
            return "insufficient data for correlation"
        abs_coeff = abs(coefficient)
        if abs_coeff >= 0.7:
            level = "strong"
        elif abs_coeff >= 0.4:
            level = "moderate"
        else:
            level = "weak"
        direction = "positive" if coefficient > 0 else "negative"
        return f"{level} {direction} association"

    def _format_policy_arguments(self, results: Dict) -> Dict:
        """Format policy arguments results."""
        state = results["state"]
        current_crop = results["current_crop"]
        proposed_crop = results["proposed_crop"]
        years = results["years"]
        crop_data = results["crop_data"]
        rainfall_stats = results["rainfall_stats"]

        insights = []
        tables = []

        # Format crop data
        for crop in [current_crop, proposed_crop]:
            if crop_data[crop] is None:
                insights.append(f"No production records for {crop} in {state}.")
                continue

            growth = crop_data[crop]["growth"]
            avg_prod = crop_data[crop]["avg_production"]
            series = crop_data[crop]["series"]

            insights.append(
                f"{crop}: avg {avg_prod:.1f} tonnes over {len(years)} year(s) with {growth:.1f}% total change."
            )

            tables.append({
                "title": f"{crop} production",
                "headers": ["Year", "Production (tonnes)"],
                "rows": [
                    [int(row["year"]), float(round(float(row["production_tonnes"]), 2))]
                    for _, row in series.iterrows()
                ]
            })

        # Add rainfall context
        if rainfall_stats:
            avg_rain = rainfall_stats["avg_rainfall"]
            trend = rainfall_stats["trend"]
            rainfall_data = rainfall_stats["data"]

            insights.append(
                f"Rainfall averaged {avg_rain:.1f} mm with {trend:.1f}% change, "
                f"affecting water availability for {proposed_crop}."
            )

            tables.append({
                "title": "Rainfall context",
                "headers": ["Year", "Rainfall (mm)"],
                "rows": [
                    [int(row["year"]), float(round(float(row["annual_rainfall_mm"]), 1))]
                    for _, row in rainfall_data.iterrows()
                ]
            })

        # Generate answer
        answer = (
            f"Supporting a shift towards {proposed_crop}: "
            + "; ".join(insights[:3])
        )

        # Citations
        citations = [
            {
                "dataset": "agriculture",
                "source": "https://data.gov.in/resources/district-wise-crop-production-statistics",
                "resource_id": "9ef84268-d588-465a-a308-a864a43d0070"
            },
            {
                "dataset": "rainfall",
                "source": "https://data.gov.in/resources/rainfall-sub-division-wise-distribution",
                "resource_id": "cca5f77c-68b3-43df-bd01-beb3b69204ed"
            }
        ]

        return {
            "answer": answer,
            "tables": tables,
            "citations": citations
        }
