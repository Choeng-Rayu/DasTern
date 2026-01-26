import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <main className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8 mt-20">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            DasTern OCR Test Interface
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Test OCR extraction and prescription formatting without Docker
          </p>

          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-8 rounded">
            <h2 className="text-lg font-semibold text-blue-800 mb-2">
              🎯 Purpose
            </h2>
            <p className="text-blue-700">
              This interface allows you to test OCR functionality locally without requiring Docker containers or database connections.
              Upload a prescription image and see how it's processed into structured data with reminder schedules.
            </p>
          </div>

          <div className="space-y-6 mb-8">
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-800 mb-2">✅ Features</h3>
              <ul className="list-disc list-inside text-green-700 space-y-1">
                <li>Upload prescription images</li>
                <li>Extract text using OCR with confidence scores</li>
                <li>Format extracted text into structured prescription data</li>
                <li>Generate medication reminder schedules</li>
                <li>View patient info, medications, and dosage instructions</li>
              </ul>
            </div>

            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="font-semibold text-yellow-800 mb-2">📋 Test Modes</h3>
              <ul className="list-disc list-inside text-yellow-700 space-y-1">
                <li><strong>Mock Mode:</strong> Uses simulated OCR data for UI testing</li>
                <li><strong>Real OCR:</strong> Connect to actual OCR service (requires backend)</li>
              </ul>
            </div>
          </div>

          <Link
            href="/test-ocr"
            className="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 px-8 rounded-lg transition duration-200 text-lg"
          >
            🚀 Start OCR Test
          </Link>

          <div className="mt-8 pt-8 border-t border-gray-200">
            <h3 className="font-semibold text-gray-800 mb-3">🛠️ Setup Instructions</h3>
            <div className="bg-gray-50 p-4 rounded text-sm">
              <pre className="text-gray-700 whitespace-pre-wrap">
{`# Install dependencies
npm install

# Run development server
npm run dev

# Open in browser
http://localhost:3000/test-ocr`}
              </pre>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
