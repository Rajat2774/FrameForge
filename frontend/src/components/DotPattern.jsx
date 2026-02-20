import { useCallback, useEffect, useMemo, useRef } from "react";
import { cn } from "../lib/utils";

function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : { r: 0, g: 0, b: 0 };
}

export function DotPattern({
  className,
  children,
  dotSize = 2,
  gap = 24,
  baseColor = "#404040",
  glowColor = "#00ff99", // cyan-green hover color
  proximity = 120,
  glowIntensity = 1,
  waveSpeed = 0.5,
}) {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const dotsRef = useRef([]);
  const mouseRef = useRef({ x: -1000, y: -1000 });
  const animationRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  const baseRgb = useMemo(() => hexToRgb(baseColor), [baseColor]);
  const glowRgb = useMemo(() => hexToRgb(glowColor), [glowColor]);

  const buildGrid = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    const ctx = canvas.getContext("2d");
    if (ctx) ctx.scale(dpr, dpr);

    const cellSize = dotSize + gap;
    const cols = Math.ceil(rect.width / cellSize) + 1;
    const rows = Math.ceil(rect.height / cellSize) + 1;

    const offsetX = (rect.width - (cols - 1) * cellSize) / 2;
    const offsetY = (rect.height - (rows - 1) * cellSize) / 2;

    const dots = [];
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        dots.push({
          x: offsetX + col * cellSize,
          y: offsetY + row * cellSize,
          baseOpacity: 0.3 + Math.random() * 0.2,
        });
      }
    }
    dotsRef.current = dots;
  }, [dotSize, gap]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr);

    const { x: mx, y: my } = mouseRef.current;
    const proxSq = proximity * proximity;
    const time = (Date.now() - startTimeRef.current) * 0.001 * waveSpeed;

    for (const dot of dotsRef.current) {
      const dx = dot.x - mx;
      const dy = dot.y - my;
      const distSq = dx * dx + dy * dy;

      // Wave animation
      const wave = Math.sin(dot.x * 0.02 + dot.y * 0.02 + time) * 0.5 + 0.5;
      const waveOpacity = dot.baseOpacity + wave * 0.15;
      const waveScale = 1 + wave * 0.2;

      let opacity = waveOpacity;
      let scale = waveScale;
      let r = baseRgb.r;
      let g = baseRgb.g;
      let b = baseRgb.b;
      let glow = 0;

      // Mouse proximity effect
      if (distSq < proxSq) {
        const dist = Math.sqrt(distSq);
        const t = 1 - dist / proximity;
        const easedT = t * t * (3 - 2 * t); // smoothstep

        r = Math.round(baseRgb.r + (glowRgb.r - baseRgb.r) * easedT);
        g = Math.round(baseRgb.g + (glowRgb.g - baseRgb.g) * easedT);
        b = Math.round(baseRgb.b + (glowRgb.b - baseRgb.b) * easedT);

        opacity = Math.min(1, waveOpacity + easedT * 0.7);
        scale = waveScale + easedT * 0.8;
        glow = easedT * glowIntensity;
      }

      const radius = (dotSize / 2) * scale;

      // Draw glow halo
      if (glow > 0) {
        const gradient = ctx.createRadialGradient(
          dot.x,
          dot.y,
          0,
          dot.x,
          dot.y,
          radius * 4,
        );
        gradient.addColorStop(
          0,
          `rgba(${glowRgb.r},${glowRgb.g},${glowRgb.b},${glow * 0.4})`,
        );
        gradient.addColorStop(
          0.5,
          `rgba(${glowRgb.r},${glowRgb.g},${glowRgb.b},${glow * 0.1})`,
        );
        gradient.addColorStop(
          1,
          `rgba(${glowRgb.r},${glowRgb.g},${glowRgb.b},0)`,
        );
        ctx.beginPath();
        ctx.arc(dot.x, dot.y, radius * 4, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
      }

      // Draw dot
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${r},${g},${b},${opacity})`;
      ctx.fill();
    }

    animationRef.current = requestAnimationFrame(draw);
  }, [proximity, baseRgb, glowRgb, dotSize, glowIntensity, waveSpeed]);

  /* Build grid on mount + resize */
  useEffect(() => {
    buildGrid();
    const container = containerRef.current;
    if (!container) return;
    const ro = new ResizeObserver(buildGrid);
    ro.observe(container);
    return () => ro.disconnect();
  }, [buildGrid]);

  /* Start animation loop */
  useEffect(() => {
    animationRef.current = requestAnimationFrame(draw);
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [draw]);

  /* Track mouse — listen on WINDOW so events work even when UI elements
       are layered on top of the fixed canvas (pointer-events would block
       container-level listeners). The canvas is fixed full-viewport so
       clientX/Y map directly to canvas coordinates. */
  useEffect(() => {
    const handleMouseMove = (e) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };
    const handleMouseLeave = () => {
      mouseRef.current = { x: -1000, y: -1000 };
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={cn("fixed inset-0 overflow-hidden", className)}
      style={{ background: "#000", pointerEvents: "none" }}
    >
      <canvas ref={canvasRef} />
      {children}
    </div>
  );
}

export default DotPattern;
