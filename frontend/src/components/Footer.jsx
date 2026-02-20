import logoImg from "../assets/frameforge.png";

const QUICK_LINKS = [
  { label: "Examples", href: "#examples", scroll: true },
  {
    label: "Docs",
    href: "https://docs.manim.community/en/stable/",
    external: true,
  },
  { label: "Contact", href: "#footer", scroll: true },
];

const SOCIAL_LINKS = [
  {
    label: "GitHub",
    href: "https://github.com/Rajat2774/FrameForge",
    color: "#e2e8f0",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.605-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12" />
      </svg>
    ),
  },
  {
    label: "LinkedIn",
    href: "https://www.linkedin.com/in/rajat-singh-6558aa294",
    color: "#60a5fa",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
      </svg>
    ),
  },
  {
    label: "X / Twitter",
    href: "https://x.com/RAJAT_073",
    color: "#94a3b8",
    icon: (
      <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
      </svg>
    ),
  },
  {
    label: "Email",
    href: "rajatsingh2774@gmail.com",
    color: "#a78bfa",
    icon: (
      <svg
        width="18"
        height="18"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
        />
      </svg>
    ),
  },
];

function FooterLink({ link }) {
  const handleClick = (e) => {
    if (link.scroll) {
      e.preventDefault();
      const target = document.querySelector(link.href);
      if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <a
      href={link.href}
      target={link.external ? "_blank" : undefined}
      rel={link.external ? "noopener noreferrer" : undefined}
      onClick={handleClick}
      style={{
        fontSize: 13,
        color: "rgba(255,255,255,.45)",
        textDecoration: "none",
        transition: "color .2s",
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
      }}
      onMouseEnter={(e) =>
        (e.currentTarget.style.color = "rgba(255,255,255,.85)")
      }
      onMouseLeave={(e) =>
        (e.currentTarget.style.color = "rgba(255,255,255,.45)")
      }
    >
      {link.label}
      {link.external && (
        <svg
          width="9"
          height="9"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2.5"
          style={{ opacity: 0.45 }}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6m0 0v6m0-6L10 14"
          />
        </svg>
      )}
    </a>
  );
}

function SocialIcon({ link }) {
  return (
    <a
      href={link.href}
      target="_blank"
      rel="noopener noreferrer"
      title={link.label}
      style={{
        width: 38,
        height: 38,
        borderRadius: 10,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(255,255,255,.05)",
        border: "1px solid rgba(255,255,255,.08)",
        color: "rgba(255,255,255,.45)",
        textDecoration: "none",
        transition: "all .2s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.color = link.color;
        e.currentTarget.style.background = "rgba(255,255,255,.09)";
        e.currentTarget.style.borderColor = "rgba(255,255,255,.16)";
        e.currentTarget.style.transform = "translateY(-2px) scale(1.08)";
        e.currentTarget.style.boxShadow = `0 6px 20px rgba(0,0,0,.3)`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.color = "rgba(255,255,255,.45)";
        e.currentTarget.style.background = "rgba(255,255,255,.05)";
        e.currentTarget.style.borderColor = "rgba(255,255,255,.08)";
        e.currentTarget.style.transform = "translateY(0) scale(1)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      {link.icon}
    </a>
  );
}

export default function Footer() {
  return (
    <footer
      id="footer"
      style={{
        borderTop: "1px solid rgba(255,255,255,.06)",
        background: "rgba(5,6,10,0.95)",
        backdropFilter: "blur(20px)",
        padding: "48px 24px 28px",
        flexShrink: 0,
      }}
    >
      {/* Gradient top border line */}
      <div
        style={{
          height: 1,
          background:
            "linear-gradient(90deg, transparent, rgba(33,198,143,.35) 30%, rgba(109,230,181,.35) 70%, transparent)",
          marginBottom: 48,
          marginTop: -48,
        }}
      />

      <div
        style={{
          maxWidth: 1120,
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "40px 32px",
          marginBottom: 40,
        }}
      >
        {/* ── Left — Branding ── */}
        <div style={{ gridColumn: "span 1" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              marginBottom: 14,
            }}
          >
            <img
              src={logoImg}
              alt="FrameForge"
              style={{
                width: 32,
                height: 32,
                objectFit: "contain",
              }}
            />
            <span
              style={{
                fontSize: 16,
                fontWeight: 800,
                letterSpacing: "-0.025em",
                color: "rgba(255,255,255,.9)",
              }}
            >
              FrameForge
            </span>
          </div>
          <p
            style={{
              fontSize: 13,
              color: "rgba(255,255,255,.35)",
              lineHeight: 1.65,
              maxWidth: 220,
            }}
          >
            AI-Powered Animation Generation
            <br />
            Powered by Manim &amp; Groq AI
          </p>
          {/* Badge */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              marginTop: 16,
              padding: "5px 12px",
              borderRadius: 999,
              background: "rgba(33,198,143,.08)",
              border: "1px solid rgba(33,198,143,.2)",
              fontSize: 11,
              color: "var(--accent-lt)",
              fontWeight: 600,
            }}
          >
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: "#34d399",
                display: "inline-block",
                boxShadow: "0 0 6px rgba(52,211,153,.6)",
              }}
            />
            Open Source · v2.2
          </div>
        </div>

        {/* ── Center — Quick Links ── */}
        <div>
          <p
            style={{
              fontSize: 10,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: "rgba(255,255,255,.25)",
              marginBottom: 16,
            }}
          >
            Quick Links
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {QUICK_LINKS.map((link) => (
              <FooterLink key={link.label} link={link} />
            ))}
          </div>
        </div>

        {/* ── Right — Social Icons ── */}
        <div>
          <p
            style={{
              fontSize: 10,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: "rgba(255,255,255,.25)",
              marginBottom: 16,
            }}
          >
            Connect
          </p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {SOCIAL_LINKS.map((link) => (
              <SocialIcon key={link.label} link={link} />
            ))}
          </div>
        </div>
      </div>

      {/* ── Bottom bar ── */}
      <div
        style={{
          maxWidth: 1120,
          margin: "0 auto",
          paddingTop: 20,
          borderTop: "1px solid rgba(255,255,255,.05)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <p style={{ fontSize: 11, color: "rgba(255,255,255,.18)" }}>
          © 2025 FrameForge. All rights reserved.
        </p>
        <p style={{ fontSize: 11, color: "rgba(255,255,255,.18)" }}>
          Built using Manim, Groq &amp; React
        </p>
      </div>
    </footer>
  );
}
