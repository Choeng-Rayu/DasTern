'use client';

import { useState, useCallback } from 'react';

interface Medication {
  name: string;
  strength: string | null;
  dosage: string | null;
  frequency: string;
  duration: string | null;
}

interface OCRResult {
  prescription_id: string;
  ocr_text: string;
  ocr_confidence: number;
  ai_enhanced: boolean;
  medications: Medication[];
}

export default function Home() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<OCRResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = useCallback((file: File) => {
    setSelectedFile(file);
    setError(null);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      const response = await fetch('/api/ocr-test', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to process image');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📋 DasTern OCR Test
          </h1>
          <p className="text-gray-600">
            Upload prescription image to extract medications and create reminders
          </p>
        </div>

        {/* Main Container */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              📤 Upload Prescription
            </h2>

            {/* Dropzone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                dragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
              }`}
            >
              <input 
                type="file" 
                id="file-upload" 
                accept="image/*" 
                onChange={handleChange}
                className="hidden"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                {preview ? (
                  <div className="space-y-4">
                    <img
                      src={preview}
                      alt="Preview"
                      className="max-h-64 mx-auto rounded-lg shadow-md"
                    />
                    <p className="text-sm text-gray-600">
                      {selectedFile?.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      Click or drag to replace
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="text-5xl">📷</div>
                    <p className="text-lg text-gray-700">
                      {dragActive
                        ? 'Drop the image here'
                        : 'Drag & drop prescription image here'}
                    </p>
                    <p className="text-sm text-gray-500">
                      or click to select file
                    </p>
                  </div>
                )}
              </label>
            </div>

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className={`w-full mt-4 py-3 px-6 rounded-lg font-semibold text-white transition-colors ${
                !selectedFile || uploading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {uploading ? (
                <span className="flex items-center justify-center">
                  <svg
                    className="animate-spin h-5 w-5 mr-3"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Processing...
                </span>
              ) : (
                '🚀 Process Prescription'
              )}
            </button>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">❌ {error}</p>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              📊 Results
            </h2>

            {!result ? (
              <div className="text-center py-12 text-gray-400">
                <div className="text-6xl mb-4">📝</div>
                <p>Upload a prescription to see results</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* OCR Text */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-700">
                      Extracted Text
                    </h3>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          result.ai_enhanced
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {result.ai_enhanced ? '🤖 AI Enhanced' : '📝 OCR Only'}
                      </span>
                      <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium">
                        {(result.ocr_confidence * 100).toFixed(1)}% Confidence
                      </span>
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">
                      {result.ocr_text}
                    </p>
                  </div>
                </div>

                {/* Medications */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-3">
                    💊 Detected Medications ({result.medications.length})
                  </h3>
                  <div className="space-y-3">
                    {result.medications.map((med, index) => (
                      <div
                        key={index}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-lg text-gray-800">
                            {med.name}
                          </h4>
                          {med.strength && (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                              {med.strength}
                            </span>
                          )}
                        </div>
                        <div className="space-y-1 text-sm text-gray-600">
                          {med.dosage && (
                            <p>
                              <span className="font-medium">Dosage:</span>{' '}
                              {med.dosage}
                            </p>
                          )}
                          <p>
                            <span className="font-medium">Frequency:</span>{' '}
                            {med.frequency}
                          </p>
                          {med.duration && (
                            <p>
                              <span className="font-medium">Duration:</span>{' '}
                              {med.duration}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Prescription ID */}
                <div className="text-xs text-gray-500 border-t pt-4">
                  <p>
                    <span className="font-medium">Prescription ID:</span>{' '}
                    {result.prescription_id}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Service Status */}
        <div className="mt-6 bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600 text-center">
            💡 <strong>Tip:</strong> Upload a clear image of the prescription for
            best results. The system uses OCR + AI to extract medication
            information.
          </p>
        </div>
      </div>
    </div>
  );
}
