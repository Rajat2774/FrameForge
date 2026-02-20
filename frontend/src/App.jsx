import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import DotPattern from "./components/DotPattern";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const STEPS = [
  { key: "gen", label: "Generating animation code" },
  { key: "val", label: "Validating animation" },
  { key: "ren", label: "Rendering animation" },
];

const EXAMPLES = [
  { label: "Growing Circle", prompt: "blue circle that grows" },
  {
    label: "Pythagorean Theorem",
    prompt: "pythagorean theorem visualization",
  },
  { label: "Sine Wave", prompt: "plot sin(x)" },
  {
    label: "Shape Morph",
    prompt: "show a square transforming into a circle",
  },
  { label: "Bouncing Ball", prompt: "bouncing red ball animation" },
  { label: "Neural Network", prompt: "draw a neural network diagram" },
];

/* ══════════════════════════════════════════════════════════
   Star Rating Component
══════════════════════════════════════════════════════════ */
function StarRating({ value, onChange, size = 24, readonly = false }) {
  const [hover, setHover] = useState(0);
  return (
    <div style={{ display: "flex", gap: 4 }}>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => !readonly && onChange && onChange(star)}
          onMouseEnter={() => !readonly && setHover(star)}
          onMouseLeave={() => !readonly && setHover(0)}
          style={{
            background: "none",
            border: "none",
            cursor: readonly ? "default" : "pointer",
            padding: 2,
            fontSize: size,
            lineHeight: 1,
            color:
              (hover || value) >= star ? "#fbbf24" : "rgba(255,255,255,0.2)",
            transition: "color .15s, transform .15s",
            transform: !readonly && hover === star ? "scale(1.2)" : "scale(1)",
          }}
        >
          ★
        </button>
      ))}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════
   Toast Notification
══════════════════════════════════════════════════════════ */
function Toast({ message, type = "success", onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <div
      className="toast-notification"
      style={{
        position: "fixed",
        bottom: 32,
        right: 32,
        zIndex: 9999,
        padding: "14px 20px",
        borderRadius: 12,
        background:
          type === "success"
            ? "linear-gradient(135deg, rgba(52,211,153,.15), rgba(16,185,129,.1))"
            : "linear-gradient(135deg, rgba(248,113,113,.15), rgba(239,68,68,.1))",
        border: `1px solid ${type === "success" ? "rgba(52,211,153,.35)" : "rgba(248,113,113,.35)"}`,
        backdropFilter: "blur(20px)",
        color: type === "success" ? "#34d399" : "#f87171",
        fontSize: 14,
        fontWeight: 600,
        display: "flex",
        alignItems: "center",
        gap: 10,
        boxShadow: "0 8px 32px rgba(0,0,0,.4)",
        animation: "slideInRight .35s cubic-bezier(.34,1.56,.64,1) both",
        maxWidth: 360,
      }}
    >
      <span style={{ fontSize: 18 }}>{type === "success" ? "🎉" : "⚠️"}</span>
      {message}
      <button
        onClick={onClose}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          color: "inherit",
          marginLeft: 8,
          opacity: 0.7,
          fontSize: 16,
        }}
      >
        ×
      </button>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════
   Post Modal
══════════════════════════════════════════════════════════ */
function PostModal({ videoUrl, prompt, onClose, onSuccess }) {
  const [name, setName] = useState("");
  const [title, setTitle] = useState(prompt || "");
  const [rating, setRating] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return setErr("Name is required.");
    if (!title.trim()) return setErr("Title is required.");
    if (!rating) return setErr("Please select a star rating.");
    if (!videoUrl)
      return setErr("No animation to post. Please generate one first.");

    setErr("");
    setSubmitting(true);
    try {
      await axios.post(`${API}/posts`, {
        name: name.trim(),
        title: title.trim(),
        rating,
        video_url: videoUrl,
      });
      onSuccess();
    } catch (e) {
      setErr(
        e.response?.data?.detail || "Failed to save post. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  // Close on backdrop click
  const handleBackdrop = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div
      onClick={handleBackdrop}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 1000,
        background: "rgba(0,0,0,0.65)",
        backdropFilter: "blur(6px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
        animation: "fadeIn .2s ease both",
      }}
    >
      <div
        className="modal-card"
        style={{
          width: "100%",
          maxWidth: 520,
          background: "rgba(14,16,26,0.97)",
          border: "1px solid rgba(33,198,143,0.25)",
          borderRadius: 20,
          boxShadow:
            "0 24px 80px rgba(0,0,0,.7), 0 0 0 1px rgba(255,255,255,.04)",
          padding: 32,
          animation: "slideUp .35s cubic-bezier(.34,1.56,.64,1) both",
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 24,
          }}
        >
          <div>
            <h2
              style={{
                fontSize: 20,
                fontWeight: 700,
                letterSpacing: "-0.02em",
              }}
            >
              Share to Community 
            </h2>
            <p style={{ fontSize: 13, color: "var(--text-dim)", marginTop: 4 }}>
              Post your animation for everyone to see
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "rgba(255,255,255,.06)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              width: 32,
              height: 32,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              color: "var(--text-dim)",
              fontSize: 18,
              transition: "all .2s",
            }}
          >
            ×
          </button>
        </div>

        {/* Video Preview */}
        <div
          style={{
            marginBottom: 24,
            borderRadius: 12,
            overflow: "hidden",
            border: "1px solid var(--border)",
            background: "#000",
            aspectRatio: "16/9",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {videoUrl ? (
            <video
              src={videoUrl}
              autoPlay
              muted
              loop
              style={{
                width: "100%",
                height: "100%",
                objectFit: "contain",
                display: "block",
              }}
            />
          ) : (
            <span style={{ color: "var(--text-dim)", fontSize: 13 }}>
              No animation loaded
            </span>
          )}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Name */}
            <div>
              <label
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: "var(--text-dim)",
                  textTransform: "uppercase",
                  letterSpacing: ".06em",
                  display: "block",
                  marginBottom: 6,
                }}
              >
                Your Name *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Alex"
                maxLength={100}
                disabled={submitting}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  borderRadius: 10,
                  fontSize: 14,
                  background: "rgba(255,255,255,.05)",
                  border: "1px solid var(--border)",
                  color: "var(--text)",
                  outline: "none",
                  transition: "border .2s",
                }}
                onFocus={(e) => (e.target.style.borderColor = "var(--accent)")}
                onBlur={(e) => (e.target.style.borderColor = "var(--border)")}
              />
            </div>

            {/* Title */}
            <div>
              <label
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: "var(--text-dim)",
                  textTransform: "uppercase",
                  letterSpacing: ".06em",
                  display: "block",
                  marginBottom: 6,
                }}
              >
                Title *
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Give your animation a title"
                maxLength={200}
                disabled={submitting}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  borderRadius: 10,
                  fontSize: 14,
                  background: "rgba(255,255,255,.05)",
                  border: "1px solid var(--border)",
                  color: "var(--text)",
                  outline: "none",
                  transition: "border .2s",
                }}
                onFocus={(e) => (e.target.style.borderColor = "var(--accent)")}
                onBlur={(e) => (e.target.style.borderColor = "var(--border)")}
              />
            </div>

            {/* Rating */}
            <div>
              <label
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: "var(--text-dim)",
                  textTransform: "uppercase",
                  letterSpacing: ".06em",
                  display: "block",
                  marginBottom: 8,
                }}
              >
                Your Rating *
              </label>
              <StarRating value={rating} onChange={setRating} size={28} />
              {rating > 0 && (
                <p
                  style={{
                    fontSize: 11,
                    color: "var(--text-dim)",
                    marginTop: 6,
                  }}
                >
                  {["", "Poor", "Fair", "Good", "Great", "Excellent"][rating]} —{" "}
                  {rating}/5 stars
                </p>
              )}
            </div>

            {/* Error */}
            {err && (
              <div
                style={{
                  padding: "10px 14px",
                  borderRadius: 10,
                  fontSize: 13,
                  background: "rgba(248,113,113,.08)",
                  border: "1px solid rgba(248,113,113,.2)",
                  color: "#f87171",
                }}
              >
                {err}
              </div>
            )}

            {/* Buttons */}
            <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
              <button
                type="button"
                onClick={onClose}
                disabled={submitting}
                className="btn-ghost"
                style={{
                  flex: 1,
                  padding: "10px 16px",
                  borderRadius: 10,
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || !videoUrl}
                className="btn-primary"
                id="submit-post-btn"
                style={{
                  flex: 2,
                  padding: "10px 16px",
                  borderRadius: 10,
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                {submitting ? (
                  <span
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: 8,
                    }}
                  >
                    <svg
                      className="anim-spin"
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="3"
                        opacity=".25"
                      />
                      <path
                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                        fill="currentColor"
                        opacity=".75"
                      />
                    </svg>
                    Posting…
                  </span>
                ) : (
                  "Submit Post"
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════
   Community Post Card
══════════════════════════════════════════════════════════ */
function PostCard({ post }) {
  const videoRef = useRef(null);

  const formattedDate = post.created_at
    ? new Date(post.created_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "";

  return (
    <div
      className="post-card"
      style={{
        background: "rgba(14,16,26,0.85)",
        border: "1px solid var(--border)",
        borderRadius: 16,
        overflow: "hidden",
        transition:
          "transform .25s ease, border-color .25s ease, box-shadow .25s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.borderColor = "rgba(33,198,143,.4)";
        e.currentTarget.style.boxShadow =
          "0 16px 48px rgba(0,0,0,.4), 0 0 0 1px rgba(33,198,143,.1)";
        if (videoRef.current) videoRef.current.play();
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.borderColor = "var(--border)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      {/* Video */}
      <div
        style={{
          aspectRatio: "16/9",
          background: "#000",
          overflow: "hidden",
          position: "relative",
        }}
      >
        <video
          ref={videoRef}
          src={post.video_url}
          autoPlay
          muted
          loop
          playsInline
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            display: "block",
          }}
        />
        {/* Gradient overlay on bottom */}
        <div
          style={{
            position: "absolute",
            inset: "auto 0 0 0",
            height: 60,
            background: "linear-gradient(to top, rgba(8,9,14,.9), transparent)",
            pointerEvents: "none",
          }}
        />
      </div>

      {/* Info */}
      <div style={{ padding: "14px 16px 16px" }}>
        <h3
          style={{
            fontSize: 14,
            fontWeight: 700,
            color: "rgba(255,255,255,.9)",
            marginBottom: 6,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {post.title}
        </h3>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 8,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {/* Avatar chip */}
            <div
              style={{
                width: 22,
                height: 22,
                borderRadius: "50%",
                background: "linear-gradient(135deg, #21c68f, #6de6b5)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 11,
                fontWeight: 700,
                color: "#fff",
                flexShrink: 0,
              }}
            >
              {post.name.charAt(0).toUpperCase()}
            </div>
            <span
              style={{
                fontSize: 12,
                color: "var(--text-dim)",
                fontWeight: 500,
              }}
            >
              {post.name}
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <StarRating value={post.rating} readonly size={13} />
          </div>
        </div>
        {formattedDate && (
          <p
            style={{
              fontSize: 10,
              color: "rgba(255,255,255,.25)",
              marginTop: 8,
            }}
          >
            {formattedDate}
          </p>
        )}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════
   Community Section
══════════════════════════════════════════════════════════ */
function CommunitySection({ refreshKey }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPosts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.get(`${API}/posts`);
      setPosts(data.posts || []);
    } catch (e) {
      setError("Could not load community posts.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts, refreshKey]);

  return (
    <section style={{ width: "100%", marginTop: 64, paddingBottom: 64 }}>
      {/* Section Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 32,
          paddingBottom: 20,
          borderBottom: "1px solid var(--border)",
        }}
      >
        <div>
          <h2
            style={{
              fontSize: 32,
              fontWeight: 800,
              letterSpacing: "-0.02em",
              marginBottom: 6,
            }}
          >
            <span style={{ color: "var(--accent-lt)" }}>✦</span> Community
            Animations
          </h2>
          <p style={{ fontSize: 18, color: "var(--text-dim)" }}>
            AI-generated animations shared by the community
          </p>
        </div>
        <button
          onClick={fetchPosts}
          className="btn-ghost"
          style={{
            padding: "7px 14px",
            borderRadius: 9,
            fontSize: 12,
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <svg
            width="13"
            height="13"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Refresh
        </button>
      </div>

      {/* States */}
      {loading && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
            gap: 20,
          }}
        >
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              style={{
                borderRadius: 16,
                overflow: "hidden",
                border: "1px solid var(--border)",
                background: "rgba(14,16,26,0.85)",
              }}
            >
              <div className="skeleton" style={{ aspectRatio: "16/9" }} />
              <div style={{ padding: "14px 16px 16px" }}>
                <div
                  className="skeleton"
                  style={{
                    height: 14,
                    borderRadius: 7,
                    marginBottom: 10,
                    width: "80%",
                  }}
                />
                <div
                  className="skeleton"
                  style={{ height: 12, borderRadius: 6, width: "50%" }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && error && (
        <div
          style={{
            padding: "32px 24px",
            borderRadius: 16,
            textAlign: "center",
            border: "1px solid rgba(248,113,113,.15)",
            background: "rgba(248,113,113,.05)",
          }}
        >
          <p style={{ color: "#f87171", fontSize: 14, marginBottom: 12 }}>
            ⚠️ {error}
          </p>
          <button
            onClick={fetchPosts}
            className="btn-ghost"
            style={{ padding: "7px 16px", borderRadius: 8, fontSize: 12 }}
          >
            Try again
          </button>
        </div>
      )}

      {!loading && !error && posts.length === 0 && (
        <div
          style={{
            padding: "56px 24px",
            borderRadius: 16,
            textAlign: "center",
            border: "1px solid var(--border)",
            background: "rgba(14,16,26,0.5)",
          }}
        >
          <div style={{ fontSize: 40, marginBottom: 12 }}>🎬</div>
          <p
            style={{
              fontSize: 16,
              fontWeight: 600,
              color: "rgba(255,255,255,.7)",
              marginBottom: 8,
            }}
          >
            No community posts yet
          </p>
          <p style={{ fontSize: 13, color: "var(--text-dim)" }}>
            Generate an animation and be the first to share it!
          </p>
        </div>
      )}

      {!loading && !error && posts.length > 0 && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
            gap: 20,
          }}
        >
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </section>
  );
}

/* ══════════════════════════════════════════════════════════
   Main App
══════════════════════════════════════════════════════════ */
export default function App() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [videoUrl, setVideoUrl] = useState(null);
  const [sceneName, setSceneName] = useState("");
  const [code, setCode] = useState(null);
  const [error, setError] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const quality = "l"; // Fixed at 480p — quality selector removed
  const [showCode, setShowCode] = useState(false);
  const [copied, setCopied] = useState(false);
  const [templateUsed, setTemplateUsed] = useState(null);

  // Community state
  const [showPostModal, setShowPostModal] = useState(false);
  const [communityRefreshKey, setCommunityRefreshKey] = useState(0);
  const [toast, setToast] = useState(null);

  const inputRef = useRef(null);

  // Advance pipeline steps during loading
  useEffect(() => {
    if (!loading) return;
    const t1 = setTimeout(() => setStep(1), 3000);
    const t2 = setTimeout(() => setStep(2), 7000);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [loading]);

  const generate = async () => {
    const p = prompt.trim();
    if (!p) return;

    setLoading(true);
    setStep(0);
    setVideoUrl(null);
    setSceneName("");
    setCode(null);
    setError(null);
    setWarnings([]);
    setShowCode(false);
    setTemplateUsed(null);

    try {
      const { data } = await axios.post(
        `${API}/generate-animation`,
        { prompt: p, quality },
        { timeout: 130_000 },
      );

      if (data.status === "error") {
        setError({
          title:
            data.stage === "validation"
              ? "Animation type not supported yet"
              : data.stage === "rendering"
                ? "Rendering failed"
                : "Something went wrong",
          message: data.message,
          suggestion: data.suggestion,
          suggestions: data.suggestions || [],
          details: data.details,
        });
        return;
      }

      const url = data.video_url?.startsWith("http")
        ? data.video_url
        : `${API}${data.video_url}`;

      setVideoUrl(url);
      setSceneName(data.scene_name);
      setCode(data.code || null);
      setTemplateUsed(data.template_used || null);
      if (data.warnings?.length) setWarnings(data.warnings);
    } catch (err) {
      console.error("Error:", err);

      if (err.code === "ECONNABORTED" || err.message?.includes("timeout")) {
        setError({
          title: "Request timed out",
          message: "The animation took too long to generate or render.",
          suggestion: "Try a simpler prompt with fewer elements.",
          suggestions: [
            "blue circle that grows",
            "plot sin(x)",
            "show a square transforming into a circle",
          ],
        });
        return;
      }

      let errObj = {
        title: "Something went wrong",
        message: "Animation generation failed.",
        suggestion: "Try a simpler prompt.",
        suggestions: [],
      };

      if (err.response) {
        const d = err.response.data;
        if (d?.status === "error") {
          errObj = {
            title:
              d.stage === "validation"
                ? "Animation type not supported yet"
                : d.stage === "rendering"
                  ? "Rendering failed"
                  : "Something went wrong",
            message: d.message || errObj.message,
            suggestion: d.suggestion || errObj.suggestion,
            suggestions: d.suggestions || [],
            details: d.details,
          };
        } else if (typeof d?.detail === "string") {
          errObj.message = d.detail;
        }
      } else if (err.request) {
        errObj.title = "Server unreachable";
        errObj.message =
          "Cannot connect to the backend. Make sure the server is running on port 8000.";
      }

      setError(errObj);
    } finally {
      setLoading(false);
      setStep(0);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !loading) generate();
  };

  const download = async () => {
    if (!videoUrl) return;
    try {
      const response = await fetch(videoUrl);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = blobUrl;
      a.download = `${sceneName || "animation"}.mp4`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error("Download failed:", err);
      window.open(videoUrl, "_blank");
    }
  };

  const copyCode = () => {
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePostSuccess = () => {
    setShowPostModal(false);
    setToast({
      message: "Animation posted to the community! 🎉",
      type: "success",
    });
    // Refresh community feed
    setCommunityRefreshKey((k) => k + 1);
  };

  /* ─── JSX ───────────────────────────────────────────────────────────── */
  return (
    <>
      {/* ── Dot-pattern fixed background ─────────────────────────────── */}
      <DotPattern
        dotSize={2}
        gap={26}
        baseColor="#2a2a3a" /* dark dots on black backdrop */
        glowColor="#00ff99" /* cyan‑green when hovering/mouse‑near */
        proximity={130}
        glowIntensity={1.1}
        waveSpeed={0.4}
        className=""
      />

      {/* ── App shell (sits above DotPattern via stacking context) ───── */}
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          position: "relative",
          zIndex: 1,
        }}
      >
        {/* ── Navbar ─────────────────────────────────────────────────────── */}
        <Navbar />

        {/* ── Main body ──────────────────────────────────────────────────── */}
        <main
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: "92px 20px 60px",
            overflowY: "auto",
          }}
        >
          <div style={{ width: "100%", maxWidth: "none", padding: "0 20px" }}>
            {/* ── Hero (idle state) ─────────────────────────────────────── */}
            {!videoUrl && !error && !loading && (
              <div
                className="anim-up"
                style={{ textAlign: "center", marginBottom: 40, marginTop: 24 }}
              >
                <h1
                  style={{
                    fontSize: "clamp(80px, 12vw, 120px)",
                    fontWeight: 900,
                    letterSpacing: "-0.04em",
                    marginBottom: 18,
                    lineHeight: 1.0,
                  }}
                >
                  <span className="logo-grad">FrameForge</span>
                </h1>
                <p
                  style={{
                    color: "rgba(255,255,255,0.88)",
                    fontSize: "clamp(20px, 3vw, 26px)",
                    maxWidth: 480,
                    margin: "0 auto",
                    lineHeight: 1.65,
                    fontWeight: 400,
                    letterSpacing: "0.005em",
                  }}
                >
                  Describe any animation in plain English and watch AI bring it
                  to life with Manim.
                </p>
              </div>
            )}

            {/* ── Prompt bar ───────────────────────────────────────────── */}
            <div
              className="glass prompt-container"
              style={{
                padding: 6,
                marginBottom: 24,
                display: "flex",
                alignItems: "center",
                gap: 6,
                flexWrap: "wrap",
              }}
            >
              {/* Icon */}
              <div
                style={{
                  paddingLeft: 12,
                  color: "var(--accent-lt)",
                  display: "flex",
                  flexShrink: 0,
                }}
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                </svg>
              </div>

              <input
                ref={inputRef}
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={handleKey}
                placeholder="Describe your animation…"
                disabled={loading}
                className="input-field"
                id="prompt-input"
                style={{ flex: 1, padding: "16px 12px", fontSize: 16 }}
              />

              <button
                onClick={generate}
                disabled={loading || !prompt.trim()}
                id="generate-btn"
                style={{
                  padding: "14px 24px",
                  borderRadius: 10,
                  fontSize: 15,
                  fontWeight: 700,
                  flexShrink: 0,
                  background: "#28FFB7",
                  color: "#000",
                  border: "none",
                  cursor: loading || !prompt.trim() ? "not-allowed" : "pointer",
                  transition: "transform .2s, box-shadow .2s, background .2s",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
                onMouseEnter={(e) => {
                  if (!loading && prompt.trim()) {
                    e.currentTarget.style.transform = "translateY(-1px)";
                    e.currentTarget.style.boxShadow =
                      "0 6px 24px rgba(0,0,0,.2)";
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                {loading ? (
                  <span
                    style={{ display: "flex", alignItems: "center", gap: 6 }}
                  >
                    <svg
                      className="anim-spin"
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="3"
                        opacity=".25"
                      />
                      <path
                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                        fill="currentColor"
                        opacity=".75"
                      />
                    </svg>
                    Working…
                  </span>
                ) : (
                  "Generate"
                )}
              </button>

              {/* Post Button */}
              <button
                onClick={() => setShowPostModal(true)}
                disabled={!videoUrl || loading}
                id="post-btn"
                style={{
                  padding: "14px 22px",
                  borderRadius: 10,
                  fontSize: 15,
                  fontWeight: 600,
                  flexShrink: 0,
                  cursor: videoUrl && !loading ? "pointer" : "not-allowed",
                  background:
                    videoUrl && !loading
                      ? "linear-gradient(135deg, rgba(33,198,143,.2), rgba(109,230,181,.15))"
                      : "rgba(255,255,255,.04)",
                  border: `1px solid ${videoUrl && !loading ? "rgba(33,198,143,.5)" : "var(--border)"}`,
                  color:
                    videoUrl && !loading
                      ? "var(--accent-lt)"
                      : "rgba(255,255,255,.2)",
                  transition: "all .25s ease",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
                onMouseEnter={(e) => {
                  if (videoUrl && !loading) {
                    e.currentTarget.style.background =
                      "linear-gradient(135deg, rgba(33,198,143,.3), rgba(109,230,181,.25))";
                    e.currentTarget.style.transform = "translateY(-1px)";
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background =
                    videoUrl && !loading
                      ? "linear-gradient(135deg, rgba(33,198,143,.2), rgba(109,230,181,.15))"
                      : "rgba(255,255,255,.04)";
                  e.currentTarget.style.transform = "translateY(0)";
                }}
              >
                <svg
                  width="13"
                  height="13"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                Post
              </button>
            </div>

            {/* ── Pipeline loading ──────────────────────────────────────── */}
            {loading && (
              <div
                className="glass anim-in"
                style={{ padding: 24, marginBottom: 24 }}
              >
                <div
                  style={{ display: "flex", flexDirection: "column", gap: 16 }}
                >
                  {STEPS.map((s, i) => (
                    <div
                      key={s.key}
                      style={{ display: "flex", alignItems: "center", gap: 12 }}
                    >
                      <div
                        className={`step-dot ${step > i ? "done" : step === i ? "active" : "pending"}`}
                      />
                      <span
                        style={{
                          fontSize: 13,
                          transition: "color .3s",
                          color:
                            step >= i
                              ? "rgba(255,255,255,.85)"
                              : "rgba(255,255,255,.25)",
                        }}
                      >
                        {s.label}
                      </span>
                      <span style={{ marginLeft: "auto", fontSize: 11 }}>
                        {step > i && (
                          <span style={{ color: "var(--success)" }}>✓</span>
                        )}
                        {step === i && (
                          <span style={{ color: "var(--accent-lt)" }}>
                            in progress
                          </span>
                        )}
                      </span>
                    </div>
                  ))}
                </div>
                <p
                  style={{
                    fontSize: 11,
                    color: "var(--text-dim)",
                    textAlign: "center",
                    marginTop: 20,
                  }}
                >
                  Typically takes 30–60 seconds depending on complexity
                </p>
              </div>
            )}

            {/* ── Error panel ───────────────────────────────────────────── */}
            {error && (
              <div
                className="glass anim-up"
                style={{
                  padding: 20,
                  marginBottom: 24,
                  borderColor: "rgba(248,113,113,.15)",
                }}
              >
                <div
                  style={{ display: "flex", gap: 12, alignItems: "flex-start" }}
                >
                  <div
                    style={{
                      width: 34,
                      height: 34,
                      borderRadius: "50%",
                      background: "rgba(248,113,113,.1)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                    }}
                  >
                    <svg
                      width="16"
                      height="16"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="#f87171"
                      strokeWidth="2"
                    >
                      <circle cx="12" cy="12" r="10" />
                      <path d="M12 8v4m0 4h.01" />
                    </svg>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3
                      style={{
                        fontSize: 14,
                        fontWeight: 600,
                        color: "var(--danger)",
                        marginBottom: 4,
                      }}
                    >
                      {error.title}
                    </h3>
                    <p
                      style={{
                        fontSize: 13,
                        color: "rgba(255,255,255,.65)",
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-word",
                      }}
                    >
                      {error.message}
                    </p>
                    {error.suggestion && (
                      <p
                        style={{
                          fontSize: 12,
                          color: "var(--accent-lt)",
                          marginTop: 8,
                          display: "flex",
                          gap: 6,
                          alignItems: "flex-start",
                        }}
                      >
                        <span>💡</span>
                        <span>{error.suggestion}</span>
                      </p>
                    )}
                    {error.details && (
                      <details style={{ marginTop: 10 }}>
                        <summary
                          style={{
                            fontSize: 11,
                            color: "var(--text-dim)",
                            cursor: "pointer",
                          }}
                        >
                          Technical details
                        </summary>
                        <pre
                          style={{
                            fontSize: 11,
                            color: "var(--text-dim)",
                            marginTop: 6,
                            whiteSpace: "pre-wrap",
                            wordBreak: "break-all",
                          }}
                        >
                          {error.details}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
                {error.suggestions?.length > 0 && (
                  <div
                    style={{
                      marginTop: 16,
                      paddingTop: 14,
                      borderTop: "1px solid var(--border)",
                    }}
                  >
                    <p
                      style={{
                        fontSize: 11,
                        color: "var(--text-dim)",
                        marginBottom: 10,
                      }}
                    >
                      Try one of these instead:
                    </p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {error.suggestions.map((s, i) => (
                        <button
                          key={i}
                          className="chip"
                          onClick={() => {
                            setPrompt(s);
                            setError(null);
                          }}
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── Warnings ─────────────────────────────────────────────── */}
            {warnings.length > 0 && (
              <div
                className="glass anim-in"
                style={{
                  padding: 16,
                  marginBottom: 24,
                  borderColor: "rgba(251,191,36,.12)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    marginBottom: 8,
                  }}
                >
                  <span style={{ fontSize: 14 }}>⚠️</span>
                  <span
                    style={{
                      fontSize: 13,
                      fontWeight: 600,
                      color: "var(--warn)",
                    }}
                  >
                    Warnings
                  </span>
                </div>
                {warnings.map((w, i) => (
                  <p
                    key={i}
                    style={{
                      fontSize: 12,
                      color: "rgba(255,255,255,.55)",
                      paddingLeft: 22,
                      marginTop: 4,
                    }}
                  >
                    • {w}
                  </p>
                ))}
              </div>
            )}

            {/* ── Video preview card ────────────────────────────────────── */}
            {videoUrl && (
              <div
                className="glass anim-up"
                style={{ padding: 16, marginBottom: 24 }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: 12,
                    flexWrap: "wrap",
                    gap: 8,
                  }}
                >
                  <div>
                    <h3 style={{ fontSize: 14, fontWeight: 600 }}>
                      🎬 Animation Ready
                    </h3>
                    <p
                      style={{
                        fontSize: 11,
                        color: "var(--text-dim)",
                        marginTop: 2,
                      }}
                    >
                      {sceneName}
                    </p>
                    {templateUsed && (
                      <span
                        style={{
                          display: "inline-block",
                          marginTop: 4,
                          fontSize: 10,
                          fontWeight: 600,
                          color: "var(--success)",
                          background: "rgba(52,211,153,.1)",
                          border: "1px solid rgba(52,211,153,.2)",
                          borderRadius: 999,
                          padding: "2px 8px",
                        }}
                      >
                        ⚡ Template: {templateUsed}
                      </span>
                    )}
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    {code && (
                      <button
                        className="btn-ghost"
                        onClick={() => setShowCode((v) => !v)}
                        style={{
                          padding: "5px 12px",
                          borderRadius: 8,
                          fontSize: 12,
                        }}
                        id="toggle-code-btn"
                      >
                        {showCode ? "Hide Code" : "View Code"}
                      </button>
                    )}
                    <button
                      className="btn-ghost"
                      onClick={download}
                      style={{
                        padding: "5px 12px",
                        borderRadius: 8,
                        fontSize: 12,
                        display: "flex",
                        alignItems: "center",
                        gap: 5,
                      }}
                      id="download-btn"
                    >
                      <svg
                        width="13"
                        height="13"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V3"
                        />
                      </svg>
                      Download
                    </button>
                  </div>
                </div>

                <video
                  key={videoUrl}
                  controls
                  autoPlay
                  muted
                  style={{
                    width: "100%",
                    maxWidth: 640,
                    display: "block",
                    margin: "0 auto",
                    borderRadius: "var(--radius-sm)",
                  }}
                  id="video-player"
                >
                  <source src={videoUrl} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>

                {showCode && code && (
                  <div className="anim-in" style={{ marginTop: 16 }}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginBottom: 8,
                      }}
                    >
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 600,
                          textTransform: "uppercase",
                          letterSpacing: ".06em",
                          color: "var(--text-dim)",
                        }}
                      >
                        Generated Manim Code
                      </span>
                      <button
                        onClick={copyCode}
                        style={{
                          background: "none",
                          border: "none",
                          color: copied ? "var(--success)" : "var(--text-dim)",
                          fontSize: 11,
                          cursor: "pointer",
                          transition: "color .2s",
                        }}
                      >
                        {copied ? "✓ Copied" : "Copy"}
                      </button>
                    </div>
                    <pre className="code-block">{code}</pre>
                  </div>
                )}
              </div>
            )}

            {/* ── Examples (idle) ───────────────────────────────────────── */}
            {!loading && !videoUrl && !error && (
              <div
                id="examples"
                className="anim-in"
                style={{ textAlign: "center" }}
              >
                <p
                  style={{
                    fontSize: 18,
                    color: "var(--text-dim)",
                    marginBottom: 14,
                  }}
                >
                  Try an example prompt
                </p>
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    justifyContent: "center",
                    gap: 8,
                  }}
                >
                  {EXAMPLES.map((ex) => (
                    <button
                      key={ex.prompt}
                      className="chip"
                      onClick={() => setPrompt(ex.prompt)}
                    >
                      {ex.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* ── Community Section (always visible below) ──────────────── */}
            <CommunitySection refreshKey={communityRefreshKey} />
          </div>
        </main>

        {/* ── Footer ─────────────────────────────────────────────────────── */}
        <Footer />

        {/* ── Post Modal ─────────────────────────────────────────────────── */}
        {showPostModal && (
          <PostModal
            videoUrl={videoUrl}
            prompt={prompt}
            onClose={() => setShowPostModal(false)}
            onSuccess={handlePostSuccess}
          />
        )}

        {/* ── Toast ──────────────────────────────────────────────────────── */}
        {toast && (
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast(null)}
          />
        )}
      </div>
    </>
  );
}
