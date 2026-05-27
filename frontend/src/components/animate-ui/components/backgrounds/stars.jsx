import { useEffect, useRef } from 'react';

export function StarsBackground({ 
  starColor = '#ffffff', 
  className = '', 
  style = {},
  count = 200 
}) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const setSize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    setSize();

    const stars = Array.from({ length: count }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      baseX: 0,
      baseY: 0,
      radius: Math.random() * 1.4 + 0.2,
      alpha: Math.random() * 0.6 + 0.4,
      speed: Math.random() * 0.6 + 0.2,
      phase: Math.random() * Math.PI * 2,
      parallax: Math.random() * 0.5 + 0.5,
    }));

    stars.forEach(star => {
      star.baseX = star.x;
      star.baseY = star.y;
    });

    let time = 0;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      time += 0.016;
      
      const mouseX = mouseRef.current.x;
      const mouseY = mouseRef.current.y;
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const offsetX = (mouseX - centerX) * 0.02;
      const offsetY = (mouseY - centerY) * 0.02;

      stars.forEach((star) => {
        const flicker = Math.sin(time * star.speed + star.phase) * 0.35 + 0.65;
        const moveX = offsetX * star.parallax;
        const moveY = offsetY * star.parallax;
        
        ctx.beginPath();
        ctx.arc(star.baseX + moveX, star.baseY + moveY, star.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${hexToRgb(starColor)}, ${(star.alpha * flicker).toFixed(3)})`;
        ctx.fill();
      });
      animationRef.current = requestAnimationFrame(draw);
    };

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    };

    const handleResize = () => {
      setSize();
      stars.forEach((star) => {
        star.x = Math.random() * canvas.width;
        star.y = Math.random() * canvas.height;
        star.baseX = star.x;
        star.baseY = star.y;
      });
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('resize', handleResize);
    draw();

    return () => {
      cancelAnimationFrame(animationRef.current);
      canvas.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
    };
  }, [count, starColor]);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', ...style }}
    />
  );
}

function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result 
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : '255, 255, 255';
}
