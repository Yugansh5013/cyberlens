"use client";
import { useState } from "react";
import EvidenceUploader from "@/components/EvidenceUploader";
import Link from "next/link";

export default function UploadPage() {
  const [fileData, setFileData] = useState<any | null>(null);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Upload Evidence</h1>
      <EvidenceUploader onUpload={setFileData} />

      {fileData && (
        <div className="bg-white p-4 rounded shadow mt-6">
          <h2 className="text-lg font-semibold mb-2">Upload Details</h2>
          <p><b>File ID:</b> {fileData.file_id}</p>
          <p><b>SHA256:</b> {fileData.sha256}</p>

          <Link
            href={`/cases/${fileData.file_id}`}
            className="inline-block mt-4 bg-blue-700 text-white px-4 py-2 rounded"
          >
            Analyze →
          </Link>
        </div>
      )}
    </div>
  );
}
