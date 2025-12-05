import React, { useState, useEffect } from 'react';
import { X, Download, FileText, Loader2, AlertCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { getAllDocumentUrls, downloadDocument } from '@/utils/azureStorage';

interface DocumentViewerProps {
  claimId: string;
  onClose: () => void;
}

interface ClaimDocument {
  fileName: string;
  url: string;
  type: string;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({ claimId, onClose }) => {
  const [documents, setDocuments] = useState<ClaimDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<ClaimDocument | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, [claimId]);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const docs = await getAllDocumentUrls(claimId);
      setDocuments(docs);
      if (docs.length > 0) {
        setSelectedDoc(docs[0]);
      } else {
        setError('No documents found for this claim.');
      }
    } catch (err) {
      console.error('Error loading documents:', err);
      setError('Failed to load documents. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!selectedDoc) return;
    try {
      setIsDownloading(true);
      await downloadDocument(claimId, selectedDoc.fileName);
    } catch (err) {
      console.error('Error downloading document:', err);
      alert('Failed to download document. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-6xl h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-50 to-blue-100">
          <div>
            <h2 className="text-xl font-bold text-blue-900">Claim Documents</h2>
            <p className="text-sm text-blue-700">Claim ID: {claimId}</p>
            {selectedDoc && (
              <p className="text-xs text-blue-600 mt-1">{selectedDoc.fileName}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {selectedDoc && (
              <button
                onClick={handleDownload}
                disabled={isDownloading}
                className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
                title="Download document"
              >
                {isDownloading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Download className="h-4 w-4" />
                )}
                <span>Download</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="px-3 py-2 hover:bg-blue-100 rounded-lg transition-colors"
              title="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Document List Sidebar */}
          {!isLoading && documents.length > 0 && (
            <div className="w-72 border-r p-4 overflow-y-auto bg-gray-50">
              <h3 className="font-semibold mb-3 text-gray-700 flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Available Documents ({documents.length})
              </h3>
              <div className="space-y-2">
                {documents.map((doc) => (
                  <button
                    key={doc.fileName}
                    onClick={() => setSelectedDoc(doc)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      selectedDoc?.fileName === doc.fileName
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'bg-white hover:bg-blue-50 border border-gray-200'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <FileText className={`h-4 w-4 mt-0.5 flex-shrink-0 ${
                        selectedDoc?.fileName === doc.fileName ? 'text-white' : 'text-blue-600'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-medium mb-1 ${
                          selectedDoc?.fileName === doc.fileName ? 'text-white' : 'text-gray-900'
                        }`}>
                          {doc.type}
                        </div>
                        <div className={`text-xs truncate ${
                          selectedDoc?.fileName === doc.fileName ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {doc.fileName}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* PDF Viewer / Loading / Error */}
          <div className="flex-1 overflow-auto bg-gray-100">
            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <Card className="p-8">
                  <CardContent className="flex flex-col items-center gap-4">
                    <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
                    <p className="text-gray-600">Loading documents...</p>
                  </CardContent>
                </Card>
              </div>
            ) : error ? (
              <div className="flex items-center justify-center h-full">
                <Card className="p-8 max-w-md">
                  <CardContent className="flex flex-col items-center gap-4">
                    <AlertCircle className="h-12 w-12 text-red-500" />
                    <p className="text-gray-800 font-semibold">Error Loading Documents</p>
                    <p className="text-gray-600 text-center">{error}</p>
                    <button
                      onClick={loadDocuments}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Try Again
                    </button>
                  </CardContent>
                </Card>
              </div>
            ) : selectedDoc ? (
              <iframe
                src={selectedDoc.url}
                className="w-full h-full border-0"
                title={selectedDoc.fileName}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <Card className="p-8">
                  <CardContent className="flex flex-col items-center gap-4">
                    <FileText className="h-12 w-12 text-gray-400" />
                    <p className="text-gray-600">No document selected</p>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
