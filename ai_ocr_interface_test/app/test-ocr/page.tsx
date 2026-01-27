'use client';

import { useState } from 'react';
import Image from 'next/image';

interface OCRBlock {
  text: string;
  confidence: number;
  bbox?: number[][];
}

interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  duration?: string;
  instructions?: string;
}

interface Reminder {
  time: string;
  instruction: string;
  enabled: boolean;
}

interface PrescriptionData {
  patient_info: {
    name?: string;
    age?: string;
    gender?: string;
    patient_id?: string;
  };
  prescription_details: {
    date?: string;
    doctor_name?: string;
    clinic_name?: string;
    diagnosis?: string;
  };
  medications: Medication[];
  dosage_instructions: Array<{ text: string; timing: string; with_food?: boolean }>;
  reminder_schedule: Reminder[];
  raw_ocr_data: {
    full_text: string;
    confidence: number;
    blocks_count: number;
    language: string;
  };
}

export default function OCRTestPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [ocrBlocks, setOcrBlocks] = useState<OCRBlock[]>([]);
  const [prescription, setPrescription] = useState<PrescriptionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'ocr' | 'prescription' | 'reminders'>('ocr');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setError('');
    setOcrBlocks([]);
    setPrescription(null);
  };

  const processOCR = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Call the actual OCR service
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://localhost:8000/ocr', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`OCR service error: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('OCR Result:', result);

      // Extract blocks for display
      const blocks: OCRBlock[] = result.blocks?.map((block: any) => ({
        text: block.text,
        confidence: block.confidence,
        bbox: block.bbox,
      })) || [];

      setOcrBlocks(blocks);

      // Format as prescription data
      const prescriptionData: PrescriptionData = {
        patient_info: result.patient_info || {
          name: undefined,
          age: undefined,
          gender: undefined,
          patient_id: undefined,
        },
        prescription_details: result.prescription_details || {
          date: undefined,
          doctor_name: undefined,
          clinic_name: undefined,
          diagnosis: undefined,
        },
        medications: result.medications || [],
        dosage_instructions: result.dosage_instructions || [],
        reminder_schedule: result.reminder_schedule || [],
        raw_ocr_data: {
          full_text: result.full_text || blocks.map(b => b.text).join(' '),
          confidence: result.overall_confidence || 0,
          blocks_count: blocks.length,
          language: result.language || 'en',
        },
      };

      setPrescription(prescriptionData);
      setActiveTab('prescription');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'OCR processing failed');
    } finally {
      setLoading(false);
    }
  };

  const ConfidenceBadge = ({ confidence }: { confidence: number }) => {
    const getColor = () => {
      if (confidence >= 0.9) return 'bg-green-100 text-green-800';
      if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-800';
      return 'bg-red-100 text-red-800';
    };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${getColor()}`}>
        {(confidence * 100).toFixed(0)}%
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            OCR Prescription Test Interface
          </h1>
          <p className="text-gray-600 mb-8">
            Upload a prescription image to test OCR extraction and formatting
          </p>

          {/* File Upload Section */}
          <div className="mb-8">
            <label className="block mb-2 font-semibold text-gray-700">
              Select Prescription Image
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none p-2"
            />
          </div>

          {/* Image Preview */}
          {previewUrl && (
            <div className="mb-8 bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-700 mb-3">Image Preview</h3>
              <div className="relative w-full max-w-md mx-auto">
                <img
                  src={previewUrl}
                  alt="Prescription preview"
                  className="w-full h-auto rounded-lg border-2 border-gray-200"
                />
              </div>
            </div>
          )}

          {/* Process Button */}
          {selectedFile && (
            <button
              onClick={processOCR}
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed mb-8"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Processing OCR...
                </span>
              ) : (
                '🔍 Process OCR & Generate Prescription'
              )}
            </button>
          )}

          {/* Error Display */}
          {error && (
            <div className="mb-8 bg-red-50 border-l-4 border-red-500 p-4 rounded">
              <p className="text-red-700 font-medium">❌ {error}</p>
            </div>
          )}

          {/* Results Tabs */}
          {(ocrBlocks.length > 0 || prescription) && (
            <div className="mt-8">
              <div className="border-b border-gray-200 mb-6">
                <nav className="flex space-x-8">
                  <button
                    onClick={() => setActiveTab('ocr')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
                      activeTab === 'ocr'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    📝 OCR Blocks ({ocrBlocks.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('prescription')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
                      activeTab === 'prescription'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    💊 Prescription Data
                  </button>
                  <button
                    onClick={() => setActiveTab('reminders')}
                    className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
                      activeTab === 'reminders'
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    ⏰ Reminder Schedule ({prescription?.reminder_schedule.length || 0})
                  </button>
                </nav>
              </div>

              {/* OCR Blocks Tab */}
              {activeTab === 'ocr' && (
                <div className="space-y-3">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">
                    Extracted Text Blocks
                  </h3>
                  {ocrBlocks.map((block, index) => (
                    <div
                      key={index}
                      className="bg-gray-50 p-4 rounded-lg border border-gray-200 flex items-start justify-between"
                    >
                      <div className="flex-1">
                        <span className="text-sm text-gray-500 mr-3">#{index + 1}</span>
                        <span className="text-gray-800">{block.text}</span>
                      </div>
                      <ConfidenceBadge confidence={block.confidence} />
                    </div>
                  ))}
                </div>
              )}

              {/* Prescription Tab */}
              {activeTab === 'prescription' && prescription && (
                <div className="space-y-6">
                  {/* Patient Info */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">👤 Patient Information</h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div><span className="font-medium">Name:</span> {prescription.patient_info.name || 'N/A'}</div>
                      <div><span className="font-medium">Age:</span> {prescription.patient_info.age || 'N/A'}</div>
                      <div><span className="font-medium">Gender:</span> {prescription.patient_info.gender || 'N/A'}</div>
                      <div><span className="font-medium">Patient ID:</span> {prescription.patient_info.patient_id || 'N/A'}</div>
                    </div>
                  </div>

                  {/* Prescription Details */}
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">📋 Prescription Details</h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div><span className="font-medium">Date:</span> {prescription.prescription_details.date || 'N/A'}</div>
                      <div><span className="font-medium">Doctor:</span> {prescription.prescription_details.doctor_name || 'N/A'}</div>
                      <div><span className="font-medium">Clinic:</span> {prescription.prescription_details.clinic_name || 'N/A'}</div>
                      <div><span className="font-medium">Diagnosis:</span> {prescription.prescription_details.diagnosis || 'N/A'}</div>
                    </div>
                  </div>

                  {/* Medications */}
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">💊 Medications</h3>
                    <div className="space-y-3">
                      {prescription.medications.map((med, index) => (
                        <div key={index} className="bg-white p-3 rounded border border-purple-200">
                          <h4 className="font-semibold text-purple-900">{med.name}</h4>
                          <div className="mt-2 text-sm space-y-1 text-gray-700">
                            <div>📊 <span className="font-medium">Dosage:</span> {med.dosage}</div>
                            <div>🔄 <span className="font-medium">Frequency:</span> {med.frequency}</div>
                            {med.duration && <div>⏱️ <span className="font-medium">Duration:</span> {med.duration}</div>}
                            {med.instructions && <div>📝 <span className="font-medium">Instructions:</span> {med.instructions}</div>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* OCR Metadata */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">📊 OCR Metadata</h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div><span className="font-medium">Language:</span> {prescription.raw_ocr_data.language.toUpperCase()}</div>
                      <div><span className="font-medium">Blocks:</span> {prescription.raw_ocr_data.blocks_count}</div>
                      <div className="col-span-2">
                        <span className="font-medium">Confidence:</span>{' '}
                        <ConfidenceBadge confidence={prescription.raw_ocr_data.confidence} />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Reminders Tab */}
              {activeTab === 'reminders' && prescription && (
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">
                    ⏰ Medication Reminder Schedule
                  </h3>
                  {prescription.reminder_schedule.length > 0 ? (
                    <div className="space-y-3">
                      {prescription.reminder_schedule.map((reminder, index) => (
                        <div
                          key={index}
                          className={`p-4 rounded-lg border-2 ${
                            reminder.enabled
                              ? 'bg-green-50 border-green-300'
                              : 'bg-gray-50 border-gray-300'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center mb-2">
                                <span className="text-2xl font-bold text-indigo-600 mr-3">
                                  {reminder.time}
                                </span>
                                <span className={`px-2 py-1 rounded text-xs font-medium ${
                                  reminder.enabled
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-gray-100 text-gray-600'
                                }`}>
                                  {reminder.enabled ? '✓ Enabled' : '✗ Disabled'}
                                </span>
                              </div>
                              <p className="text-gray-700">{reminder.instruction}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                      <p className="text-yellow-800">
                        ⚠️ No reminder schedule generated. The OCR text did not contain timing keywords.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
