from typing import Dict, Optional

from app.schemas.spectral import SpectralResult, SpectralResultCreate


_spectral_results: Dict[str, SpectralResult] = {}


def set_spectral_result(
    incident_id: str,
    data: SpectralResultCreate,
) -> SpectralResult:

    result = SpectralResult(
        incident_id=incident_id,
        **data.model_dump(),
    )

    _spectral_results[incident_id] = result

    return result


def get_spectral_result(
    incident_id: str,
) -> Optional[SpectralResult]:

    return _spectral_results.get(incident_id)