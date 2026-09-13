import React, { useRef, useState } from "react";
import {
  Upload,
  Image as ImageIcon,
  Camera,
  X,
  CheckCircle2,
  FileImage,
  Plus,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function UploadBox({
  onFilesSelected,
  multiple = true,
  accept = "image/jpeg,image/jpg,image/png,image/webp",
  maxFiles = 4,
}) {
  const inputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);

  const processFiles = (selectedFiles) => {
    const imageFiles = Array.from(selectedFiles).filter(
      (file) =>
        file.type.startsWith("image/")
    );

    const limitedFiles = imageFiles.slice(
      0,
      maxFiles
    );

    setFiles(limitedFiles);

    if (onFilesSelected) {
      onFilesSelected(limitedFiles);
    }
  };

  const handleInputChange = (event) => {
    processFiles(event.target.files);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);

    if (event.dataTransfer.files) {
      processFiles(event.dataTransfer.files);
    }
  };

  const removeFile = (index) => {
    const updated = files.filter(
      (_, fileIndex) => fileIndex !== index
    );

    setFiles(updated);

    if (onFilesSelected) {
      onFilesSelected(updated);
    }
  };

  const openFilePicker = () => {
    inputRef.current?.click();
  };

  return (
    <div className="w-full">

      {/* Hidden input */}

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleInputChange}
        className="hidden"
      />

      {/* =====================================================
          EMPTY STATE
      ====================================================== */}

      {files.length === 0 && (
        <motion.div
          whileHover={{
            borderColor:
              "rgba(34,211,238,0.35)",
          }}
          onDragOver={(event) => {
            event.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() =>
            setDragActive(false)
          }
          onDrop={handleDrop}
          className={`relative overflow-hidden rounded-3xl border-2 border-dashed p-8 text-center transition-all ${
            dragActive
              ? "border-cyan-400/50 bg-cyan-400/[0.06]"
              : "border-slate-800 bg-[#07131f]/60"
          }`}
        >

          {/* Glow */}

          <div className="pointer-events-none absolute left-1/2 top-1/2 h-40 w-40 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-400/5 blur-3xl" />

          {/* Icon */}

          <motion.div
            animate={{
              y: [0, -5, 0],
            }}
            transition={{
              duration: 2.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="relative mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.07] text-cyan-400"
          >
            {dragActive ? (
              <Upload size={25} />
            ) : (
              <ImageIcon size={25} />
            )}
          </motion.div>

          <h3 className="relative mt-5 text-sm font-semibold text-white">
            Upload Satellite Imagery
          </h3>

          <p className="relative mx-auto mt-2 max-w-md text-xs leading-relaxed text-slate-500">
            Drag and drop satellite images here, or
            select files from your device for oil-spill
            analysis.
          </p>

          {/* Buttons */}

          <div className="relative mt-6 flex flex-wrap items-center justify-center gap-2">

            <button
              type="button"
              onClick={openFilePicker}
              className="flex items-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2.5 text-xs font-semibold text-cyan-300 transition hover:border-cyan-400/40 hover:bg-cyan-400/15"
            >
              <Upload size={14} />
              Choose Images
            </button>

            <button
              type="button"
              onClick={openFilePicker}
              className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/60 px-4 py-2.5 text-xs font-medium text-slate-400 transition hover:border-slate-600 hover:text-white"
            >
              <Camera size={14} />
              Camera
            </button>
          </div>

          {/* Formats */}

          <div className="relative mt-6 flex flex-wrap items-center justify-center gap-2">
            {["JPG", "JPEG", "PNG", "WEBP"].map(
              (format) => (
                <span
                  key={format}
                  className="rounded-md border border-slate-800 bg-slate-900/50 px-2 py-1 text-[8px] font-medium text-slate-600"
                >
                  {format}
                </span>
              )
            )}

            <span className="text-[8px] text-slate-700">
              •
            </span>

            <span className="text-[8px] text-slate-600">
              Max {maxFiles} images
            </span>
          </div>
        </motion.div>
      )}

      {/* =====================================================
          FILE PREVIEW
      ====================================================== */}

      {files.length > 0 && (
        <div className="rounded-3xl border border-slate-800/80 bg-[#07131f]/70 p-4">

          {/* Header */}

          <div className="mb-4 flex items-center justify-between">

            <div>
              <div className="flex items-center gap-2">
                <CheckCircle2
                  size={15}
                  className="text-emerald-400"
                />

                <h3 className="text-xs font-semibold text-white">
                  Imagery Ready
                </h3>
              </div>

              <p className="mt-1 text-[9px] text-slate-600">
                {files.length} image
                {files.length > 1 ? "s" : ""} selected
              </p>
            </div>

            <button
              type="button"
              onClick={openFilePicker}
              className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900/60 px-2.5 py-2 text-[9px] text-slate-400 transition hover:border-cyan-400/20 hover:text-cyan-300"
            >
              <Plus size={12} />
              Add
            </button>
          </div>

          {/* Preview grid */}

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">

            <AnimatePresence>
              {files.map((file, index) => (
                <motion.div
                  key={`${file.name}-${index}`}
                  initial={{
                    opacity: 0,
                    scale: 0.9,
                  }}
                  animate={{
                    opacity: 1,
                    scale: 1,
                  }}
                  exit={{
                    opacity: 0,
                    scale: 0.9,
                  }}
                  className="group relative overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50"
                >
                  <img
                    src={URL.createObjectURL(file)}
                    alt={file.name}
                    className="aspect-square w-full object-cover opacity-75 transition group-hover:scale-105 group-hover:opacity-100"
                  />

                  {/* Overlay */}

                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />

                  {/* Remove */}

                  <button
                    type="button"
                    onClick={() =>
                      removeFile(index)
                    }
                    className="absolute right-2 top-2 flex h-6 w-6 items-center justify-center rounded-lg bg-black/60 text-white opacity-0 backdrop-blur-sm transition group-hover:opacity-100 hover:bg-red-500"
                  >
                    <X size={12} />
                  </button>

                  {/* File info */}

                  <div className="absolute bottom-0 left-0 right-0 p-2">
                    <div className="flex items-center gap-1.5">
                      <FileImage
                        size={10}
                        className="text-cyan-400"
                      />

                      <p className="truncate text-[8px] font-medium text-white">
                        {file.name}
                      </p>
                    </div>

                    <p className="mt-1 text-[7px] text-slate-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
}