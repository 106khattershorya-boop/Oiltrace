from typing import Dict, Optional

from app.schemas.ml_analysis import MLAnalysisResult


_ml_results: Dict[str, MLAnalysisResult] = {}


def save_result(result: MLAnalysisResult) -> MLAnalysisResult:
    _ml_results[result.incident_id] = result
    return result


def get_result(incident_id: str) -> Optional[MLAnalysisResult]:
    return _ml_results.get(incident_id)