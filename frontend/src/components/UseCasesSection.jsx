export default function UseCasesSection() {
  const useCases = [
    {
      icon: "🎓",
      title: "Education",
      description: "Visualize math and physics concepts for students — turn abstract equations into animated proofs they can actually see.",
      examples: ["Pythagorean theorem proof", "Sine wave behaviour", "Sorting algorithm steps"],
    },
    {
      icon: "🎥",
      title: "Content Creation",
      description: "Generate slick animated clips for YouTube explainers, social posts, or lecture slides without touching After Effects.",
      examples: ["Animated diagram for a video", "Neural network explainer", "Shape morphing B-roll"],
    },
    {
      icon: "🔬",
      title: "Research & Prototyping",
      description: "Quickly prototype mathematical visualizations to test how an idea looks before committing to a full production render.",
      examples: ["Function curve comparison", "Convergence animation", "Data structure walkthrough"],
    },
    {
      icon: "🖥️",
      title: "Presentations",
      description: "Replace static slide diagrams with short looping animations that make your audience actually pay attention.",
      examples: ["Quadratic formula reveal", "Graph of growth curves", "Geometric transformation"],
    },
  ];

  return (
    <section style={{ width: "100%", marginTop: 96, paddingBottom: 64 }}>
      {/* Header — consistent with other sections */}
      <div style={{ marginBottom: 40, paddingBottom: 20, borderBottom: "1px solid var(--border)" }}>
        <h2 style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 6 }}>
          <span style={{ color: "var(--accent-lt)" }}>◈</span> Use Cases
        </h2>
        <p style={{ fontSize: 18, color: "var(--text-dim)" }}>
          Who uses FrameForge and how
        </p>
      </div>

      {/* Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 20 }}>
        {useCases.map((uc) => (
          <div
            key={uc.title}
            style={{
              background: "rgba(14,16,26,0.75)",
              border: "1px solid var(--border)",
              borderRadius: 16,
              padding: "22px 24px",
              transition: "transform .2s ease, border-color .2s ease, box-shadow .2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-3px)";
              e.currentTarget.style.borderColor = "rgba(33,198,143,.35)";
              e.currentTarget.style.boxShadow = "0 12px 40px rgba(0,0,0,.35)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.borderColor = "var(--border)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            {/* Card header */}
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
              <span style={{ fontSize: 24 }}>{uc.icon}</span>
              <h3 style={{ fontSize: 16, fontWeight: 700, letterSpacing: "-0.01em", color: "rgba(255,255,255,.9)" }}>
                {uc.title}
              </h3>
            </div>

            {/* Description */}
            <p style={{ fontSize: 13, color: "rgba(255,255,255,.55)", lineHeight: 1.65, marginBottom: 16 }}>
              {uc.description}
            </p>

            {/* Example prompts */}
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {uc.examples.map((ex) => (
                <div
                  key={ex}
                  style={{
                    fontSize: 12,
                    color: "var(--accent-lt)",
                    background: "rgba(33,198,143,.07)",
                    border: "1px solid rgba(33,198,143,.15)",
                    borderRadius: 8,
                    padding: "5px 10px",
                    fontFamily: "monospace",
                  }}
                >
                  "{ex}"
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
