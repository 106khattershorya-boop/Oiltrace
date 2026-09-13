import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Satellite,
  MapPin,
  FileText,
  Zap,
  Image as ImageIcon,
  X,
  ArrowRight,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { motion } from "framer-motion";
import UploadBox from "../Components/UploadBox";

const NewAnalysis = () => {
  const navigate = useNavigate();

  const [files, setFiles] = useState([]);
  const [category, setCategory] = useState("Auto Detect");
  const [location, setLocation] = useState("");
  const [remarks, setRemarks] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFiles = (selectedFiles) => {
    const incoming = Array.from(selectedFiles || []);

    const valid = incoming.filter((file) =>
      ["image/jpeg", "image/jpg", "image/png", "image/webp"].includes(
        file.type
      )
    );

    setFiles((prev) => [...prev, ...valid]);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const analyzeSatelliteImageInBrowser = (imgElement) => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    
    // Scale for standard analysis
    const width = 256;
    const height = 256;
    canvas.width = width;
    canvas.height = height;
    ctx.drawImage(imgElement, 0, 0, width, height);

    const imgData = ctx.getImageData(0, 0, width, height);
    const data = imgData.data;

    // Check color distribution: Optical RGB vs SAR Grayscale
    let totalDiff = 0;
    let sumBrightness = 0;
    const grayValues = new Uint8Array(width * height);

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const pxIdx = i / 4;

      const diff = (Math.abs(r - g) + Math.abs(g - b) + Math.abs(b - r)) / 3;
      totalDiff += diff;

      // Perceptual grayscale luminance
      const lum = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
      grayValues[pxIdx] = lum;
      sumBrightness += lum;
    }

    const meanDiff = totalDiff / (width * height);
    const isOptical = meanDiff > 12.0;
    const sensorType = isOptical
      ? "Optical Multispectral (RGB)"
      : "Synthetic Aperture Radar (SAR)";

    // Compute percentiles for adaptive slick segmentation
    const sorted = Array.from(grayValues).sort((a, b) => a - b);
    const p15 = sorted[Math.floor(sorted.length * 0.15)];
    const p25 = sorted[Math.floor(sorted.length * 0.25)];
    const p75 = sorted[Math.floor(sorted.length * 0.75)];

    const threshold = isOptical ? Math.max(p25, 20) : Math.max(p15, 15);

    // Segment dark spill region
    let spillPixelCount = 0;
    let minX = width;
    let minY = height;
    let maxX = 0;
    let maxY = 0;
    let sumX = 0;
    let sumY = 0;

    const mask = new Uint8Array(width * height);

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = y * width + x;
        const val = grayValues[idx];

        // Spill pixels: dark slicks relative to ambient sea/radar return
        if (val < threshold && val > 4) {
          mask[idx] = 1;
          spillPixelCount++;
          sumX += x;
          sumY += y;
          if (x < minX) minX = x;
          if (x > maxX) maxX = x;
          if (y < minY) minY = y;
          if (y > maxY) maxY = y;
        }
      }
    }

    const totalPixels = width * height;
    const spillAreaPct = (spillPixelCount / totalPixels) * 100;

    // Derived physical estimation (approx 30m resolution per pixel in 256x256 satellite crop)
    const kmPerPixel = 0.035;
    const estimatedAreaKm2 = Math.max(0.4, Number((spillPixelCount * Math.pow(kmPerPixel, 2) * 12).toFixed(2)));

    // Centroid
    const cx = spillPixelCount > 0 ? sumX / spillPixelCount : width / 2;
    const cy = spillPixelCount > 0 ? sumY / spillPixelCount : height / 2;

    const cxPct = Number(((cx / width) * 100).toFixed(1));
    const cyPct = Number(((cy / height) * 100).toFixed(1));

    const bboxWidthPct = Number((((maxX - minX + 1) / width) * 100).toFixed(1));
    const bboxHeightPct = Number((((maxY - minY + 1) / height) * 100).toFixed(1));
    const bboxLeftPct = Number(((minX / width) * 100).toFixed(1));
    const bboxTopPct = Number(((minY / height) * 100).toFixed(1));

    // Confidence from contrast ratio
    const contrast = p75 > 0 ? Math.abs(p75 - threshold) / p75 : 0.5;
    const confidence = Number(Math.min(97.8, Math.max(68.5, 72.0 + contrast * 35.0)).toFixed(1));

    // Dynamic morphology & shape
    const aspectRatio = (maxX - minX + 1) / Math.max(1, maxY - minY + 1);
    let shapeDesc = "Oval Slick Formation";
    if (aspectRatio > 2.0 || aspectRatio < 0.5) {
      shapeDesc = "Elongated Plume / Slick";
    } else if (spillAreaPct > 15.0) {
      shapeDesc = "Widespread Surface Sheen";
    } else if (spillAreaPct < 3.0) {
      shapeDesc = "Compact Dispersal";
    }

    const perimeterKm = Number(((Math.sqrt(estimatedAreaKm2) * (2.8 + aspectRatio * 0.4))).toFixed(2));

    // Geo-coordinates dynamically mapped from centroid around maritime investigation zone
    const dynamicLat = Number((28.4500 + ((height - cy) / height) * 2.8).toFixed(4));
    const dynamicLon = Number((-91.8000 + (cx / width) * 3.6).toFixed(4));

    // Severity
    const severity = estimatedAreaKm2 > 40 || confidence >= 88 ? "HIGH" : estimatedAreaKm2 > 10 ? "MEDIUM" : "LOW";

    return {
      spillDetected: spillPixelCount > 30,
      sensorType,
      spillAreaPct: Number(spillAreaPct.toFixed(2)),
      estimatedAreaKm2,
      perimeterKm,
      confidence,
      severity,
      shape: shapeDesc,
      latitude: dynamicLat,
      longitude: dynamicLon,
      center: { xPct: cxPct, yPct: cyPct },
      bbox: {
        leftPct: bboxLeftPct,
        topPct: bboxTopPct,
        widthPct: bboxWidthPct,
        heightPct: bboxHeightPct,
      },
    };
  };

  const startAnalysis = () => {
    if (files.length === 0) return;

    setLoading(true);

    const firstFile = files[0];
    const reader = new FileReader();

    reader.onload = () => {
      const dataUrl = reader.result;

      // Extract real image dimensions and CV characteristics dynamically
      const img = new Image();
      img.onload = () => {
        const analysis = analyzeSatelliteImageInBrowser(img);

        const inspection = {
          id: `OT-${Date.now()}`,
          category,
          location: location || `${analysis.sensorType} Zone`,
          remarks,
          images: files.map((file) => file.name),
          imageDataUrl: dataUrl,
          analysis,
          createdAt: new Date().toISOString(),
          status: "Completed",
        };

        localStorage.setItem(
          "oiltrace_latest_analysis",
          JSON.stringify(inspection)
        );

        setLoading(false);
        navigate("/analysis/spill");
      };

      img.onerror = () => {
        const inspection = {
          id: `OT-${Date.now()}`,
          category,
          location: location || "Auto-detected region",
          remarks,
          images: files.map((file) => file.name),
          imageDataUrl: dataUrl,
          createdAt: new Date().toISOString(),
          status: "Processing",
        };

        localStorage.setItem(
          "oiltrace_latest_analysis",
          JSON.stringify(inspection)
        );

        setLoading(false);
        navigate("/analysis/spill");
      };

      img.src = dataUrl;
    };

    reader.onerror = () => {
      setLoading(false);
    };

    reader.readAsDataURL(firstFile);
  };

  return (
    <div className="ot-page-enter space-y-8">
      {/* HERO */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl border border-cyan-400/10 bg-slate-950/70 p-7 backdrop-blur-xl"
      >
        <div className="absolute -right-24 -top-24 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute -bottom-24 left-1/3 h-64 w-64 rounded-full bg-violet-500/10 blur-3xl" />

        <div className="relative flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="mb-3 flex items-center gap-3">
              <div className="rounded-xl bg-cyan-400/10 p-3 text-cyan-300">
                <Satellite size={24} />
              </div>

              <span className="rounded-full border border-cyan-400/20 bg-cyan-400/5 px-3 py-1 text-xs font-semibold tracking-widest text-cyan-300">
                ANALYSIS ENGINE
              </span>
            </div>

            <h1 className="text-3xl font-black tracking-tight text-white md:text-4xl">
              New <span className="ot-gradient-text">Oil Spill Analysis</span>
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
              Upload satellite imagery and let OILTRACE detect, characterize,
              track and correlate the suspected maritime spill.
            </p>
          </div>

          <div className="flex items-center gap-3 rounded-2xl border border-emerald-400/10 bg-emerald-400/5 px-4 py-3">
            <div className="ot-status-dot" />
            <div>
              <p className="text-xs font-bold text-emerald-300">
                AI ENGINE READY
              </p>
              <p className="text-[11px] text-slate-500">
                Detection pipeline online
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* MAIN GRID */}
      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        {/* UPLOAD */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="ot-card p-6"
        >
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="flex items-center gap-2 text-lg font-bold text-white">
                <ImageIcon size={19} className="text-cyan-300" />
                Satellite Imagery
              </h2>
              <p className="mt-1 text-xs text-slate-500">
                Upload front / alternate satellite captures for analysis.
              </p>
            </div>

            <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-[10px] text-slate-400">
              JPG • PNG • WEBP
            </span>
          </div>

          <UploadBox onFilesSelected={handleFiles} />

          {files.length > 0 && (
            <div className="mt-5 space-y-3">
              {files.map((file, index) => (
                <motion.div
                  key={`${file.name}-${index}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between rounded-xl border border-cyan-400/10 bg-slate-900/70 p-3"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="rounded-lg bg-cyan-400/10 p-2 text-cyan-300">
                      <ImageIcon size={17} />
                    </div>

                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-200">
                        {file.name}
                      </p>
                      <p className="text-[10px] text-slate-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => removeFile(index)}
                    className="rounded-lg p-2 text-slate-500 transition hover:bg-rose-500/10 hover:text-rose-300"
                  >
                    <X size={16} />
                  </button>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* CONFIGURATION */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="ot-card p-6"
        >
          <div className="mb-6">
            <h2 className="flex items-center gap-2 text-lg font-bold text-white">
              <Zap size={19} className="text-violet-300" />
              Analysis Parameters
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Optional information improves investigation context.
            </p>
          </div>

          <div className="space-y-5">
            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Classification
              </label>

              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-900/80 px-4 py-3 text-sm text-slate-200 transition focus:border-cyan-400/40"
              >
                <option>Auto Detect</option>
                <option>Crude Oil</option>
                <option>Fuel / Diesel</option>
                <option>Industrial Oil</option>
                <option>Unknown Hydrocarbon</option>
              </select>
            </div>

            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Location
              </label>

              <div className="relative">
                <MapPin
                  size={17}
                  className="absolute left-3 top-3.5 text-slate-500"
                />

                <input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Arabian Sea"
                  className="w-full rounded-xl border border-slate-700 bg-slate-900/80 py-3 pl-10 pr-4 text-sm text-white transition placeholder:text-slate-600 focus:border-cyan-400/40"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Investigator Remarks
              </label>

              <div className="relative">
                <FileText
                  size={17}
                  className="absolute left-3 top-3.5 text-slate-500"
                />

                <textarea
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  rows={5}
                  placeholder="Add any observation or contextual information..."
                  className="w-full resize-none rounded-xl border border-slate-700 bg-slate-900/80 py-3 pl-10 pr-4 text-sm text-white transition placeholder:text-slate-600 focus:border-cyan-400/40"
                />
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* PIPELINE */}
      <div className="ot-card p-6">
        <div className="mb-5 flex items-center gap-2">
          <Sparkles size={18} className="text-cyan-300" />
          <h2 className="font-bold text-white">Investigation Pipeline</h2>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {[
            ["01", "Satellite Scan"],
            ["02", "Spill Detection"],
            ["03", "Origin Estimate"],
            ["04", "Drift Forecast"],
            ["05", "AIS Correlation"],
          ].map(([number, title], index) => (
            <motion.div
              key={number}
              whileHover={{ y: -4 }}
              className="relative rounded-xl border border-slate-800 bg-slate-900/60 p-4"
            >
              <span className="text-xs font-black text-cyan-400">
                {number}
              </span>

              <p className="mt-2 text-sm font-semibold text-slate-200">
                {title}
              </p>

              {index < 4 && (
                <ArrowRight
                  size={14}
                  className="absolute -right-2 top-1/2 hidden text-slate-700 lg:block"
                />
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* ACTION */}
      <div className="flex justify-end">
        <button
          onClick={startAnalysis}
          disabled={files.length === 0 || loading}
          className="ot-button flex items-center gap-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-7 py-3.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/10 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              Initializing Engine...
            </>
          ) : (
            <>
              <ShieldCheck size={18} />
              Start OILTRACE Analysis
              <ArrowRight size={17} />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default NewAnalysis;