
// =====================================================
// OILTRACE STORAGE SYSTEM
// =====================================================

const INSPECTIONS_KEY = "oiltrace_inspections";
const REPORTS_KEY = "oiltrace_reports";
const SETTINGS_KEY = "oiltrace_settings";


// =====================================================
// GENERIC STORAGE HELPERS
// =====================================================

function readStorage(key, fallback = []) {
  try {
    const data = localStorage.getItem(key);

    if (!data) {
      return fallback;
    }

    const parsed = JSON.parse(data);

    return parsed;
  } catch (error) {
    console.error(`Failed reading ${key}:`, error);
    return fallback;
  }
}


function writeStorage(key, value) {
  try {
    localStorage.setItem(
      key,
      JSON.stringify(value)
    );

    return true;
  } catch (error) {
    console.error(`Failed writing ${key}:`, error);
    return false;
  }
}


// =====================================================
// INSPECTIONS
// =====================================================

export function getInspections() {
  return readStorage(
    INSPECTIONS_KEY,
    []
  );
}


export function saveInspection(inspection) {

  const inspections = getInspections();

  const newInspection = {
    id:
      inspection?.id ||
      `SPILL-${Date.now()}`,

    ...inspection,

    createdAt:
      inspection?.createdAt ||
      new Date().toISOString(),

    updatedAt:
      new Date().toISOString(),
  };

  const existingIndex = inspections.findIndex(
    (item) =>
      item.id === newInspection.id
  );

  if (existingIndex >= 0) {

    inspections[existingIndex] =
      newInspection;

  } else {

    inspections.unshift(
      newInspection
    );
  }

  writeStorage(
    INSPECTIONS_KEY,
    inspections
  );

  return newInspection;
}


// =====================================================
// REPORTS
// =====================================================

export function getReports() {
  return readStorage(
    REPORTS_KEY,
    []
  );
}


export function saveReport(report) {

  const reports = getReports();

  const newReport = {
    id:
      report?.id ||
      `RPT-${Date.now()}`,

    type:
      report?.type ||
      "Inspection Report",

    title:
      report?.title ||
      "OILTRACE Intelligence Report",

    date:
      report?.date ||
      new Date().toISOString(),

    createdAt:
      report?.createdAt ||
      new Date().toISOString(),

    periodFrom:
      report?.periodFrom ||
      "",

    periodTo:
      report?.periodTo ||
      "",

    status:
      report?.status ||
      "Generated",

    inspectionCount:
      Number(
        report?.inspectionCount || 0
      ),

    score:
      Number(
        report?.score || 0
      ),

    risk:
      report?.risk ||
      "LOW",

    summary:
      report?.summary ||
      "OILTRACE maritime intelligence report generated successfully.",

    inspections:
      Array.isArray(report?.inspections)
        ? report.inspections
        : [],
  };


  const existingIndex =
    reports.findIndex(
      (item) =>
        item.id === newReport.id
    );


  if (existingIndex >= 0) {

    reports[existingIndex] =
      newReport;

  } else {

    reports.unshift(
      newReport
    );
  }


  writeStorage(
    REPORTS_KEY,
    reports
  );

  return newReport;
}


// =====================================================
// GET SINGLE REPORT
// =====================================================

export function getReportById(id) {

  if (!id) {
    return null;
  }

  const reports = getReports();

  return (
    reports.find(
      (report) =>
        String(report.id) ===
        String(id)
    ) || null
  );
}


// =====================================================
// DELETE REPORT
// =====================================================

export function deleteReport(id) {

  const reports = getReports();

  const filtered =
    reports.filter(
      (report) =>
        String(report.id) !==
        String(id)
    );

  writeStorage(
    REPORTS_KEY,
    filtered
  );

  return true;
}


// =====================================================
// SETTINGS
// =====================================================

export function getSettings() {
  return readStorage(
    SETTINGS_KEY,
    {}
  );
}


export function saveSettings(settings) {

  writeStorage(
    SETTINGS_KEY,
    settings
  );

  return settings;
}


// =====================================================
// DEMO DATA
// =====================================================

export function seedDemoData() {

  const existing =
    getInspections();

  // Don't overwrite user's data
  if (
    Array.isArray(existing) &&
    existing.length > 0
  ) {
    return;
  }


  const demoInspections = [

    {
      id: "SPILL-001",

      location:
        "Arabian Sea",

      coordinates:
        "18.742° N, 72.913° E",

      latitude: 18.742,

      longitude: 72.913,

      area:
        42.6,

      areaUnit:
        "km²",

      confidence:
        94.8,

      score:
        94.8,

      risk:
        "HIGH",

      status:
        "Active",

      severity:
        "HIGH",

      detectedAt:
        "2026-09-12T00:18:00",

      createdAt:
        "2026-09-12T00:18:00",

      source:
        "Sentinel-1 SAR",

      satellite:
        "Sentinel-1",

      shape:
        "Elongated / Irregular",

      perimeter:
        31.7,

      age:
        "8–14 hours",

      description:
        "High-confidence oil spill detected in the Arabian Sea."
    },


    {
      id: "SPILL-002",

      location:
        "Bay of Bengal",

      coordinates:
        "16.231° N, 82.114° E",

      latitude: 16.231,

      longitude: 82.114,

      area:
        18.4,

      areaUnit:
        "km²",

      confidence:
        91.3,

      score:
        91.3,

      risk:
        "MEDIUM",

      status:
        "Monitoring",

      severity:
        "MEDIUM",

      detectedAt:
        "2026-09-11T18:42:00",

      createdAt:
        "2026-09-11T18:42:00",

      source:
        "Sentinel-1 SAR",

      satellite:
        "Sentinel-1",

      shape:
        "Irregular",

      perimeter:
        19.8,

      age:
        "12–20 hours",

      description:
        "Medium-risk spill under active monitoring."
    },


    {
      id: "SPILL-003",

      location:
        "Indian Ocean",

      coordinates:
        "11.823° N, 74.521° E",

      latitude: 11.823,

      longitude: 74.521,

      area:
        8.7,

      areaUnit:
        "km²",

      confidence:
        89.6,

      score:
        89.6,

      risk:
        "LOW",

      status:
        "Resolved",

      severity:
        "LOW",

      detectedAt:
        "2026-09-11T12:06:00",

      createdAt:
        "2026-09-11T12:06:00",

      source:
        "Sentinel-1 SAR",

      satellite:
        "Sentinel-1",

      shape:
        "Compact",

      perimeter:
        12.4,

      age:
        "24–36 hours",

      description:
        "Previously detected spill marked as resolved."
    },
  ];


  writeStorage(
    INSPECTIONS_KEY,
    demoInspections
  );


  // Create demo reports only if none exist

  const existingReports =
    getReports();

  if (
    !existingReports ||
    existingReports.length === 0
  ) {

    const demoReports = [

      {
        id: "RPT-DEMO-001",

        type:
          "Compliance Summary",

        title:
          "September Maritime Compliance Summary",

        date:
          "2026-09-12T08:30:00",

        createdAt:
          "2026-09-12T08:30:00",

        periodFrom:
          "2026-09-01",

        periodTo:
          "2026-09-12",

        status:
          "Generated",

        inspectionCount:
          3,

        score:
          91.9,

        risk:
          "HIGH",

        summary:
          "Three maritime spill intelligence cases were analysed using satellite-derived observations and supporting vessel intelligence.",

        inspections:
          demoInspections.map(
            (item) => item.id
          ),
      },

    ];

    writeStorage(
      REPORTS_KEY,
      demoReports
    );
  }
}

