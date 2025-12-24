"use client";

import { useState } from "react";

export default function EvidenceUploader({
  onUpload,
  disabled = false,
}: {
  onUpload: (file: File) => void;
  disabled?: boolean;
}) {
  const [fileName, setFileName] = useState<string | null>(null);

  return (
    <div className="border-2 border-dashed border-gray-400 rounded-lg p-6 text-center bg-gray-50 hover:bg-gray-100 transition-colors">
      <input
        type="file"
        id="evidence-upload"
        accept=".png,.jpg,.jpeg,.pdf"
        disabled={disabled}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            setFileName(file.name);
            onUpload(file);
          }
        }}
        className="hidden"
      />

      <label
        htmlFor="evidence-upload"
        className={`cursor-pointer font-medium text-cyan-600 hover:text-cyan-800 ${
          disabled ? "opacity-50 cursor-not-allowed" : ""
        }`}
      >
        {fileName ? `Uploaded: ${fileName}` : "Click or Drag & Drop Evidence File"}
      </label>

      <p className="text-xs text-gray-500 mt-2">Supported: PNG, JPG, PDF</p>
    </div>
  );
}
