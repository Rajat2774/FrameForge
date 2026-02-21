export default function CapabilitiesSection() {
  const categories = [
    {
      title: "Geometry",
      color: "#60a5fa",
      glow: "rgba(96,165,250,.1)",
      border: "rgba(96,165,250,.2)",
      items: [
        "Growing / shrinking circles",
        "Square, triangle, polygon creation",
        "Shape transformations & morphing",
        "Fill, stroke, and color animations",
        "Rotation and scaling",
      ],
    },
    {
      title: "Graphs & Functions",
      color: "#34d399",
      glow: "rgba(52,211,153,.1)",
      border: "rgba(52,211,153,.2)",
      items: [
        "Plot any function (sin, cos, tan, log…)",
        "Parabolas and polynomial curves",
        "Multi-curve comparisons",
        "Axes with Text labels (LaTeX-free)",
        "Animated curve tracing",
      ],
    },
    {
      title: "Math & Equations",
      color: "#f59e0b",
      glow: "rgba(245,158,11,.1)",
      border: "rgba(245,158,11,.2)",
      items: [
        "Famous equations showcase",
        "Pythagorean theorem proof",
        "Quadratic formula step-by-step",
        "Euler's identity visualization",
        "Step-by-step equation reveals",
      ],
    },
    {
      title: "Animations & Motion",
      color: "#a78bfa",
      glow: "rgba(167,139,250,.1)",
      border: "rgba(167,139,250,.2)",
      items: [
        "Bouncing ball physics",
        "Fade in / out transitions",
        "Write and Create animations",
        "Object path following",
        "Simultaneous multi-object animation",
      ],
    },
    {
      title: "Diagrams & Structures",
      color: "#f87171",
      glow: "rgba(248,113,113,.1)",
      border: "rgba(248,113,113,.2)",
      items: [
        "Neural network diagrams",
        "Binary search visualization",
        "Sorting algorithm steps",
        "Tree and graph structures",
        "Labeled node-edge layouts",
      ],
    },
    {
      title: "Template Engine",
      color: "#21c68f",
      glow: "rgba(33,198,143,.1)",
      border: "rgba(33,198,143,.2)",
      items: [
        "Instant renders for common prompts",
        "LLM confirms template intent",
        "Falls back to AI for complex prompts",
        "9 built-in high-quality templates",
        "Zero generation time on cache hits",
      ],
    },
  ];

  const limitations = [
    { icon: "🔤", text: "No LaTeX — equations use plain Text rendering" },
    { icon: "📷", text: "No 3D scenes or camera movement" },
    { icon: "🖼️", text: "No image or external asset imports" },
    { icon: "🎵", text: "No audio or sound effects" },
    { icon: "📺", text: "Output fixed at 480p quality" },
  ];

  return (
    <section style={{ width: "100%", marginTop: 96, paddingBottom: 80 }}>
      {/* Header — matches CommunitySection style exactly */}
      <div
        style={{
          marginBottom: 40,
          paddingBottom: 20,
          borderBottom: "1px solid var(--border)",
        }}
      >
        <h2
          style={{
            fontSize: 32,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            marginBottom: 6,
          }}
        >
          <span style={{ color: "var(--accent-lt)" }}>⚙</span> Current
          Capabilities
        </h2>
        <p style={{ fontSize: 18, color: "var(--text-dim)" }}>
          What FrameForge can generate today
        </p>
      </div>

      {/* Capability Cards Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
          gap: 20,
          marginBottom: 48,
        }}
      >
        {categories.map((cat) => (
          <div
            key={cat.title}
            style={{
              background: cat.glow,
              border: `1px solid ${cat.border}`,
              borderRadius: 16,
              padding: "20px 24px",
              transition: "transform .2s ease, box-shadow .2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-3px)";
              e.currentTarget.style.boxShadow = `0 12px 40px ${cat.glow}`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                marginBottom: 16,
              }}
            >
              <span style={{ fontSize: 22 }}>{cat.icon}</span>
              <h3
                style={{
                  fontSize: 15,
                  fontWeight: 700,
                  color: cat.color,
                  letterSpacing: "-0.01em",
                }}
              >
                {cat.title}
              </h3>
            </div>
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {cat.items.map((item) => (
                <li
                  key={item}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 8,
                    fontSize: 13,
                    color: "rgba(255,255,255,.72)",
                    lineHeight: 1.5,
                    marginBottom: 8,
                  }}
                >
                  <span
                    style={{
                      color: cat.color,
                      fontSize: 10,
                      marginTop: 4,
                      flexShrink: 0,
                    }}
                  >
                    ●
                  </span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Limitations bar */}
      <div
        style={{
          background: "rgba(255,255,255,.03)",
          border: "1px solid var(--border)",
          borderRadius: 16,
          padding: "20px 28px",
        }}
      >
        <p
          style={{
            fontSize: 11,
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: ".1em",
            color: "rgba(255,255,255,.3)",
            marginBottom: 16,
          }}
        >
          Current Limitations
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px 32px" }}>
          {limitations.map((l) => (
            <div
              key={l.text}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                fontSize: 13,
                color: "rgba(255,255,255,.45)",
              }}
            >
              <span style={{ fontSize: 14 }}>{l.icon}</span>
              {l.text}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
