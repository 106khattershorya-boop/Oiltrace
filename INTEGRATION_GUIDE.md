# Backend Integration Guide — SIH26143

This document tells the Database, ML, and Frontend teammates exactly how to
integrate with the backend without needing to read all the code.

---

## For Database / PostGIS Teammate

The backend currently uses in-memory Python dicts as placeholder storage
(`app/storage/*.py`). Each store file has a small, isolated interface:

| Store file | Functions to reimplement with PostGIS |
|---|---|
| `app/storage/memory_store.py` | `create_incident`, `list_incidents`, `get_incident` |
| `app/storage/vessel_store.py` | `add_report`, `list_reports`, `list_reports_by_mmsi` |
| `app/storage/spectral_store.py` | `set_spectral_result`, `get_spectral_result` |
| `app/storage/cargo_store.py` | `set_cargo_score`, `get_cargo_score`, `get_all_scores_for_incident` |

**Your job:** replace the internals of these functions with real SQL/PostGIS
queries against the project database schema.

The function names, inputs, and return types (Pydantic models) should stay the
same so that the routers and services continue working without major changes.

### Table ↔ Schema Field Mapping

#### 1. Spill Incidents

Database table:

`spill_incidents`

Backend schema:

`app/schemas/spill.py`

Relevant mapping:

- `incident_id` → `incident_id`
- `latitude` → `latitude`
- `longitude` → `longitude`
- `detection_time` → `detection_time`
- `estimated_area` → `estimated_area_km2`
- `detection_confidence` → `detection_confidence`
- `satellite_source` → `satellite_source`

The database also contains `probable_oil_category`, which can be populated
from the spectral-analysis result.

#### 2. Vessels and AIS

Database tables:

- `vessels`
- `ais_positions`

Backend schema:

`app/schemas/vessel.py`

The API currently accepts a flat AIS report containing:

- `mmsi`
- `vessel_name`
- `vessel_type`
- `latitude`
- `longitude`
- `speed_knots`
- `course_degrees`
- `timestamp`

When implementing `vessel_store.py`:

1. Look up or create the vessel using `mmsi`.
2. Obtain the corresponding `vessel_id`.
3. Insert the AIS position into `ais_positions`.
4. Link the position to the vessel using `vessel_id`.

The external API field names do not need to change.

#### 3. Spill-Vessel Matching

Database table:

`spill_vessel_matches`

Backend schema:

`app/schemas/correlation.py`

The current MVP exposes:

`spatial_temporal_score`

which combines spatial and temporal correlation into one score.

The database schema also supports:

- `spatial_score`
- `temporal_score`
- `trajectory_score`

These should be handled separately when the correlation service is upgraded.

Do not change the database implementation until the exact score mapping is
agreed with the backend.

#### 4. Behaviour Analysis

Database table:

`behaviour_analysis`

Backend schema:

`app/schemas/behaviour.py`

Current fields:

- `speed_anomaly`
- `stop_anomaly`
- `course_deviation`
- `ais_gap`
- `loitering`
- `behaviour_score`

#### 5. Spectral Analysis

Database table:

`spectral_analysis`

Backend schema:

`app/schemas/spectral.py`

Current fields:

- `spectral_features`
- `probable_oil_category`
- `spectral_score`

#### 6. Investigation Scores

Database table:

`investigation_scores`

Backend schema:

`app/schemas/priority.py`

Current fields:

- `spatial_temporal_score`
- `behaviour_score`
- `spectral_score`
- `cargo_score`
- `final_priority_score`
- `priority_level`

### Important

The current backend uses in-memory storage only for MVP testing.

Do not change the API routes unnecessarily while replacing the storage layer.
The goal is for PostgreSQL/PostGIS to replace the temporary storage while
keeping the existing API contracts stable.

---

## For the ML Teammate

The ML teammate does not need to know the backend's internal storage
implementation.

Once the ML models produce their results, they can submit them through the
following endpoints.

### 1. Spectral / Oil Category Result

**Endpoint:**

`POST /incidents/{incident_id}/spectral-result`

**Body:**

```json
{
  "spectral_features": "free text or JSON-encoded summary of extracted features",
  "probable_oil_category": "heavy_petroleum",
  "spectral_score": 0.82
}