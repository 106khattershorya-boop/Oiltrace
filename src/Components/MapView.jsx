import { Fragment, useEffect, useMemo, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Circle,
  CircleMarker,
  Polygon,
  Polyline,
  Popup,
  Tooltip,
  useMap,
} from "react-leaflet";

import {
  Radar,
  Radio,
  Satellite,
  ShieldAlert,
  Ship,
  Target,
  Layers3,
} from "lucide-react";

import "leaflet/dist/leaflet.css";

/* =========================================================
   OILTRACE MAP CONFIG
========================================================= */

const CENTER = [18.742, 72.913];

/* =========================================================
   DEMO VESSEL DATA
========================================================= */

const vessels = [
  {
    id: "MV-01",
    name: "MV Ocean Pioneer",
    imo: "IMO 9876543",
    type: "Oil Tanker",
    flag: "India",
    risk: "CRITICAL",
    score: 94,
    distance: "7.2 km",
    position: [18.775, 72.865],
  },

  {
    id: "MV-02",
    name: "MT Blue Horizon",
    imo: "IMO 9123456",
    type: "Chemical Tanker",
    flag: "Singapore",
    risk: "HIGH",
    score: 86,
    distance: "12.8 km",
    position: [18.695, 73.005],
  },

  {
    id: "MV-03",
    name: "MV Eastern Star",
    imo: "IMO 9345678",
    type: "Cargo Vessel",
    flag: "Panama",
    risk: "HIGH",
    score: 79,
    distance: "18.6 km",
    position: [18.835, 72.982],
  },

  {
    id: "MV-04",
    name: "MT Coastal Trader",
    imo: "IMO 9456123",
    type: "Oil Tanker",
    flag: "Liberia",
    risk: "MEDIUM",
    score: 63,
    distance: "26.4 km",
    position: [18.625, 72.805],
  },

  {
    id: "MV-05",
    name: "MV Arabian Pearl",
    imo: "IMO 9567812",
    type: "Container Ship",
    flag: "Malta",
    risk: "LOW",
    score: 38,
    distance: "34.9 km",
    position: [18.895, 72.755],
  },
];

/* =========================================================
   RISK COLOR
========================================================= */

function riskColor(risk) {
  switch (risk) {
    case "CRITICAL":
      return "#fb7185";

    case "HIGH":
      return "#fb923c";

    case "MEDIUM":
      return "#facc15";

    default:
      return "#22d3ee";
  }
}

/* =========================================================
   MAP CONTROLLER
========================================================= */

function MapController({ focusTarget }) {
  const map = useMap();

  useEffect(() => {
    if (!focusTarget) return;

    map.flyTo(focusTarget, 10, {
      duration: 1.4,
      easeLinearity: 0.25,
    });
  }, [focusTarget, map]);

  return null;
}

/* =========================================================
   DRIFT FORECAST
========================================================= */

function AnimatedDriftPath({ visible }) {
  if (!visible) return null;

  const points = [
    CENTER,
    [18.79, 72.94],
    [18.85, 72.985],
    [18.91, 73.035],
    [18.98, 73.09],
  ];

  return (
    <>
      {/* Outer glow */}

      <Polyline
        positions={points}
        pathOptions={{
          color: "#22d3ee",
          weight: 12,
          opacity: 0.08,
        }}
      />

      {/* Secondary glow */}

      <Polyline
        positions={points}
        pathOptions={{
          color: "#8b5cf6",
          weight: 6,
          opacity: 0.16,
        }}
      />

      {/* Main forecast line */}

      <Polyline
        positions={points}
        pathOptions={{
          color: "#22d3ee",
          weight: 2.5,
          opacity: 0.95,
          dashArray: "8 10",
        }}
      />

      {/* Forecast points */}

      {points.slice(1).map((point, index) => (
        <Fragment key={`forecast-${index}`}>
          <CircleMarker
            center={point}
            radius={7}
            pathOptions={{
              color: "#a78bfa",
              fillColor: "#22d3ee",
              fillOpacity: 0.25,
              weight: 1,
            }}
          />

          <CircleMarker
            center={point}
            radius={3.5}
            pathOptions={{
              color: "#ffffff",
              fillColor: "#22d3ee",
              fillOpacity: 1,
              weight: 1,
            }}
          >
            <Tooltip direction="top">
              <strong>
                +{(index + 1) * 6}h Forecast
              </strong>
            </Tooltip>
          </CircleMarker>
        </Fragment>
      ))}
    </>
  );
}

/* =========================================================
   VESSEL ROUTES
========================================================= */

function VesselRoutes({ visible }) {
  if (!visible) return null;

  const routes = [
    {
      vessel: vessels[0],
      points: [
        [18.68, 72.78],
        [18.72, 72.81],
        [18.75, 72.84],
        vessels[0].position,
      ],
    },

    {
      vessel: vessels[1],
      points: [
        [18.61, 73.11],
        [18.64, 73.07],
        [18.67, 73.04],
        vessels[1].position,
      ],
    },

    {
      vessel: vessels[2],
      points: [
        [18.94, 72.83],
        [18.91, 72.87],
        [18.88, 72.92],
        vessels[2].position,
      ],
    },

    {
      vessel: vessels[3],
      points: [
        [18.55, 72.72],
        [18.58, 72.75],
        [18.60, 72.78],
        vessels[3].position,
      ],
    },
  ];

  return (
    <>
      {routes.map((route, index) => (
        <Fragment key={`route-${index}`}>
          <Polyline
            positions={route.points}
            pathOptions={{
              color: riskColor(route.vessel.risk),
              weight: 4,
              opacity: 0.08,
            }}
          />

          <Polyline
            positions={route.points}
            pathOptions={{
              color: riskColor(route.vessel.risk),
              weight: 1.5,
              opacity: 0.55,
              dashArray: "5 8",
            }}
          />
        </Fragment>
      ))}
    </>
  );
}

/* =========================================================
   MAIN MAP COMPONENT
========================================================= */

const MapView = ({
  height = "620px",
  showControls = true,
  showVessels = true,
  showForecast = true,
}) => {
  const [activeLayer, setActiveLayer] =
    useState("INTEL");

  const [selectedVessel, setSelectedVessel] =
    useState(null);

  const [focusTarget, setFocusTarget] =
    useState(null);

  const [systemOnline, setSystemOnline] =
    useState(true);

  /* =======================================================
     LAYER VISIBILITY
  ======================================================= */

  const layerVisibility = useMemo(() => {
    return {
      spill:
        activeLayer === "INTEL" ||
        activeLayer === "SPILL",

      vessels:
        showVessels &&
        (activeLayer === "INTEL" ||
          activeLayer === "VESSEL"),

      drift:
        showForecast &&
        (activeLayer === "INTEL" ||
          activeLayer === "DRIFT"),
    };
  }, [
    activeLayer,
    showVessels,
    showForecast,
  ]);

  /* =======================================================
     SPILL BOUNDARY
  ======================================================= */

  const spillPolygon = useMemo(
    () => [
      [18.68, 72.82],
      [18.71, 72.86],
      [18.73, 72.91],
      [18.77, 72.96],
      [18.80, 72.94],
      [18.79, 72.88],
      [18.75, 72.83],
      [18.70, 72.80],
    ],
    []
  );

  /* =======================================================
     VESSEL CLICK
  ======================================================= */

  const handleVesselClick = (vessel) => {
    setSelectedVessel(vessel);
    setFocusTarget(vessel.position);
  };

  /* =======================================================
     LAYER CHANGE
  ======================================================= */

  const handleLayerChange = (layer) => {
    setActiveLayer(layer);

    if (layer === "SPILL") {
      setFocusTarget(CENTER);
    }

    if (layer === "DRIFT") {
      setFocusTarget([18.86, 72.98]);
    }

    if (layer === "VESSEL") {
      setFocusTarget(vessels[0].position);
    }

    if (layer === "INTEL") {
      setFocusTarget(CENTER);
    }
  };

  /* =======================================================
     RECENTER
  ======================================================= */

  const handleRecenter = () => {
    setSelectedVessel(null);
    setFocusTarget(CENTER);
  };

  return (
    <div
      className="oiltrace-map-wrapper"
      style={{
        height,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* =================================================
          TOP BAR
      ================================================= */}

      <div className="oiltrace-map-topbar">
        <div className="oiltrace-map-title">
          <div className="oiltrace-live-icon">
            <Radar size={17} />
          </div>

          <div>
            <div className="oiltrace-map-heading">
              MARITIME INTELLIGENCE
            </div>

            <div className="oiltrace-map-subheading">
              ARABIAN SEA • 18.742°N • 72.913°E
            </div>
          </div>
        </div>

        <div
          className={`oiltrace-map-status ${
            systemOnline ? "online" : "offline"
          }`}
        >
          <span className="oiltrace-status-dot"></span>

          {systemOnline
            ? "SATELLITE LINK ACTIVE"
            : "SATELLITE LINK OFFLINE"}
        </div>
      </div>

      {/* =================================================
          LEAFLET MAP
      ================================================= */}

      <MapContainer
        center={CENTER}
        zoom={9}
        minZoom={5}
        maxZoom={18}
        scrollWheelZoom={true}
        zoomControl={true}
        className="oiltrace-leaflet-map"
      >
        {/* =================================================
            OPEN STREET MAP

            NO API KEY REQUIRED
        ================================================= */}

        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
          maxZoom={19}
        />

        {/* =================================================
            MAP CONTROLLER
        ================================================= */}

        <MapController
          focusTarget={focusTarget}
        />

        {/* =================================================
            SPILL AREA
        ================================================= */}

        {layerVisibility.spill && (
          <>
            <Polygon
              positions={spillPolygon}
              pathOptions={{
                color: "#fb7185",
                weight: 2,
                opacity: 1,
                fillColor: "#ef4444",
                fillOpacity: 0.18,
              }}
            />

            {/* Outer radius */}

            <Circle
              center={CENTER}
              radius={13500}
              pathOptions={{
                color: "#fb7185",
                weight: 1,
                opacity: 0.3,
                fillColor: "#fb7185",
                fillOpacity: 0.03,
              }}
            />

            {/* Inner radius */}

            <Circle
              center={CENTER}
              radius={7500}
              pathOptions={{
                color: "#fb923c",
                weight: 1,
                opacity: 0.35,
                fillColor: "#fb923c",
                fillOpacity: 0.04,
              }}
            />
          </>
        )}

        {/* =================================================
            PROBABLE ORIGIN
        ================================================= */}

        {layerVisibility.spill && (
          <CircleMarker
            center={CENTER}
            radius={9}
            pathOptions={{
              color: "#ffffff",
              fillColor: "#fb7185",
              fillOpacity: 1,
              weight: 2,
            }}
          >
            <Tooltip
              permanent
              direction="top"
              offset={[0, -8]}
            >
              <strong>
                PROBABLE ORIGIN
              </strong>
            </Tooltip>

            <Popup>
              <div className="oiltrace-popup">
                <div className="popup-kicker">
                  PROBABLE ORIGIN
                </div>

                <strong>
                  Oil Spill Detection Zone
                </strong>

                <div className="popup-row">
                  <span>Confidence</span>
                  <b>94.8%</b>
                </div>

                <div className="popup-row">
                  <span>Area</span>
                  <b>42.6 km²</b>
                </div>

                <div className="popup-row">
                  <span>Severity</span>
                  <b className="popup-critical">
                    HIGH
                  </b>
                </div>

                <div className="popup-row">
                  <span>Coordinates</span>
                  <b>
                    18.742°N
                    <br />
                    72.913°E
                  </b>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        )}

        {/* =================================================
            DRIFT FORECAST
        ================================================= */}

        <AnimatedDriftPath
          visible={layerVisibility.drift}
        />

        {/* =================================================
            VESSEL ROUTES
        ================================================= */}

        <VesselRoutes
          visible={layerVisibility.vessels}
        />

        {/* =================================================
            VESSELS
        ================================================= */}

        {layerVisibility.vessels &&
          vessels.map((vessel) => {
            const color = riskColor(
              vessel.risk
            );

            return (
              <CircleMarker
                key={vessel.id}
                center={vessel.position}
                radius={
                  selectedVessel?.id === vessel.id
                    ? 9
                    : 6
                }
                pathOptions={{
                  color,
                  fillColor: color,
                  fillOpacity: 1,
                  weight:
                    selectedVessel?.id ===
                    vessel.id
                      ? 3
                      : 2,
                }}
                eventHandlers={{
                  click: () =>
                    handleVesselClick(vessel),
                }}
              >
                <Tooltip
                  direction="top"
                  offset={[0, -6]}
                >
                  <strong>
                    {vessel.name}
                  </strong>

                  <br />

                  {vessel.type}

                  <br />

                  Risk: {vessel.risk}

                  <br />

                  Score: {vessel.score}%
                </Tooltip>

                <Popup>
                  <div className="oiltrace-popup">
                    <div className="popup-kicker">
                      AIS CORRELATION
                    </div>

                    <h3>
                      {vessel.name}
                    </h3>

                    <div className="popup-imo">
                      {vessel.imo}
                    </div>

                    <div className="popup-score">
                      <span>
                        Attribution Score
                      </span>

                      <strong>
                        {vessel.score}%
                      </strong>
                    </div>

                    <div className="popup-row">
                      <span>Vessel Type</span>
                      <b>{vessel.type}</b>
                    </div>

                    <div className="popup-row">
                      <span>Flag</span>
                      <b>{vessel.flag}</b>
                    </div>

                    <div className="popup-row">
                      <span>Distance</span>
                      <b>{vessel.distance}</b>
                    </div>

                    <div
                      className="popup-risk"
                      style={{
                        color,
                      }}
                    >
                      ● {vessel.risk} PRIORITY
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
      </MapContainer>

      {/* =================================================
          RADAR OVERLAY
      ================================================= */}

      <div className="oiltrace-radar-overlay">
        <div className="radar-sweep"></div>

        <div className="radar-circle radar-one"></div>

        <div className="radar-circle radar-two"></div>

        <div className="radar-circle radar-three"></div>

        <Radar size={17} />
      </div>

      {/* =================================================
          SCAN LINE
      ================================================= */}

      <div className="oiltrace-map-scanline"></div>

      {/* =================================================
          LAYER PANEL
      ================================================= */}

      {showControls && (
        <div className="oiltrace-layer-panel">
          <div className="layer-panel-title">
            <Satellite size={14} />

            INTELLIGENCE LAYERS
          </div>

          {[
            ["INTEL", "Full Intelligence"],
            ["SPILL", "Spill Boundary"],
            ["VESSEL", "AIS Vessels"],
            ["DRIFT", "Drift Forecast"],
          ].map(([id, label]) => (
            <button
              key={id}
              type="button"
              className={
                activeLayer === id
                  ? "layer-btn active"
                  : "layer-btn"
              }
              onClick={() =>
                handleLayerChange(id)
              }
            >
              <span className="layer-indicator"></span>

              {label}
            </button>
          ))}
        </div>
      )}

      {/* =================================================
          RIGHT CONTROL DOCK
      ================================================= */}

      {showControls && (
        <div className="oiltrace-map-dock">
          {/* Recenter */}

          <button
            type="button"
            title="Recenter spill"
            onClick={handleRecenter}
          >
            <Target size={17} />
          </button>

          {/* System link */}

          <button
            type="button"
            title="Toggle intelligence link"
            onClick={() =>
              setSystemOnline(
                (value) => !value
              )
            }
          >
            <Radio size={17} />
          </button>

          {/* Focus top vessel */}

          <button
            type="button"
            title="Focus highest risk vessel"
            onClick={() =>
              handleVesselClick(
                vessels[0]
              )
            }
          >
            <Ship size={17} />
          </button>
        </div>
      )}

      {/* =================================================
          SELECTED VESSEL INTELLIGENCE
      ================================================= */}

      {selectedVessel && (
        <div className="oiltrace-selected-vessel">
          <div className="selected-vessel-top">
            <div>
              <div className="selected-kicker">
                SELECTED AIS CONTACT
              </div>

              <div className="selected-vessel-name">
                {selectedVessel.name}
              </div>
            </div>

            <button
              type="button"
              onClick={() =>
                setSelectedVessel(null)
              }
              aria-label="Close selected vessel"
            >
              ×
            </button>
          </div>

          <div className="selected-vessel-grid">
            <div>
              <span>IMO</span>
              <strong>
                {selectedVessel.imo.replace(
                  "IMO ",
                  ""
                )}
              </strong>
            </div>

            <div>
              <span>TYPE</span>
              <strong>
                {selectedVessel.type}
              </strong>
            </div>

            <div>
              <span>DISTANCE</span>
              <strong>
                {selectedVessel.distance}
              </strong>
            </div>

            <div>
              <span>FLAG</span>
              <strong>
                {selectedVessel.flag}
              </strong>
            </div>
          </div>

          <div className="selected-analysis-line">
            <div>
              <span>
                ATTRIBUTION SCORE
              </span>

              <strong>
                {selectedVessel.score}%
              </strong>
            </div>

            <div
              className="selected-risk"
              style={{
                color: riskColor(
                  selectedVessel.risk
                ),
              }}
            >
              {selectedVessel.risk}
            </div>
          </div>

          <div className="selected-score-track">
            <div
              className="selected-score-fill"
              style={{
                width: `${selectedVessel.score}%`,
                background:
                  riskColor(
                    selectedVessel.risk
                  ),
              }}
            ></div>
          </div>
        </div>
      )}

      {/* =================================================
          BOTTOM HUD
      ================================================= */}

      <div className="oiltrace-map-bottom-hud">
        <div className="hud-block">
          <span className="hud-label">
            ACTIVE DETECTIONS
          </span>

          <span className="hud-value">
            03
          </span>
        </div>

        <div className="hud-divider"></div>

        <div className="hud-block">
          <span className="hud-label">
            AIS CONTACTS
          </span>

          <span className="hud-value">
            05
          </span>
        </div>

        <div className="hud-divider"></div>

        <div className="hud-block">
          <span className="hud-label">
            DETECTION CONF.
          </span>

          <span className="hud-value cyan">
            94.8%
          </span>
        </div>

        <div className="hud-divider"></div>

        <div className="hud-block">
          <span className="hud-label">
            CORRELATION
          </span>

          <span className="hud-value purple">
            94%
          </span>
        </div>

        <div className="hud-divider"></div>

        <div className="hud-block">
          <span className="hud-label">
            SYSTEM
          </span>

          <span
            className={`hud-value ${
              systemOnline
                ? "online"
                : "danger"
            }`}
          >
            {systemOnline
              ? "ONLINE"
              : "OFFLINE"}
          </span>
        </div>
      </div>

      {/* =================================================
          LEGEND
      ================================================= */}

      <div className="oiltrace-map-legend">
        <div className="legend-title">
          <Layers3 size={13} />
          LIVE LEGEND
        </div>

        <div className="legend-item">
          <span className="legend-dot spill"></span>
          Spill Zone
        </div>

        <div className="legend-item">
          <span className="legend-dot critical"></span>
          Critical Vessel
        </div>

        <div className="legend-item">
          <span className="legend-dot high"></span>
          High Risk
        </div>

        <div className="legend-item">
          <span className="legend-dot forecast"></span>
          Drift Forecast
        </div>
      </div>

      {/* =================================================
          OFFLINE BANNER
      ================================================= */}

      {!systemOnline && (
        <div className="oiltrace-offline-banner">
          <ShieldAlert size={15} />

          SATELLITE LINK DEGRADED — DISPLAYING
          LAST KNOWN INTELLIGENCE
        </div>
      )}
    </div>
  );
};

export default MapView;