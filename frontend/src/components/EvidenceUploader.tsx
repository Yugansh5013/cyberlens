"use client";
import React, { useState } from "react";
import { uploadEvidence } from "../lib/api";

export default function EvidenceUploader({ onUpload }: { onUpload: (data: any) => void }) {
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    try {
      const data = await uploadEvidence(file, (p) => setProgress(p));
      onUpload(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="border-2 border-dashed border-blue-400 rounded-lg p-8 text-center bg-white shadow-sm">
      <input
        type="file"
        onChange={(e) => e.target.files && handleFile(e.target.files[0])}
        className="hidden"
        id="fileInput"
      />
      <label htmlFor="fileInput" className="cursor-pointer text-blue-700 font-medium">
        Click to upload or drag & drop your evidence
      </label>

      {progress > 0 && (
        <div className="mt-4 w-full bg-gray-200 rounded">
          <div
            className="h-2 bg-blue-600 rounded"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}
      {error && <p className="text-red-600 mt-2">{error}</p>}
    </div>
  );
}
