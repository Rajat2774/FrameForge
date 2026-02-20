import { useState, useEffect } from "react";
import logoImg from "../assets/frameforge.png";

const NAV_LINKS = [
  {
    label: "Examples",
    href: "#examples",
    scroll: true,
  },
  {
    label: "Docs",
    href: "https://docs.manim.community/en/stable/",
    external: true,
  },
  {
    label: "Contact",
    href: "#footer",
    scroll: true,
  },
];

function Logo() {
  return (
    <a
      href="/"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        textDecoration: "none",
      }}
    >
      <img
        src={logoImg}
        alt="FrameForge"
        style={{
          width: 34,
          height: 34,
          objectFit: "contain",
        }}
      />
      <span
        style={{
          fontSize: 17,
          fontWeight: 800,
          letterSpacing: "-0.03em",
          color: "rgba(255,255,255,.92)",
        }}
      >
        FrameForge
      </span>
    </a>
  );
}

function NavLink({ link, onClick }) {
  const handleClick = (e) => {
    if (link.scroll) {
      e.preventDefault();
      const target = document.querySelector(link.href);
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }
    onClick?.();
  };

  return (
    <a
      href={link.href}
      target={link.external ? "_blank" : undefined}
      rel={link.external ? "noopener noreferrer" : undefined}
      onClick={handleClick}
      className="nav-link"
      style={{
        fontSize: 13,
        fontWeight: 500,
        color: "rgba(255,255,255,.65)",
        textDecoration: "none",
        padding: "6px 12px",
        borderRadius: 8,
        transition: "color .2s, background .2s",
        display: "flex",
        alignItems: "center",
        gap: 5,
        whiteSpace: "nowrap",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.color = "rgba(255,255,255,.95)";
        e.currentTarget.style.background = "rgba(255,255,255,.06)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.color = "rgba(255,255,255,.65)";
        e.currentTarget.style.background = "transparent";
      }}
    >
      {link.label}
      {link.external && (
        <svg
          width="10"
          height="10"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2.5"
          style={{ opacity: 0.5 }}
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

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Close menu on resize to desktop
  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth > 640) setMenuOpen(false);
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return (
    <>
      <nav
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 500,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          height: 60,
          background: scrolled ? "rgba(8,9,14,0.90)" : "rgba(8,9,14,0.65)",
          backdropFilter: "blur(20px) saturate(1.2)",
          WebkitBackdropFilter: "blur(20px) saturate(1.2)",
          borderBottom: scrolled
            ? "1px solid rgba(255,255,255,.08)"
            : "1px solid rgba(255,255,255,.04)",
          transition:
            "background .3s ease, border-color .3s ease, box-shadow .3s ease",
          boxShadow: scrolled ? "0 4px 32px rgba(0,0,0,.35)" : "none",
        }}
      >
        {/* Left — Logo */}
        <Logo />

        {/* Center/Right — Desktop nav links */}
        <div
          className="nav-desktop-links"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 2,
          }}
        >
          {NAV_LINKS.map((link) => (
            <NavLink key={link.label} link={link} />
          ))}

          {/* CTA pill */}
          <a
            href="https://github.com/Rajat2774/FrameForge"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              marginLeft: 10,
              display: "flex",
              alignItems: "center",
              gap: 7,
              padding: "7px 16px",
              borderRadius: 999,
              fontSize: 12,
              fontWeight: 700,
              color: "#000",
              background: "#28FFB7",
              /* remove gradient for solid green */
              textDecoration: "none",
              boxShadow: "0 3px 16px rgba(33,198,143,.35)",
              transition: "transform .2s, box-shadow .2s",
              letterSpacing: "0.01em",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-1px)";
              e.currentTarget.style.boxShadow =
                "0 6px 24px rgba(33,198,143,.5)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow =
                "0 3px 16px rgba(33,198,143,.35)";
            }}
          >
            {/* GitHub icon */}
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.605-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12" />
            </svg>
            GitHub
          </a>
        </div>

        {/* Hamburger — mobile only */}
        <button
          onClick={() => setMenuOpen((v) => !v)}
          className="nav-hamburger"
          aria-label="Toggle menu"
          style={{
            display: "none",
            background: "rgba(255,255,255,.05)",
            border: "1px solid rgba(255,255,255,.1)",
            borderRadius: 8,
            padding: "6px 8px",
            cursor: "pointer",
            color: "rgba(255,255,255,.8)",
            transition: "background .2s",
          }}
        >
          {menuOpen ? (
            <svg
              width="18"
              height="18"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          ) : (
            <svg
              width="18"
              height="18"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          )}
        </button>
      </nav>

      {/* Mobile Dropdown Menu */}
      {menuOpen && (
        <div
          className="nav-mobile-menu"
          style={{
            position: "fixed",
            top: 60,
            left: 0,
            right: 0,
            zIndex: 490,
            background: "rgba(8,9,14,.97)",
            backdropFilter: "blur(20px)",
            borderBottom: "1px solid rgba(255,255,255,.07)",
            padding: "12px 20px 20px",
            display: "flex",
            flexDirection: "column",
            gap: 4,
            animation: "slideDown .25s cubic-bezier(.16,1,.3,1) both",
          }}
        >
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.label}
              link={link}
              onClick={() => setMenuOpen(false)}
            />
          ))}
          <div
            style={{
              marginTop: 8,
              paddingTop: 12,
              borderTop: "1px solid rgba(255,255,255,.06)",
            }}
          >
            <a
              href="https://github.com/Rajat2774/FrameForge"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 7,
                padding: "9px 16px",
                borderRadius: 10,
                fontSize: 13,
                fontWeight: 700,
                color: "#000",
                background: "#28FFB7",
                textDecoration: "none",
                justifyContent: "center",
              }}
              onClick={() => setMenuOpen(false)}
            >
              <svg
                width="13"
                height="13"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.605-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12c0-6.63-5.37-12-12-12" />
              </svg>
              GitHub
            </a>
          </div>
        </div>
      )}
    </>
  );
}
