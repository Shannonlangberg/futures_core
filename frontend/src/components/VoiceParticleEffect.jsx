import React, { useEffect, useRef, useState } from 'react';

const VoiceParticleEffect = ({ isRecording, isHovered, children }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const particlesRef = useRef([]);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });

  // Particle class
  class Particle {
    constructor(x, y, canvas) {
      this.x = x;
      this.y = y;
      this.canvas = canvas;
      this.vx = (Math.random() - 0.5) * 0.2;
      this.vy = (Math.random() - 0.5) * 0.2;
      this.size = Math.random() * 1.5 + 0.3;
      this.opacity = Math.random() * 0.6 + 0.2;
      this.life = Math.random() * 300 + 200;
      this.maxLife = this.life;
      this.originalX = x;
      this.originalY = y;
      this.wanderRadius = Math.random() * 30 + 10;
      this.wanderAngle = Math.random() * Math.PI * 2;
      this.wanderSpeed = (Math.random() - 0.5) * 0.01;
      this.centerX = canvas.width / 2;
      this.centerY = canvas.height / 2;
      this.attractionRadius = 150;
    }

    update(isRecording, isHovered) {
      // Calculate distance from center
      const dx = this.x - this.centerX;
      const dy = this.y - this.centerY;
      const distanceFromCenter = Math.sqrt(dx * dx + dy * dy);

      // Natural wandering motion
      this.wanderAngle += this.wanderSpeed;
      const targetX = this.originalX + Math.cos(this.wanderAngle) * this.wanderRadius;
      const targetY = this.originalY + Math.sin(this.wanderAngle) * this.wanderRadius;
      
      // Gentle movement towards target
      this.x += (targetX - this.x) * 0.005;
      this.y += (targetY - this.y) * 0.005;
      
      // Add subtle velocity
      this.x += this.vx;
      this.y += this.vy;
      
      // Attraction to center area
      if (distanceFromCenter > this.attractionRadius) {
        const attractionStrength = 0.002;
        this.x += (this.centerX - this.x) * attractionStrength;
        this.y += (this.centerY - this.y) * attractionStrength;
      }
      
      // Bounce off edges with wrap-around
      if (this.x < 0) this.x = this.canvas.width;
      if (this.x > this.canvas.width) this.x = 0;
      if (this.y < 0) this.y = this.canvas.height;
      if (this.y > this.canvas.height) this.y = 0;

      // Life cycle
      this.life--;
      if (this.life <= 0) {
        this.life = this.maxLife;
        // Respawn in center area
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * this.attractionRadius;
        this.x = this.centerX + Math.cos(angle) * radius;
        this.y = this.centerY + Math.sin(angle) * radius;
        this.originalX = this.x;
        this.originalY = this.y;
      }

      // Opacity based on recording state
      if (isRecording) {
        this.opacity = Math.min(0.8, this.opacity + 0.01);
      } else {
        this.opacity = Math.max(0.2, this.opacity - 0.003);
      }
    }

    draw(ctx) {
      ctx.save();
      ctx.globalAlpha = this.opacity;
      
      // Create soft glowing effect
      const gradient = ctx.createRadialGradient(
        this.x, this.y, 0,
        this.x, this.y, this.size * 4
      );
      gradient.addColorStop(0, 'rgba(191, 219, 254, 0.9)'); // Light blue center
      gradient.addColorStop(0.3, 'rgba(147, 197, 253, 0.6)'); // Blue
      gradient.addColorStop(0.7, 'rgba(59, 130, 246, 0.3)'); // Darker blue
      gradient.addColorStop(1, 'rgba(147, 197, 253, 0)');
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size * 4, 0, Math.PI * 2);
      ctx.fill();
      
      // Inner bright core
      ctx.fillStyle = 'rgba(219, 234, 254, 0.9)';
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
      
      ctx.restore();
    }
  }

  // Initialize particles
  const initParticles = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const particleCount = 200; // More particles for denser effect
    particlesRef.current = [];

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const attractionRadius = 150;

    for (let i = 0; i < particleCount; i++) {
      // Distribute particles around center area
      const angle = Math.random() * Math.PI * 2;
      const radius = Math.random() * attractionRadius;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      
      particlesRef.current.push(
        new Particle(x, y, canvas)
      );
    }
  };

  // Animation loop
  const animate = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    
    // Clear canvas with fade effect
    ctx.fillStyle = 'rgba(15, 23, 42, 0.03)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Update and draw particles
    particlesRef.current.forEach(particle => {
      particle.update(isRecording, isHovered);
      particle.draw(ctx);
    });

    animationRef.current = requestAnimationFrame(animate);
  };

  // Handle resize
  const handleResize = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    setCanvasSize({ width: rect.width, height: rect.height });
  };

  // Initialize and cleanup
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    handleResize();
    initParticles();
    animate();

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none"
        style={{ zIndex: 1 }}
      />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};

export default VoiceParticleEffect; 