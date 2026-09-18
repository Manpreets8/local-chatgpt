import { useEffect, useRef, useState } from "react";

import { deleteDocument, listDocuments, uploadDocument } from "../services/api.js";

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function StatusBadge({ status }) {
  return <span className={`status-badge status-badge--${status}`}>{status}</span>;
}

export default function DocumentsPage({ onMenuClick }) {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const refresh = async () => {
    try {
      const data = await listDocuments();
      setDocuments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError("");
    try {
      await uploadDocument(file);
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (documentId) => {
    try {
      await deleteDocument(documentId);
      setDocuments((prev) => prev.filter((d) => d.id !== documentId));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="documents-page">
      <header className="chat-header">
        <button type="button" className="menu-button" onClick={onMenuClick} aria-label="Toggle conversations">
          ☰
        </button>
        <h1>Documents</h1>
      </header>

      <div className="documents-body">
        <div className="upload-area">
          <input
            ref={fileInputRef}
            type="file"
            id="document-upload-input"
            accept=".pdf,.txt,.docx"
            onChange={handleFileChange}
            disabled={isUploading}
            hidden
          />
          <label htmlFor="document-upload-input" className="upload-button">
            {isUploading ? "Uploading…" : "+ Upload Document"}
          </label>
          <span className="upload-hint">PDF, TXT, or DOCX — up to 10MB</span>
        </div>

        {error && <div className="documents-error">{error}</div>}

        {isLoading && <div className="chat-empty-state">Loading documents…</div>}

        {!isLoading && documents.length === 0 && (
          <div className="chat-empty-state">No documents uploaded yet.</div>
        )}

        {!isLoading && documents.length > 0 && (
          <table className="documents-table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Status</th>
                <th>Chunks</th>
                <th>Size</th>
                <th>Uploaded</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td className="documents-filename">
                    {doc.filename}
                    {doc.status === "failed" && doc.error_message && (
                      <div className="documents-error-detail">{doc.error_message}</div>
                    )}
                  </td>
                  <td>
                    <StatusBadge status={doc.status} />
                  </td>
                  <td>{doc.chunk_count}</td>
                  <td>{formatFileSize(doc.file_size_bytes)}</td>
                  <td>{new Date(doc.created_at).toLocaleString()}</td>
                  <td>
                    <button
                      type="button"
                      className="documents-delete-button"
                      onClick={() => handleDelete(doc.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
