import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  const [sceneName, setSceneName] = useState("");
  const [error, setError] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [quality, setQuality] = useState("l"); // l, m, h, k

  const qualityOptions = [
    { value: "l", label: "Low (480p)", description: "Fast rendering" },
    { value: "m", label: "Medium (720p)", description: "Balanced" },
    { value: "h", label: "High (1080p)", description: "High quality" },
    { value: "k", label: "4K (2160p)", description: "Best quality" },
  ];

  const generateAnimation = async () => {
    // Validation
    if (!prompt.trim()) {
      setError("Please enter a prompt");
      return;
    }

    setLoading(true);
    setVideoUrl(null);
    setSceneName("");
    setError(null);
    setWarnings([]);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/generate-animation`,
        {
          prompt: prompt.trim(),
          quality: quality,
        },
        {
          timeout: 300000, // 5 minutes timeout
        }
      );

      const data = response.data;

      // Set video URL (prepend base URL if relative)
      const fullVideoUrl = data.video_url.startsWith("http")
        ? data.video_url
        : `${API_BASE_URL}${data.video_url}`;

      setVideoUrl(fullVideoUrl);
      setSceneName(data.scene_name);
      
      if (data.warnings && data.warnings.length > 0) {
        setWarnings(data.warnings);
      }

      console.log("Animation generated:", data);
    } catch (err) {
      console.error("Error:", err);

      // Extract error message
      let errorMessage = "Animation generation failed";

      if (err.response) {
        // Server responded with error
        const detail = err.response.data?.detail;

        if (typeof detail === "string") {
          errorMessage = detail;
        } else if (detail?.error) {
          errorMessage = detail.error;
          if (detail.details) {
            errorMessage += `: ${detail.details}`;
          }
          if (detail.validation_errors) {
            errorMessage += `\n\nValidation errors:\n- ${detail.validation_errors.join("\n- ")}`;
          }
        }
      } else if (err.request) {
        // Request made but no response
        errorMessage = "Server not responding. Please check if the backend is running.";
      } else {
        // Error setting up request
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading) {
      generateAnimation();
    }
  };

  const downloadVideo = () => {
    if (videoUrl) {
      // Create temporary link and trigger download
      const link = document.createElement("a");
      link.href = videoUrl;
      link.download = `${sceneName || "animation"}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="app-container">
      <div className="content">
        <header className="header">
          <h1>🎬 FrameForge</h1>
          <p className="subtitle">Generate Manim animations from text prompts</p>
        </header>

        <div className="input-section">
          <div className="input-group">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe your animation (e.g., 'blue circle that grows')"
              className="prompt-input"
              disabled={loading}
            />

            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
              className="quality-select"
              disabled={loading}
            >
              {qualityOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>

            <button
              onClick={generateAnimation}
              disabled={loading || !prompt.trim()}
              className="generate-button"
            >
              {loading ? "Rendering..." : "Generate"}
            </button>
          </div>

          <div className="quality-info">
            {qualityOptions.find((opt) => opt.value === quality)?.description}
          </div>
        </div>

        {loading && (
          <div className="loading-section">
            <div className="spinner"></div>
            <p>Generating animation...</p>
            <p className="loading-subtext">
              This may take 30-60 seconds depending on complexity
            </p>
          </div>
        )}

        {error && (
          <div className="error-section">
            <h3>❌ Error</h3>
            <pre className="error-message">{error}</pre>
          </div>
        )}

        {warnings.length > 0 && (
          <div className="warning-section">
            <h3>⚠️ Warnings</h3>
            <ul>
              {warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </div>
        )}

        {videoUrl && (
          <div className="video-section">
            <div className="video-header">
              <h3>✅ Animation Ready: {sceneName}</h3>
              <button onClick={downloadVideo} className="download-button">
                ⬇️ Download
              </button>
            </div>

            <video
              key={videoUrl}
              controls
              autoPlay
              className="video-player"
            >
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {!loading && !videoUrl && !error && (
          <div className="examples-section">
            <h3>Try these examples:</h3>
            <div className="example-buttons">
              <button
                onClick={() => setPrompt("blue circle that grows")}
                className="example-button"
              >
                Growing Circle
              </button>
              <button
                onClick={() => setPrompt("pythagorean theorem visualization")}
                className="example-button"
              >
                Pythagorean Theorem
              </button>
              <button
                onClick={() => setPrompt("bouncing red ball")}
                className="example-button"
              >
                Bouncing Ball
              </button>
              <button
                onClick={() => setPrompt("square morphs into circle")}
                className="example-button"
              >
                Shape Transformation
              </button>
            </div>
          </div>
        )}
      </div>

      <footer className="footer">
        <p>Powered by Manim & Groq AI</p>
      </footer>
    </div>
  );
}

export default App;