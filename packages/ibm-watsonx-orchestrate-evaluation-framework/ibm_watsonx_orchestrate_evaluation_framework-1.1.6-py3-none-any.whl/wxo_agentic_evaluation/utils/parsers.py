from typing import Any, List, Mapping, Optional

from wxo_agentic_evaluation.metrics import (
    Annotation,
    FailedSemanticTestCases,
    FailedStaticTestCases,
)


class ReferencelessEvalParser:
    @staticmethod
    def static_parser(
        static_metrics: Mapping[str, Mapping[str, Any]],
    ) -> List[FailedStaticTestCases]:
        """
        static.metrics
        """

        failed_test_cases = []

        for metric, metric_data in static_metrics.items():
            if not metric_data.get("valid", False):
                fail = FailedStaticTestCases(
                    metric_name=metric,
                    description=metric_data.get("description"),
                    explanation=metric_data.get("explanation"),
                )

                failed_test_cases.append(fail)

        return failed_test_cases

    @staticmethod
    def parse_annotations(
        actionable_reccomendations, filters: List[str]
    ) -> Optional[List[Annotation]]:
        annotations = [
            Annotation(
                parameter_name=recc.get("parameter_name"),
                recommendation=recc.get("recommendation"),
                details=recc.get("details"),
                quote=recc.get("quote"),
            )
            for recc in actionable_reccomendations
            if recc.get("recommendation") in filters
        ]

        annotations = annotations if annotations else None

        return annotations

    @staticmethod
    def semantic_parser(
        metric_name, data, annotation_filters: Optional[List[str]]
    ):
        semantic_metric = FailedSemanticTestCases(
            metric_name=metric_name,
            evidence=data.get("evidence"),
            explanation=data.get("explanation"),
            output=data.get("output"),
            confidence=data.get("confidence"),
        )

        if annotation_filters and (
            annotations := ReferencelessEvalParser.parse_annotations(
                data.get("actionable_recommendations"), annotation_filters
            )
        ):
            semantic_metric.annotations = annotations

        return semantic_metric
