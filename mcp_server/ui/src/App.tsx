import { useState } from "react";
import "./App.css";

type EmailResult = {
  subject?: string;
  email?: string;
  error?: string;
};

function AppUI() {
  const [tone, setTone] = useState("");
  const [context, setContext] = useState("");
  const [dataPoints, setDataPoints] = useState("");

  const [subject, setSubject] = useState("");
  const [email, setEmail] = useState("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleGenerateEmail = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const res = await fetch("/api/generate-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tone,
          context,
          data_points: dataPoints
            .split("\n")
            .map((item) => item.trim())
            .filter(Boolean),
        }),
      });

      const result: EmailResult = await res.json();

      if (result.error) {
        setError(result.error);
        return;
      }

      setSubject(result.subject ?? "");
      setEmail(result.email ?? "");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to generate email.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    setMessage("");
    setError("");

    try {
      const res = await fetch("/api/approve-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, email }),
      });

      const result = await res.json();
      setMessage(result.message || result.result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to approve email.",
      );
    }
  };

  const handleReject = async () => {
    setMessage("");
    setError("");

    try {
      const res = await fetch("/api/reject-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, email }),
      });

      const result = await res.json();
      setMessage(result.message || result.result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to reject email.",
      );
    }
  };

  return (
    <div className="app">
      <div className="container">
        <h1>Email Generator</h1>

        <p className="description">
          Generate, review, modify, and approve a professional email.
        </p>

        <div className="form">
          <label htmlFor="tone">Tone</label>

          <select
            id="tone"
            value={tone}
            onChange={(event) => setTone(event.target.value)}
          >
            <option value="">Select tone</option>
            <option value="formal">Formal</option>
            <option value="empathetic">Empathetic</option>
            <option value="assertive">Assertive</option>
            <option value="friendly">Friendly</option>
          </select>

          <label htmlFor="context">Context</label>

          <textarea
            id="context"
            rows={3}
            placeholder="Enter the background/context..."
            value={context}
            onChange={(event) => setContext(event.target.value)}
          />

          <label htmlFor="dataPoints">
            Data Points
          </label>

          <textarea
            id="dataPoints"
            rows={4}
            placeholder="Enter one data point per line..."
            value={dataPoints}
            onChange={(event) => setDataPoints(event.target.value)}
          />

          <button
            className="btn btn-primary"
            onClick={handleGenerateEmail}
            disabled={loading}
          >
            {loading ? <><span className="spinner" />Generating...</> : "Generate Email"}
          </button>
        </div>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {(subject || email) && (
          <div className="email-result">
            <h2>Generated Email</h2>

            <label htmlFor="subject">Subject</label>

            <input
              id="subject"
              value={subject}
              onChange={(event) =>
                setSubject(event.target.value)
              }
            />

            <label htmlFor="email">Email</label>

            <textarea
              id="email"
              rows={15}
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
            />

            <div className="actions">
              <button className="btn btn-approve" onClick={handleApprove}>
                Approve & Send
              </button>

              <button className="btn btn-reject" onClick={handleReject}>
                Reject
              </button>
            </div>
          </div>
        )}

        {message && (
          <div className="message">
            {message}
          </div>
        )}
      </div>
    </div>
  );
}

export default AppUI;