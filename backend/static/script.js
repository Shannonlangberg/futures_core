// FIXED Futures Link Assistant - Complete Version with Performance Optimizations
document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Enhanced Futures Link Assistant initializing...');

  // Set page title to 'Futures LINK'
  document.title = 'Futures LINK';

  // State Management
  let currentState = 'idle';
  let particleInterval;
  let recognitionIsRunning = false;
  let currentCampus = null;
  let sessionData = {};
  let audioQueue = [];
  let isPlayingAudio = false;
  let dataRefreshInterval;
  let greeted = false;
  
  // Initialize campus from dropdown
  const campusDropdown = document.getElementById('campusDropdown');
  if (campusDropdown) {
    currentCampus = campusDropdown.value ? campusDropdown.value.toLowerCase() : null;
    console.log(`Initialized currentCampus to: ${currentCampus}`);
  }

  // DOM Elements
  const orbContainer = document.querySelector('.orb-container');
  const orbWrapper = document.getElementById('orbWrapper');
  const statusText = document.getElementById('statusText');
  const transcriptDisplay = document.getElementById('transcriptDisplay');
  const particlesContainer = document.getElementById('particlesContainer');
  const campusSelect = document.getElementById('campusSelect');
  const navItems = document.querySelectorAll('.nav-item');
  const statCards = document.querySelectorAll('.stat-card');

  // No hardcoded default encouragements/insights present; only backend-provided encouragements are used.

  // OPTIMIZED PARTICLE SYSTEM - Better Performance
  function createParticle() {
    if (!particlesContainer) return;
    
    // Get the full dimensions of the assistant panel
    const panelRect = particlesContainer.getBoundingClientRect();
    const panelWidth = panelRect.width;
    const panelHeight = panelRect.height;
    
    // FIXED: Reduced particle limit for better performance
    if (particlesContainer.children.length > 15) { // Reduced from 25
      const oldParticles = Array.from(particlesContainer.children).slice(0, 3);
      oldParticles.forEach(particle => particle.remove());
    }
    
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // SIMPLIFIED: Fewer particle types for better performance
    const types = ['type-1', 'type-2', 'type-3'];
    const randomType = types[Math.floor(Math.random() * types.length)];
    particle.classList.add(randomType);
    
    // Position particles anywhere in the container
    const x = Math.random() * (panelWidth - 10);
    const y = panelHeight - 10; // Start from bottom
    
    particle.style.left = x + 'px';
    particle.style.top = y + 'px';
    
    // OPTIMIZED: Simpler animation timing
    const baseDelay = Math.random() * 0.5; // Reduced delay variation
    particle.style.animationDelay = baseDelay + 's';
    particle.style.animationDuration = `${3 + Math.random() * 2}s`; // 3-5 seconds (reduced from 3-6)
    
    particlesContainer.appendChild(particle);
    
    // Enhanced cleanup
    const cleanup = () => {
      if (particle.parentNode) {
        particle.parentNode.removeChild(particle);
      }
    };
    
    particle.addEventListener('animationend', cleanup);
    setTimeout(cleanup, 6000); // Reduced cleanup time
  }

  // OPTIMIZED burst effect
  function createParticleBurst(intensity = 5, type = null) {
    if (!particlesContainer) return;
    
    const panelRect = particlesContainer.getBoundingClientRect();
    const centerX = panelRect.width / 2;
    const centerY = panelRect.height / 2;
    
    // FIXED: Reduced intensity to improve performance
    const safeIntensity = Math.min(intensity, 8);
    
    for (let i = 0; i < safeIntensity; i++) {
      setTimeout(() => {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Use specific type or random
        if (type) {
          particle.classList.add(type);
        } else {
          const types = ['type-1', 'type-2', 'type-3'];
          particle.classList.add(types[Math.floor(Math.random() * types.length)]);
        }
        
        // Burst from center area with some spread
        const spreadRadius = 60; // Reduced spread for performance
        const angle = (Math.PI * 2 * i) / safeIntensity;
        const distance = Math.random() * spreadRadius;
        
        const x = centerX + Math.cos(angle) * distance;
        const y = centerY + Math.sin(angle) * distance;
        
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.animationDelay = (Math.random() * 0.2) + 's';
        
        particlesContainer.appendChild(particle);
        
        // Cleanup
        const cleanup = () => {
          if (particle.parentNode) {
            particle.parentNode.removeChild(particle);
          }
        };
        
        particle.addEventListener('animationend', cleanup);
        setTimeout(cleanup, 5000); // Reduced cleanup time
        
      }, i * 80); // Reduced stagger time
    }
  }

  // OPTIMIZED ambient particle system
  function createAmbientParticles() {
    if (!particlesContainer) return;
    
    // FIXED: Reduced ambient particle count
    const count = 2 + Math.floor(Math.random() * 2); // 2-3 particles instead of 3-5
    
    for (let i = 0; i < count; i++) {
      setTimeout(() => {
        createParticle();
      }, i * 300); // Increased interval
    }
  }

  // Text Input Functions (PRESERVED - unchanged)
  function showTextInputOption() {
    // Remove existing input if present
    const existingInput = document.getElementById('text-input-panel');
    if (existingInput) existingInput.remove();

    const inputPanel = document.createElement('div');
    inputPanel.id = 'text-input-panel';
    inputPanel.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(15, 20, 40, 0.95);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(0, 212, 255, 0.3);
      border-radius: 16px;
      padding: 30px;
      max-width: 450px;
      width: 90%;
      color: white;
      z-index: 1000;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
      animation: fadeIn 0.3s ease-out;
    `;
    
    inputPanel.innerHTML = `
      <style>
        @keyframes fadeIn {
          from { opacity: 0; transform: translate(-50%, -60%); }
          to { opacity: 1; transform: translate(-50%, -50%); }
        }
        @keyframes fadeOut {
          from { opacity: 1; transform: translate(-50%, -50%); }
          to { opacity: 0; transform: translate(-50%, -60%); }
        }
      </style>
      
      <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="margin: 0 0 10px 0; color: #00d4ff; font-size: 1.3rem;">📝 Enter Your Stats</h3>
        <p style="margin: 0; color: rgba(255,255,255,0.7); font-size: 0.9rem;">
          Type your attendance data - works exactly like voice input!
        </p>
      </div>
      
      <textarea 
        id="statsTextInput" 
        placeholder="Example: Salisbury had 150 people, 8 new visitors, 3 salvations"
        style="
          width: 100%;
          height: 90px;
          padding: 15px;
          border: 1px solid rgba(0, 212, 255, 0.3);
          border-radius: 8px;
          background: rgba(0,0,0,0.4);
          color: white;
          font-size: 1rem;
          resize: vertical;
          font-family: 'Inter', sans-serif;
          margin-bottom: 15px;
          line-height: 1.4;
          outline: none;
          transition: border-color 0.3s ease;
        "
      ></textarea>
      
      <div style="display: flex; gap: 12px; margin-bottom: 20px;">
        <button onclick="submitTextStats()" style="
          flex: 1;
          background: linear-gradient(135deg, #00d4ff, #0ea5e9);
          border: none;
          border-radius: 8px;
          padding: 14px 20px;
          color: white;
          font-weight: 600;
          cursor: pointer;
          font-size: 1rem;
          transition: transform 0.2s ease;
        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
          ✅ Submit Stats
        </button>
        
        <button onclick="closeTextInput()" style="
          background: rgba(255,255,255,0.1);
          border: 1px solid rgba(255,255,255,0.3);
          border-radius: 8px;
          padding: 14px 20px;
          color: white;
          cursor: pointer;
          font-size: 1rem;
          transition: background 0.2s ease;
        " onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">
          ❌ Cancel
        </button>
      </div>
      
      <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 0.85rem; color: rgba(255,255,255,0.6);">
        <strong style="color: #00d4ff;">📋 Examples:</strong><br>
        • "Salisbury had 120 attendance, 5 new people"<br>
        • "Paradise campus: 89 people, 3 salvations, 12 youth"<br>
        • "Adelaide City 200 attendance 15 new visitors 4 new Christians"<br><br>
        <strong style="color: #ffa500;">⌨️ Shortcuts:</strong> Ctrl+Enter to submit, Escape to close
      </div>
    `;
    
    document.body.appendChild(inputPanel);
    
    // Focus on the textarea
    const textarea = document.getElementById('statsTextInput');
    if (textarea) {
      textarea.focus();
      
      // Style focus state
      textarea.addEventListener('focus', () => {
        textarea.style.borderColor = '#00d4ff';
        textarea.style.boxShadow = '0 0 0 2px rgba(0, 212, 255, 0.2)';
      });
      
      textarea.addEventListener('blur', () => {
        textarea.style.borderColor = 'rgba(0, 212, 255, 0.3)';
        textarea.style.boxShadow = 'none';
      });
      
      // Handle keyboard shortcuts
      textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.shiftKey)) {
          e.preventDefault();
          submitTextStats();
        } else if (e.key === 'Escape') {
          closeTextInput();
        }
      });
    }
  }

  // Submit text stats function (PRESERVED)
  window.submitTextStats = function() {
    const textarea = document.getElementById('statsTextInput');
    if (!textarea || !textarea.value.trim()) {
      // Show error styling
      if (textarea) {
        textarea.style.borderColor = '#ef4444';
        textarea.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.2)';
        textarea.placeholder = 'Please enter some stats first!';
        setTimeout(() => {
          textarea.style.borderColor = 'rgba(0, 212, 255, 0.3)';
          textarea.style.boxShadow = 'none';
          textarea.placeholder = 'Example: Salisbury had 150 people, 8 new visitors, 3 salvations';
        }, 2000);
      }
      return;
    }
    
    const text = textarea.value.trim();
    console.log('📝 Text stats submitted:', text);
    
    // Close the input panel with animation
    const inputPanel = document.getElementById('text-input-panel');
    if (inputPanel) {
      inputPanel.style.animation = 'fadeOut 0.3s ease-out forwards';
      setTimeout(() => inputPanel.remove(), 300);
    }
    
    // Show the text in the transcript display
    const transcriptElement = document.getElementById('transcript');
    if (transcriptElement) {
      transcriptElement.textContent = `⌨️ Typed: "${text}"`;
      transcriptElement.style.display = 'block';
      // Clear after 5 seconds
      setTimeout(() => {
        transcriptElement.textContent = 'Listening here...';
      }, 5000);
    }
    
    // Visual feedback
    showSuccess('Processing your stats...');
    
    // Process exactly like voice input
    setState('processing', 'Processing your stats...');
    processVoiceInput(text);
  };

  // Close text input function (PRESERVED)
  window.closeTextInput = function() {
    const inputPanel = document.getElementById('text-input-panel');
    if (inputPanel) {
      inputPanel.style.animation = 'fadeOut 0.3s ease-out forwards';
      setTimeout(() => inputPanel.remove(), 300);
    }
  };

  // Close text input function (PRESERVED)
  window.closeTextInput = function() {
    const inputPanel = document.getElementById('text-input-panel');
    if (inputPanel) {
      inputPanel.style.animation = 'fadeOut 0.3s ease-out forwards';
      setTimeout(() => inputPanel.remove(), 300);
    }
  };

  // Enhanced microphone device detection (PRESERVED)
  async function detectAudioDevices() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = devices.filter(device => device.kind === 'audioinput');
      
      console.log('🎤 Audio input devices found:', audioInputs.length);
      return audioInputs.length > 0;
    } catch (error) {
      console.error('❌ Failed to enumerate devices:', error);
      return false;
    }
  }

  // Enhanced microphone permission handling (PRESERVED)
  async function requestMicrophonePermission() {
    try {
      console.log('🎤 Checking for microphone devices...');
      
      // First check if any audio input devices exist
      const hasAudioDevices = await detectAudioDevices();
      if (!hasAudioDevices) {
        console.log('🎤 No audio devices found, offering text input');
        return false;
      }
      
      // Check if we're on HTTPS (required for mic access)
      if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
        showError('Microphone requires HTTPS connection. Using text input instead.', 0);
        return false;
      }
      
      console.log('🎤 Requesting microphone permission...');
      
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: { ideal: 44100, min: 8000 },
          channelCount: { ideal: 1 }
        } 
      });
      
      // Stop the stream immediately (we just needed permission)
      stream.getTracks().forEach(track => track.stop());
      
      console.log('✅ Microphone permission granted');
      updateConnectionStatus();
      return true;
      
    } catch (error) {
      console.error('❌ Microphone permission error:', error);
      updateConnectionStatus();
      return false;
    }
  }

  // Update connection status indicator (PRESERVED)
  async function updateConnectionStatus() {
    const statusIndicator = document.querySelector('.status-indicator span');
    const statusDot = document.querySelector('.status-dot');
    
    if (!statusIndicator || !statusDot) return;
    
    // Check if audio devices exist
    const hasAudioDevices = await detectAudioDevices();
    
    if (!hasAudioDevices) {
      statusIndicator.textContent = 'Text Input Ready';
      statusDot.style.background = '#00d4ff';
      statusDot.style.animation = 'pulse 2s ease-in-out infinite';
      return;
    }
    
    // Check microphone permission status
    if (navigator.permissions) {
      navigator.permissions.query({ name: 'microphone' }).then(permission => {
        if (permission.state === 'granted') {
          statusIndicator.textContent = 'Voice & Text Ready';
          statusDot.style.background = '#22c55e';
          statusDot.style.animation = 'pulse 2s ease-in-out infinite';
        } else if (permission.state === 'denied') {
          statusIndicator.textContent = 'Text Input Ready';
          statusDot.style.background = '#ffa500';
          statusDot.style.animation = 'pulse 1s ease-in-out infinite';
        } else {
          statusIndicator.textContent = 'Click to Start';
          statusDot.style.background = '#00d4ff';
          statusDot.style.animation = 'pulse 1.5s ease-in-out infinite';
        }
      }).catch(() => {
        statusIndicator.textContent = 'Ready to Start';
        statusDot.style.background = '#00d4ff';
        statusDot.style.animation = 'pulse 2s ease-in-out infinite';
      });
    } else {
      statusIndicator.textContent = 'Ready to Start';
      statusDot.style.background = '#00d4ff';
      statusDot.style.animation = 'pulse 2s ease-in-out infinite';
    }
  }

  // Enhanced error handling with user-friendly messages (PRESERVED)
  const showError = (message, duration = 5000) => {
    console.error('🚨', message);
    
    if (statusText) {
      statusText.textContent = message;
      statusText.style.color = '#ef4444';
    }
    
    // Also show in transcript area for better visibility
    if (transcriptDisplay) {
      transcriptDisplay.innerHTML = `<span style="color: #ef4444;">❌ ${message}</span>`;
    }
    
    if (duration > 0) {
      setTimeout(() => {
        if (currentState === 'idle') {
          if (statusText) {
            statusText.textContent = 'Click orb for voice, or Ctrl+T for text';
            statusText.style.color = '#00d4ff';
          }
          if (transcriptDisplay) {
            transcriptDisplay.textContent = 'Voice or text input available';
          }
        }
      }, duration);
    }
  };

  const showSuccess = (message, duration = 3000) => {
    if (statusText) {
      statusText.textContent = message;
      statusText.style.color = '#22c55e';
    }
    setTimeout(() => {
      if (currentState === 'idle' && statusText) {
        statusText.style.color = '#00d4ff';
      }
    }, duration);
  };

  // OPTIMIZED state management with improved particle effects
  function setState(newState, customMessage = null) {
    if (!orbWrapper) return;
    
    // Remove existing state classes
    orbWrapper.className = orbWrapper.className.replace(/orb-\w+/g, '');
    orbWrapper.classList.add(`orb-${newState}`);
    currentState = newState;

    // Clear existing particle interval
    if (particleInterval) {
      clearInterval(particleInterval);
    }

    // Update status with custom message or defaults
    const messages = {
      listening: customMessage || 'Listening... speak clearly',
      processing: customMessage || 'Processing your request...',
      speaking: customMessage || 'Link is responding...',
      idle: customMessage || 'Click orb for voice, or Ctrl+T for text'
    };

    const colors = {
      listening: '#ffa500',
      processing: '#9333ea', 
      speaking: '#22c55e',
      idle: '#00d4ff'
    };

    if (statusText) {
      statusText.textContent = messages[newState];
      statusText.style.color = colors[newState];
    }

    // Update transcript for idle state
    if (newState === 'idle' && transcriptDisplay) {
      transcriptDisplay.textContent = 'Voice or text input available';
    }

    // OPTIMIZED particle effects per state
    switch(newState) {
      case 'listening':
        // Burst effect + continuous particles
        createParticleBurst(6, 'type-1'); // Reduced from 8
        particleInterval = setInterval(() => {
          createParticle();
        }, 400); // Increased interval from 300
        break;
        
      case 'processing':
        // Rapid, intense particles
        createParticleBurst(8, 'type-2'); // Reduced from 12
        particleInterval = setInterval(() => {
          createParticle();
          if (Math.random() > 0.7) createParticle(); // Reduced probability
        }, 200); // Increased interval from 150
        break;
        
      case 'speaking':
        // Rhythmic, pulsing particles
        createParticleBurst(4, 'type-3'); // Reduced from 6
        let pulseToggle = true;
        particleInterval = setInterval(() => {
          if (pulseToggle) {
            createParticle();
          }
          pulseToggle = !pulseToggle;
        }, 500); // Increased interval from 400
        break;
        
      case 'idle':
      default:
        // Gentle ambient particles throughout the container
        createAmbientParticles();
        particleInterval = setInterval(() => {
          createAmbientParticles();
        }, 3000); // Increased interval from 2000
        break;
    }
  }

  // Enhanced Speech Recognition with better error handling (PRESERVED)
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition;
  
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      recognitionIsRunning = true;
      setState('listening');
      console.log('🎤 Voice recognition started');
    };

    recognition.onresult = (event) => {
      let transcript = '';
      let isFinal = false;

      // Process all results
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          isFinal = true;
        }
      }

      // Show interim results in gray
      if (!isFinal) {
        if (transcriptDisplay) {
          transcriptDisplay.innerHTML = `<span style="color: rgba(255,255,255,0.5);">"${transcript}"</span>`;
        }
        return;
      }

      // Final transcript
      if (transcriptDisplay) {
        transcriptDisplay.innerHTML = `<span style="color: #00d4ff;">"${transcript}"</span>`;
      }
      setState('processing', 'Processing your request...');
      
      // Send to backend
      processVoiceInput(transcript.trim());
    };

    recognition.onerror = (event) => {
      console.error('🎤 Speech recognition error:', event.error);
      recognitionIsRunning = false;
      
      const errorMessages = {
        'no-speech': 'No speech detected. Try text input instead?',
        'audio-capture': 'Microphone issue. Using text input.',
        'not-allowed': 'Microphone blocked. Using text input.',
        'network': 'Network error. Try text input.',
        'aborted': 'Recognition interrupted.'
      };
      
      const message = errorMessages[event.error] || 'Voice error. Try text input?';
      showError(message);
      
      // Offer text input for most errors
      if (event.error !== 'aborted') {
        setTimeout(() => {
          showTextInputOption();
        }, 2000);
      }
      
      setTimeout(() => setState('idle'), 2000);
    };

    recognition.onend = () => {
      recognitionIsRunning = false;
      console.log('🎤 Voice recognition ended');
      // FIXED: Removed auto-restart functionality - user must click again
    };
  } else {
    console.warn('⚠️ Speech recognition not supported in this browser');
  }

  // Add this helper function near the top or after updateStatsDisplay
  function renderReportTable(report) {
    if (!report || !Array.isArray(report) || report.length === 0) return '';

    // Group by year for better organization
    const groupedByYear = {};
    report.forEach(row => {
      if (!groupedByYear[row.year]) {
        groupedByYear[row.year] = [];
      }
      groupedByYear[row.year].push(row);
    });

    let html = `
      <div id="annual-review-panel" style="
        background: rgba(15, 20, 40, 0.85);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 212, 255, 0.18);
        border-radius: 18px;
        padding: 14px 8px 24px 8px;
        margin: 0 0 32px 0; /* Sits higher: no top margin, more bottom margin */
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        overflow-x: auto;
        width: 100%;
        max-width: 100vw;
        position: relative;
      ">
        <button onclick="closeAnnualReview()" style="
          position: absolute;
          top: 10px;
          right: 14px;
          background: none;
          border: none;
          color: #00d4ff;
          font-size: 1.3rem;
          font-weight: bold;
          cursor: pointer;
          z-index: 10;
          padding: 0 6px;
          line-height: 1;
          opacity: 0.7;
          transition: opacity 0.2s;
        " onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'" aria-label="Close">×</button>
        <h3 style="
          color: #00d4ff;
          font-size: 1.2rem;
          margin: 0 0 12px 0;
          text-align: center;
          font-weight: 700;
          letter-spacing: -0.5px;
        ">📊 Annual Report</h3>
        <div style="
          display: flex;
          flex-wrap: nowrap;
          gap: 14px;
          overflow-x: auto;
          padding-bottom: 4px;
          justify-content: flex-start;
          align-items: stretch;
          width: 100%;
          scrollbar-width: thin;
        ">
    `;

    // Sort years in descending order
    const years = Object.keys(groupedByYear).sort((a, b) => b - a);

    years.forEach(year => {
      const yearData = groupedByYear[year];
      html += `
        <div style="
          background: rgba(0, 0, 0, 0.18);
          border: 1.5px solid rgba(0, 212, 255, 0.18);
          border-radius: 14px;
          padding: 14px 10px 18px 10px;
          min-width: 260px;
          max-width: 95vw;
          flex: 0 0 320px;
          margin-bottom: 0;
          display: flex;
          flex-direction: column;
          align-items: stretch;
          box-shadow: 0 2px 12px rgba(0,212,255,0.07);
          transition: box-shadow 0.2s;
        ">
          <h4 style="
            color: #22c55e;
            font-size: 1.1rem;
            margin: 0 0 12px 0;
            font-weight: 700;
            text-align: center;
            border-bottom: 2px solid rgba(34, 197, 94, 0.18);
            padding-bottom: 6px;
            letter-spacing: 0.5px;
          ">${year}</h4>
          <table style="
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
          ">
            <thead>
              <tr style="
                background: linear-gradient(135deg, #0ea5e9, #00d4ff);
                color: white;
                font-weight: 600;
              ">
                <th style="padding: 8px 4px; text-align: left; border-radius: 6px 0 0 6px; font-size: 0.8rem;">Stat</th>
                <th style="padding: 8px 4px; text-align: center; font-size: 0.8rem;">Total</th>
                <th style="padding: 8px 4px; text-align: center; font-size: 0.8rem;">Avg</th>
                <th style="padding: 8px 4px; text-align: center; border-radius: 0 6px 6px 0; font-size: 0.8rem;">#</th>
              </tr>
            </thead>
            <tbody>
    `;

    yearData.forEach((row, index) => {
      const isEven = index % 2 === 0;
      html += `
        <tr style="
          background: ${isEven ? 'rgba(0, 212, 255, 0.04)' : 'rgba(14, 165, 233, 0.04)'};
          transition: background 0.2s ease;
        " onmouseover="this.style.background='rgba(0, 212, 255, 0.09)'" onmouseout="this.style.background='${isEven ? 'rgba(0, 212, 255, 0.04)' : 'rgba(14, 165, 233, 0.04)'}'">
          <td style="
            padding: 7px 4px;
            font-weight: 500;
            color: #e2e8f0;
            border-left: 3px solid #00d4ff;
            font-size: 0.8rem;
            max-width: 120px;
            overflow-wrap: break-word;
          ">${row.label}</td>
          <td style="
            padding: 7px 4px;
            text-align: center;
            font-weight: 600;
            color: #22c55e;
            font-size: 0.8rem;
          ">${row.total.toLocaleString()}</td>
          <td style="
            padding: 7px 4px;
            text-align: center;
            color: #f59e0b;
            font-size: 0.8rem;
          ">${row.average}</td>
          <td style="
            padding: 7px 4px;
            text-align: center;
            color: #8b5cf6;
            font-size: 0.75rem;
          ">${row.count}</td>
        </tr>
      `;
    });

    html += `
            </tbody>
          </table>
        </div>
      `;
    });

    html += `
        </div>
        <div style="
          margin-top: 18px;
          padding: 10px;
          background: rgba(34, 197, 94, 0.09);
          border: 1px solid rgba(34, 197, 94, 0.18);
          border-radius: 8px;
          text-align: center;
          color: #22c55e;
          font-size: 0.92rem;
          max-width: 100vw;
        ">
          💡 Years are scrollable side by side • Drag or swipe to see more
        </div>
        <div style="
          margin-top: 12px;
          text-align: center;
        ">
          <button onclick="clearReport()" style="
            background: linear-gradient(135deg, #ef4444, #dc2626);
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.9rem;
            transition: transform 0.2s, box-shadow 0.2s;
          " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 25px rgba(239, 68, 68, 0.18)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
            ❌ Clear Report & Continue
          </button>
        </div>
      </div>
    `;

    return html;
  }

  // Add the clearReport function
  window.clearReport = function() {
    const insightsPanel = document.querySelector('.insights-panel');
    const encouragementsList = document.getElementById('encouragements');
    
    if (insightsPanel && encouragementsList) {
      // Reset to default state
      encouragementsList.innerHTML = '<span class="insight-item">📊 Insights will appear here...</span>';
      insightsPanel.style.display = '';
      
      // Show success message
      showSuccess('Report cleared. Ready for your next request!');
      
      // Reset state to idle
      setState('idle', 'Click orb for voice, or Ctrl+T for text');
    }
  };

  // Enhanced voice processing with better API integration (PRESERVED)
  async function processVoiceInput(transcript) {
    if (!transcript) {
      showError('No input received. Please try again.');
      setState('idle');
      return;
    }

    // Display what was heard
    const transcriptElement = document.getElementById('transcript');
    if (transcriptElement) {
      transcriptElement.textContent = `🎤 Heard: "${transcript}"`;
      transcriptElement.style.display = 'block';
      // Clear after 5 seconds
      setTimeout(() => {
        transcriptElement.textContent = 'Listening here...';
      }, 5000);
    }

    try {
      const response = await fetch('/api/process_voice', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          text: transcript,
          campus: currentCampus 
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      
      // --- FIXED: Show ALL queries in modal popup ---
      console.log('🔍 Checking if this is a query response...');
      console.log('Data keys:', Object.keys(data));
      console.log('Has report:', !!data.report);
      console.log('Has analysis:', !!data.analysis);
      console.log('Has question:', !!data.question);
      console.log('Has comparison:', !!data.comparison);
      console.log('Has popup:', !!data.popup);
      console.log('Has summary:', !!data.summary);
      
      if (data.popup === true) {
        console.log('✅ data.popup is true, showing modal popup (forced)');
        if (window.showQueryModal && typeof window.showQueryModal === 'function') {
          try {
            window.showQueryModal(data);
            console.log('✅ Modal function called successfully (popup forced)');
          } catch (error) {
            console.error('❌ Error calling modal function:', error);
          }
        }
        setState('speaking', data.text);
        if (data.audio_url) {
          await playAudioResponse(data.audio_url);
        } else if (data.text) {
          await speakText(data.text);
        }
        return;
      }
      // fallback: legacy logic
      if (data.report || data.analysis || data.question || data.comparison || (data.summary && data.popup)) {
        console.log('📊 Query detected, showing modal popup...');
        if (window.showQueryModal && typeof window.showQueryModal === 'function') {
          try {
            window.showQueryModal(data);
            console.log('✅ Modal function called successfully');
          } catch (error) {
            console.error('❌ Error calling modal function:', error);
          }
        }
        setState('speaking', data.text);
        if (data.audio_url) {
          await playAudioResponse(data.audio_url);
        } else if (data.text) {
          await speakText(data.text);
        }
        return;
      }
      
      // Show regular stats logging responses in a styled box (not queries)
      showQueryBox({text: data.text, stats: data.stats, insights: data.insights, report: data.report});
      
      // Update UI with response
      setState('speaking', data.text);
      
      // Update campus if changed
      console.log(`Received campus: ${data.campus}, current campus: ${currentCampus}`);
      
      // Always update campus if we received one from the backend
      if (data.campus !== undefined && data.campus !== currentCampus) {
        console.log(`Updating campus from ${currentCampus} to ${data.campus}`);
        updateCampus(data.campus);
        
        // Fetch latest stats for the new campus
        if (data.campus) {
          fetch('/api/stats?campus=' + encodeURIComponent(data.campus))
            .then(response => response.json())
            .then(data => {
              console.log('📊 Latest stats for new campus:', data);
              
              let statData = {
                total_attendance: 0,
                new_people: 0,
                new_christians: 0,
                youth_attendance: 0,
                kids_total: 0,
                connect_groups: 0
              };
              
              if (data.stats && data.stats.length > 0) {
                const latest = data.stats[0];
                statData = {
                  total_attendance: latest['Total Attendance'] || latest.total_attendance || 0,
                  new_people: latest['New People'] || latest.new_people || 0,
                  new_christians: latest['New Christians'] || latest.new_christians || 0,
                  youth_attendance: latest['Youth Attendance'] || latest.youth_attendance || 0,
                  kids_total: latest['Kids Total'] || latest.kids_total || 0,
                  connect_groups: latest['Connect Groups'] || latest.connect_groups || 0
                };
              }
              
              console.log('🎯 Updating stat cards for new campus with:', statData);
              updateStatsDisplay(statData, data.encouragements || []);
            })
            .catch((error) => {
              console.error('❌ Error fetching stats for new campus:', error);
            });
        }
      } else if (data.campus === null) {
        // Handle case where no campus was detected
        console.log(`No campus detected - prompting user to select campus`);
        updateCampus(''); // Set to "No campus selected"
      } else {
        console.log(`No campus update needed - campus is ${data.campus}, current is ${currentCampus}`);
      }
      
      // Update stats if provided - now using flat stats object
      if (data.stats && Object.keys(data.stats).length > 0) {
        console.log('📊 Updating stats display with:', data.stats);
        // Use insights array if available, otherwise fall back to text
        const insights = data.insights || (data.text ? [data.text] : []);
        updateStatsDisplay(data.stats, insights);
        showStatsAnimation();
      }
      
      // Handle audio response - prioritize ElevenLabs over browser TTS
      if (data.audio_url) {
        console.log('🎤 Playing ElevenLabs audio:', data.audio_url);
        await playAudioResponse(data.audio_url);
      } else if (data.text) {
        console.log('🎤 Using browser TTS for:', data.text);
        await speakText(data.text);
      } else {
        // FIXED: No auto-listening - user must click again
        setTimeout(() => {
          setState('idle', 'Click orb again to continue!');
        }, 3000);
      }
      
      // Update session info
      if (data.session_summary) {
        updateSessionInfo(data.session_summary);
      }

    } catch (error) {
      console.error('❌ Voice processing error:', error);
      showError('Sorry, there was a problem processing your request. Please try again.');
      setState('idle');
      // FIXED: Removed auto-scheduling - user must click again
    }
  }

  // Text-to-speech function using browser's speech synthesis
  async function speakText(text) {
    if (!text) return;
    
    try {
      // Check if speech synthesis is available
      if (!window.speechSynthesis) {
        console.warn('Speech synthesis not available');
        return;
      }
      
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      // Create speech utterance
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9; // Slightly slower for clarity
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      
      // Try to use a good voice
      const voices = window.speechSynthesis.getVoices();
      const preferredVoice = voices.find(voice => 
        voice.lang.includes('en') && (voice.name.includes('Google') || voice.name.includes('Samantha'))
      );
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      
      // Set up event handlers
      utterance.onstart = () => {
        isPlayingAudio = true;
        console.log('🎤 Speaking:', text);
      };
      
      utterance.onend = () => {
        isPlayingAudio = false;
        setState('idle', 'Listening again...');
        // Auto-restart listening after a short delay
        setTimeout(() => {
          startListening();
        }, 1000);
      };
      
      utterance.onerror = (event) => {
        isPlayingAudio = false;
        console.error('Speech synthesis error:', event);
        setState('idle');
      };
      
      // Speak the text
      window.speechSynthesis.speak(utterance);
      
    } catch (error) {
      console.error('Speech synthesis error:', error);
      setState('idle');
    }
  }

  // Enhanced audio handling with queue management (PRESERVED)
  async function playAudioResponse(audioUrl) {
    try {
      const audio = new Audio(audioUrl);
      audio.preload = 'auto';
      
      // Better audio loading handling
      await new Promise((resolve, reject) => {
        audio.addEventListener('canplaythrough', resolve);
        audio.addEventListener('error', reject);
        audio.load();
        
        // Timeout for slow loading
        setTimeout(() => reject(new Error('Audio loading timeout')), 10000);
      });

      // Play audio with user gesture fallback
      try {
        await audio.play();
        isPlayingAudio = true;
      } catch (playError) {
        console.warn('Audio autoplay blocked:', playError);
        // Show click-to-play option
        if (statusText) {
          statusText.innerHTML = `${statusText.textContent} <span style="color: #ffa500; cursor: pointer; text-decoration: underline;" onclick="this.parentElement.click()">🔊 Click to hear</span>`;
        }
        
        const playOnClick = () => {
          audio.play();
          if (statusText) {
            statusText.innerHTML = statusText.textContent.split('🔊')[0];
          }
          document.removeEventListener('click', playOnClick);
        };
        document.addEventListener('click', playOnClick, { once: true });
      }
      
      audio.onended = () => {
        isPlayingAudio = false;
        setState('idle', 'Listening again...');
        // Auto-restart listening after a short delay
        setTimeout(() => {
          startListening();
        }, 1000);
      };
      
      audio.onerror = () => {
        isPlayingAudio = false;
        console.error('Audio playback error');
        setState('idle');
        // FIXED: Removed auto-listening restart
      };

    } catch (error) {
      console.error('Audio handling error:', error);
      setState('idle');
      // FIXED: Removed auto-listening restart
    }
  }

  // REMOVED: scheduleNextListening function entirely (FIXED)

  // Enhanced start listening with better device detection (PRESERVED but NO AUTO-RESTART)
  async function startListening() {
    // Play greeting the first time the orb is clicked
    if (!greeted) {
      greeted = true;
      try {
        // Try to fetch and play ElevenLabs greeting audio
        const greetingAudioUrl = '/api/greeting_audio';
        await playAudioResponse(greetingAudioUrl);
        setTimeout(() => {
          startListening();
        }, 2000); // Adjust timing as needed
        return;
      } catch (err) {
        // Fallback to browser TTS if fetch fails
        await speakText("Connected to Futures Link, how can I help you today?");
        setTimeout(() => {
          startListening();
        }, 2000);
        return;
      }
    }
    // Don't start listening if text input is open
    const textInputPanel = document.getElementById('text-input-panel');
    if (textInputPanel) {
      console.log('Text input is open, not starting voice recognition');
      return;
    }
    
    if (!recognition) {
      showError('Speech recognition not available.');
      return;
    }
    
    if (recognitionIsRunning || isPlayingAudio) {
      console.log('🎤 Recognition already active or audio playing');
      return;
    }

    // Check if devices exist first
    const hasAudioDevices = await detectAudioDevices();
    if (!hasAudioDevices) {
      showError('No microphone detected.');
      return;
    }

    // Check microphone permission
    const hasPermission = await requestMicrophonePermission();
    if (!hasPermission) {
      showError('Microphone unavailable.');
      return;
    }

    try {
      recognition.start();
    } catch (error) {
      if (error.name === 'InvalidStateError') {
        console.warn('🎤 Recognition already active');
      } else {
        console.error('🎤 Failed to start recognition:', error);
        showError('Voice recognition failed.');
      }
    }
  }

  // Enhanced campus management (PRESERVED)
  function updateCampus(campus) {
    console.log(`updateCampus called with: ${campus}`);
    currentCampus = campus;

    // Update the campus dropdown
    const campusDropdown = document.getElementById('campusDropdown');
    console.log(`Found campusDropdown element: ${campusDropdown ? 'yes' : 'no'}`);
    
    if (campusDropdown) {
      console.log(`Current dropdown value: ${campusDropdown.value}`);
      console.log(`Available options:`, Array.from(campusDropdown.options).map(opt => opt.value));
      
      // Map backend campus names to dropdown values
      const campusMapping = {
        'south': 'South',
        'north': 'North', 
        'east': 'East',
        'west': 'West',
        'paradise': 'Paradise',
        'adelaide_city': 'Adelaide City',
        'salisbury': 'Salisbury',
        'clare_valley': 'Clare Valley',
        'mount_barker': 'Mount Barker',
        'victor_harbour': 'Victor Harbour',
        'copper_coast': 'Copper Coast',
        'online': 'Online'
      };
      
      let dropdownValue;
      if (!campus || campus === '') {
        dropdownValue = ''; // "No campus selected"
      } else {
        dropdownValue = campusMapping[campus] || campus;
      }
      
      console.log(`Mapping campus '${campus}' to dropdown value '${dropdownValue}'`);
      
      // Check if the value exists in the dropdown
      const optionExists = Array.from(campusDropdown.options).some(opt => opt.value === dropdownValue);
      console.log(`Option '${dropdownValue}' exists in dropdown: ${optionExists}`);
      
      campusDropdown.value = dropdownValue;
      console.log(`Updated campus dropdown to: ${campusDropdown.value}`);
      
      // Verify the change took effect
      setTimeout(() => {
        console.log(`Dropdown value after update: ${campusDropdown.value}`);
      }, 100);
    } else {
      console.error('campusDropdown element not found!');
    }

    // Visual feedback for campus change
    if (campus && campus !== '') {
      showSuccess(`Switched to ${campus} campus`);
    } else {
      showSuccess(`No campus selected`);
    }

    // Load campus-specific data
  }

  // Enhanced stats display with animations (PRESERVED)
  function updateStatsDisplay(stats, insights) {
    // Remove any existing stat tags (e.g., "Steady Growth")
    statCards.forEach(card => {
      const tag = card.querySelector('.stat-tag');
      if (tag) tag.remove();
    });

    // Directly update each stat card by ID and key
    const statAttendance = document.getElementById('stat-attendance');
    if (statAttendance) {
      let attValue = stats['Total Attendance'] ?? stats.total_attendance ?? '–';
      statAttendance.textContent = attValue !== undefined && attValue !== null && attValue !== '' ? attValue : '–';
    }

    const statNewPeople = document.getElementById('stat-new-people');
    if (statNewPeople) {
      let value = stats['New People'] ?? stats.new_people ?? '–';
      statNewPeople.textContent = value !== undefined && value !== null && value !== '' ? value : '–';
    }

    const statNewChristians = document.getElementById('stat-new-christians');
    if (statNewChristians) {
      let value = stats['New Christians'] ?? stats.new_christians ?? '–';
      statNewChristians.textContent = value !== undefined && value !== null && value !== '' ? value : '–';
    }

    const statYouth = document.getElementById('stat-youth');
    if (statYouth) {
      let value = stats['Youth Attendance'] ?? stats.youth_attendance ?? '–';
      statYouth.textContent = value !== undefined && value !== null && value !== '' ? value : '–';
    }

    const statKids = document.getElementById('stat-kids');
    if (statKids) {
      let value = stats['Kids Total'] ?? stats.kids_total ?? '–';
      statKids.textContent = value !== undefined && value !== null && value !== '' ? value : '–';
    }

    const statConnect = document.getElementById('stat-connect');
    if (statConnect) {
      let value = stats['Connect Groups'] ?? stats.connect_groups ?? '–';
      statConnect.textContent = value !== undefined && value !== null && value !== '' ? value : '–';
    }

    // (Optional) Display insights if provided (leave your existing code for insights here)
    const insightsPanel = document.querySelector('.insights-panel');
    const encouragementsList = document.getElementById('encouragements');
    if (!insightsPanel || !encouragementsList) return;

    // If no campus or no stats, clear/hide insights
    if (!stats || !Object.keys(stats).length || !currentCampus) {
      encouragementsList.innerHTML = '';
      insightsPanel.style.display = 'none';
      return;
    }

    // If insights are present, show them in a 2-column layout
    if (Array.isArray(insights) && insights.length > 0) {
      // Create a 2-column grid layout for insights
      encouragementsList.innerHTML = `
        <div style="
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 15px;
          width: 100%;
          height: 100%;
          align-items: center;
        ">
          ${insights.map((insight, index) => `
            <div class="insight-item" style="
              border-radius: 8px; 
              padding: 12px 16px; 
              color: #0ea5e9; 
              font-size: 0.9rem; 
              background: rgba(14, 165, 233, 0.1);
              border: 1px solid rgba(14, 165, 233, 0.2);
              text-align: center;
              line-height: 1.3;
              font-weight: 500;
              display: flex;
              align-items: center;
              justify-content: center;
              height: 100%;
              max-width: 100%;
              overflow: hidden;
              text-overflow: ellipsis;
            ">📊 ${insight}</div>
          `).join('')}
        </div>
      `;
      insightsPanel.style.display = '';
    } else {
      encouragementsList.innerHTML = '';
      insightsPanel.style.display = '';
    }
  }

  // Smooth number animation (PRESERVED)
  function animateNumberChange(element, newValue) {
    const currentValue = parseInt(element.textContent) || 0;
    const duration = 1000;
    const steps = 30;
    const stepValue = (newValue - currentValue) / steps;
    let currentStep = 0;

    const animate = () => {
      currentStep++;
      const value = Math.round(currentValue + (stepValue * currentStep));
      element.textContent = value;
      
      if (currentStep < steps) {
        requestAnimationFrame(animate);
      } else {
        element.textContent = newValue;
      }
    };

    if (newValue !== currentValue) {
      animate();
    }
  }

  // Stats animation effect (PRESERVED)
  function showStatsAnimation() {
    statCards.forEach((card, index) => {
      setTimeout(() => {
        card.style.transform = 'scale(1.05)';
        card.style.boxShadow = '0 15px 35px rgba(0, 212, 255, 0.3)';
        
        setTimeout(() => {
          card.style.transform = '';
          card.style.boxShadow = '';
        }, 300);
      }, index * 100);
    });
  }

  // Update stats display with real Google Sheets data (PRESERVED)
  function updateStatsDisplayWithRealData(stats, campus) {
    const statMappings = {
      'total_attendance': { id: 'totalAttendance', label: 'Total Attendance' },
      'new_people': { id: 'newPeople', label: 'New People' },
      'new_christians': { id: 'newChristians', label: 'New Christians' },
      'youth_attendance': { id: 'youthAttendance', label: 'Youth Total' },
      'kids_total': { id: 'kidsTotal', label: 'Kids Ministry' },
      'connect_groups': { id: 'connectGroups', label: 'Connect Groups' }
    };

    Object.entries(statMappings).forEach(([key, mapping]) => {
      const element = document.getElementById(mapping.id);
      const value = stats[key];
      
      if (element && value !== undefined && value !== null) {
        // Enable inline editing before animating number change
        element.contentEditable = "true";
        // Animate number change
        animateNumberChange(element, parseInt(value) || 0);
      }
    });

    // Update page title to show current campus
    if (campus) {
      document.title = `Futures Link - ${campus} Campus`;
    }
  }

  // Enhanced session management (PRESERVED)
  async function fetchSessionData() {
    try {
      const response = await fetch('/api/session');
      if (response.ok) {
        const data = await response.json();
        updateSessionInfo(data.summary);
        if (data.current_campus) {
          updateCampus(data.current_campus);
        }
      }
    } catch (error) {
      console.warn('Failed to fetch session data:', error);
    }
  }

  function updateSessionInfo(summary) {
    if (summary && summary !== 'No stats logged this session yet.') {
      console.log('📊 Session update:', summary);
    }
  }

  // OPTIMIZED performance monitoring for particles
  function adjustParticleDensity() {
    const performanceNow = performance.now();
    const fps = 1000 / (performanceNow - (window.lastFrameTime || performanceNow));
    window.lastFrameTime = performanceNow;
    
    // FIXED: More aggressive particle reduction if FPS is low
    if (fps < 30 && particlesContainer && particlesContainer.children.length > 10) {
      const excessParticles = Array.from(particlesContainer.children).slice(0, 8); // Increased cleanup
      excessParticles.forEach(particle => particle.remove());
    }
  }

  // Monitor performance every few seconds (OPTIMIZED)
  setInterval(adjustParticleDensity, 5000); // Increased interval

  // Health check and auto-recovery (PRESERVED)
  async function performHealthCheck() {
    try {
      const response = await fetch('/api/health');
      const health = await response.json();
      
      if (health.status !== 'ok') {
        console.warn('⚠️ System health issue:', health);
        showError('System experiencing issues. Some features may be limited.');
      }
    } catch (error) {
      console.warn('Health check failed:', error);
    }
  }

  // Add loadFilteredStats function for filtering stats by campus only (date range disabled)
  async function loadFilteredStats() {
    const campus = document.getElementById('campusSelect')?.value;

    let url = '/api/stats?';
    if (campus) url += `campus=${encodeURIComponent(campus)}&`;

    const response = await fetch(url);
    const data = await response.json();

    if (!data.stats || data.stats.length === 0) {
      alert("No stats found for that range.");
      return;
    }

    // Show the most recent stat row for the selected campus
    const latest = data.stats[0];
    // Pass encouragements if present
    updateStatsDisplay({
      total_attendance: latest['Total Attendance'] || latest.total_attendance || 0,
      new_people: latest['New People'] || latest.new_people || 0,
      new_christians: latest['New Christians'] || latest.new_christians || 0,
      youth_attendance: latest['Youth Attendance'] || latest.youth_attendance || 0,
      kids_total: latest['Kids Total'] || latest.kids_total || 0,
      connect_groups: latest['Connect Groups'] || latest.connect_groups || 0
    }, data.encouragements || []);
  }

  // Make loadFilteredStats globally available (PRESERVED)
  window.loadFilteredStats = loadFilteredStats;

  // --- Show all stat/insight queries in a styled box like annual review ---
  function showQueryBox({text, stats, insights, report}) {
    // Remove any existing query box
    let oldBox = document.getElementById('query-result-panel');
    if (oldBox) oldBox.remove();

    // Compose the box content (styled like annual review)
    let html = `<style>
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
      }
    </style>
    <div id="query-result-panel" style="
      background: rgba(15, 20, 40, 0.85);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(0, 212, 255, 0.18);
      border-radius: 18px;
      padding: 14px 8px 24px 8px;
      margin: 0 0 32px 0;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
      overflow-x: auto;
      width: 100%;
      max-width: 100vw;
      position: relative;
      z-index: 100;
      animation: fadeIn 0.3s ease-out;
    ">
      <button onclick="closeQueryBox()" style="
        position: absolute;
        top: 10px;
        right: 14px;
        background: none;
        border: none;
        color: #00d4ff;
        font-size: 1.3rem;
        font-weight: bold;
        cursor: pointer;
        z-index: 10;
        padding: 0 6px;
        line-height: 1;
        opacity: 0.7;
        transition: opacity 0.2s;
      " onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'" aria-label="Close">×</button>
      <h3 style="
        color: #00d4ff;
        font-size: 1.2rem;
        margin: 0 0 12px 0;
        text-align: center;
        font-weight: 700;
        letter-spacing: -0.5px;
      ">📊 Query Results</h3>`;
    if (text) {
      html += `<div style="color:#22c55e;font-size:1.1rem;text-align:center;margin-bottom:10px;font-weight:600;">${text}</div>`;
    }
    if (report) {
      html += renderReportTable(report);
    } else if (stats && Object.keys(stats).length > 0) {
      html += `<div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-bottom:10px;">`;
      Object.entries(stats).forEach(([key, value]) => {
        html += `<div style="background:rgba(0,212,255,0.08);border-radius:8px;padding:10px 18px;font-size:1rem;color:#00d4ff;font-weight:600;min-width:120px;text-align:center;">${key.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}: <span style='color:#22c55e;'>${value}</span></div>`;
      });
      html += `</div>`;
    }
    if (insights && insights.length > 0) {
      html += `<div style="margin-top:10px;">${insights.map(i=>`<div style='color:#0ea5e9;font-size:0.95rem;margin-bottom:4px;'>${i}</div>`).join('')}</div>`;
    }
    html += `</div>`;

    // Insert the box at the top of .main-content (like annual review)
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
      mainContent.insertAdjacentHTML('afterbegin', html);
    }
  }
  window.closeQueryBox = function() {
    let box = document.getElementById('query-result-panel');
    if (box) box.remove();
  };

  // Cleanup on page unload (PRESERVED)
  window.addEventListener('beforeunload', () => {
    if (recognition && recognitionIsRunning) {
      recognition.stop();
    }
    if (particleInterval) {
      clearInterval(particleInterval);
    }
    if (dataRefreshInterval) {
      clearInterval(dataRefreshInterval);
    }
  });

  // Add encouragement override style and improved box style for encouragements
  function addEncouragementOverrideStyle() {
    // Remove any previous override style if present
    const prev = document.getElementById('encouragements-override-style');
    if (prev) prev.remove();
    const style = document.createElement('style');
    style.id = 'encouragements-override-style';
    style.innerHTML = `
      .encouragements-list div,
      .encouragements-list div:hover,
      .encouragements-list div:focus,
      .encouragements-list div:active,
      .encouragement-override,
      .encouragement-override:hover,
      .encouragement-override:focus,
      .encouragement-override:active {
        background: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
        border: none !important;
        cursor: default !important;
        user-select: none !important;
        -webkit-tap-highlight-color: transparent !important;
        -webkit-box-shadow: none !important;
      }
      /* Improved encouragements-list box style to ensure text fits cleanly */
      .encouragements-list div {
        max-width: 100%;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        text-align: center;
        padding: 0.5rem 1rem;
        box-sizing: border-box;
      }
    `;
    document.body.appendChild(style);
  }

  // Initialize everything (FIXED - removed auto-listening)
  function initialize() {
    console.log('🎤 Speech recognition:', recognition ? 'Available' : 'Not supported');
    console.log('🔮 Orb system:', orbWrapper ? 'Initialized' : 'Not found');
    console.log('✨ Enhanced particles:', particlesContainer ? 'Ready' : 'Not found');
    
    // Debug: Check if stat elements exist on page load
    console.log('🔍 Checking stat elements on page load:');
    const statElementIds = ['stat-attendance', 'stat-new-people', 'stat-new-christians', 'stat-youth', 'stat-kids', 'stat-connect'];
    statElementIds.forEach(id => {
      const element = document.getElementById(id);
      console.log(`  ${id}: ${element ? '✅ Found' : '❌ Not found'}`);
    });
    
    setState('idle', 'Click orb for voice, or Ctrl+T for text');
    updateConnectionStatus();
    // Add override style for encouragements after all other styles
    addEncouragementOverrideStyle();
    
    // Add event listeners
    if (orbContainer) {
      orbContainer.addEventListener('click', () => {
        // Don't start listening if text input is open
        const textInputPanel = document.getElementById('text-input-panel');
        if (textInputPanel) {
          console.log('Text input is open, ignoring orb click');
          return;
        }
        
        if (currentState === 'idle') {
          startListening();
        }
      });
      orbContainer.addEventListener('dblclick', showTextInputOption);
    }

    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.key.toLowerCase() === 't') {
        e.preventDefault();
        showTextInputOption();
      }
    });

    if (campusSelect) {
      campusSelect.addEventListener('change', (e) => {
        currentCampus = e.target.value;
        // On campus change, fetch and update stats and encouragements from backend only.
        fetch('/api/stats?campus=' + encodeURIComponent(currentCampus))
          .then(response => response.json())
          .then(data => {
            // Always update stat cards, even if no stats found
            let statData = {
              total_attendance: 0,
              new_people: 0,
              new_christians: 0,
              youth_attendance: 0,
              kids_total: 0,
              connect_groups: 0
            };
            if (data.stats) {
              statData = {
                total_attendance: data.stats['Total Attendance'] || data.stats.total_attendance || 0,
                new_people: data.stats['New People'] || data.stats.new_people || 0,
                new_christians: data.stats['New Christians'] || data.stats.new_christians || 0,
                youth_attendance: data.stats['Youth Attendance'] || data.stats.youth_attendance || 0,
                kids_total: data.stats['Kids Total'] || data.stats.kids_total || 0,
                connect_groups: data.stats['Connect Groups'] || data.stats.connect_groups || 0
              };
            }
            updateStatsDisplay(statData, data.encouragements || []);
          });
      });
    }

    // On campus change, fetch and update stats for the selected campus
    if (campusDropdown) {
      campusDropdown.addEventListener('change', (e) => {
        const selectedCampus = e.target.value;
        console.log('🏫 Campus selected:', selectedCampus);
        
        if (!selectedCampus) {
          // If no campus selected, clear stat cards
          updateStatsDisplay({}, []);
          return;
        }
        
        // Fetch latest stats for the selected campus
        fetch('/api/stats?campus=' + encodeURIComponent(selectedCampus))
          .then(response => response.json())
          .then(data => {
            console.log('📊 Latest stats for', selectedCampus, ':', data);
            
            let statData = {
              total_attendance: 0,
              new_people: 0,
              new_christians: 0,
              youth_attendance: 0,
              kids_total: 0,
              connect_groups: 0
            };
            
            if (data.stats) {
              statData = {
                total_attendance: data.stats['Total Attendance'] || data.stats.total_attendance || 0,
                new_people: data.stats['New People'] || data.stats.new_people || 0,
                new_christians: data.stats['New Christians'] || data.stats.new_christians || 0,
                youth_attendance: data.stats['Youth Attendance'] || data.stats.youth_attendance || 0,
                kids_total: data.stats['Kids Total'] || data.stats.kids_total || 0,
                connect_groups: data.stats['Connect Groups'] || data.stats.connect_groups || 0
              };
            }
            
            console.log('🎯 Updating stat cards with:', statData);
            updateStatsDisplay(statData, data.encouragements || []);
          })
          .catch((error) => {
            console.error('❌ Error fetching stats:', error);
            updateStatsDisplay({}, []);
          });
      });
      
      // On page load, if a campus is already selected, trigger the change event
      if (campusDropdown.value) {
        const event = new Event('change');
        campusDropdown.dispatchEvent(event);
      }
    }

    navItems.forEach(item => {
      item.addEventListener('click', () => {
        navItems.forEach(n => n.classList.remove('active'));
        item.classList.add('active');
        console.log('Switched to section:', item.dataset.section);
        // TODO: Implement actual section switching logic here
      });
    });
    
    // Monitor permission changes
    if (navigator.permissions) {
      navigator.permissions.query({ name: 'microphone' }).then(permission => {
        permission.addEventListener('change', updateConnectionStatus);
      });
    }
    
    fetchSessionData();
    performHealthCheck();
    
    // Periodic health checks
    setInterval(performHealthCheck, 60000); // Every minute
    
    console.log('✅ Enhanced Futures Link Assistant ready!');
    console.log('🎯 Options: Click orb for voice, Ctrl+T for text, double-click for text');
    console.log('🔧 FIXED: No auto-listening, optimized particles, better performance');
  }
    
  // Start the application
  initialize();

  // On page load, fetch the most recent stats from backend and populate stat cards
  // fetch('/api/stats')
  //   .then(response => response.json())
  //   .then(data => {
  //     let statData = {
  //       total_attendance: 0,
  //       new_people: 0,
  //       new_christians: 0,
  //       youth_attendance: 0,
  //       kids_total: 0,
  //       connect_groups: 0
  //     };
  //     if (data.stats && data.stats.length > 0) {
  //       const latest = data.stats[0];
  //       statData = {
  //         total_attendance: latest['Total Attendance'] || latest.total_attendance || 0,
  //         new_people: latest['New People'] || latest.new_people || 0,
  //         new_christians: latest['New Christians'] || latest.new_christians || 0,
  //         youth_attendance: latest['Youth Attendance'] || latest.youth_attendance || 0,
  //         kids_total: latest['Kids Total'] || latest.kids_total || 0,
  //         connect_groups: latest['Connect Groups'] || latest.connect_groups || 0
  //       };
  //     } else {
  //       // Fallback to demo data if no stats found
  //       statData = {
  //         total_attendance: 187,
  //         new_people: 12,
  //         new_christians: 3,
  //         youth_attendance: 27,
  //         kids_total: 41,
  //         connect_groups: 8
  //       };
  //     }
  //     updateStatsDisplay(statData, data.encouragements || []);
  //   })
  //   .catch(() => {
  //     // Fallback to demo data on error
  //     updateStatsDisplay({
  //       total_attendance: 187,
  //       new_people: 12,
  //       new_christians: 3,
  //       youth_attendance: 27,
  //       kids_total: 41,
  //       connect_groups: 8
  //     }, [
  //       'Great growth in attendance this month!',
  //       'Youth group numbers are up 10% from last quarter.'
  //     ]);
  //   });

      // Make key functions globally available for debugging (PRESERVED)
    window.FuturesLink = {
      setState,
      startListening,
      updateCampus,
      showTextInputOption,
      createParticle,
      createParticleBurst,
      createAmbientParticles,
      currentState: () => currentState,
      currentCampus: () => currentCampus,
      particleCount: () => particlesContainer ? particlesContainer.children.length : 0,
      // Add test function for debugging
      testTotalAttendance: () => {
        const element = document.getElementById('stat-attendance');
        if (element) {
          console.log('✅ Found stat-attendance element, setting to 999');
          element.textContent = '999';
          return true;
        } else {
          console.log('❌ stat-attendance element not found');
          return false;
        }
      }
    };

  console.log('🎉 FIXED Futures Link with Optimized Performance loaded!');
  console.log('🔧 Performance improvements: Reduced particles, no auto-listening, better cleanup');

  window.showQueryModal = function(data) {
    console.log('🔍 showQueryModal called with data:', data);
    console.log('🔍 Data keys:', Object.keys(data));
    console.log('🔍 Has comparison:', !!data.comparison);
    console.log('🔍 Has reports:', !!data.reports);
    console.log('🔍 Reports length:', data.reports ? data.reports.length : 'N/A');
    console.log('🔍 Has percent_changes:', !!data.percent_changes);
    
    // Remove any existing modal
    let oldModal = document.getElementById('query-modal');
    if (oldModal) oldModal.remove();

    // Modal overlay
    let modal = document.createElement('div');
    modal.id = 'query-modal';
    modal.style.cssText = `
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(10,18,30,0.85); z-index: 2000; display: flex; align-items: center; justify-content: center; animation: fadeIn 0.2s;`;
    modal.innerHTML = `<style>
      @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      .modal-content { background: #181f2a; border-radius: 18px; box-shadow: 0 8px 32px rgba(0,0,0,0.45); padding: 32px 24px 24px 24px; max-width: 98vw; min-width: 320px; max-height: 90vh; overflow-y: auto; position: relative; }
      .modal-close { position: absolute; top: 18px; right: 22px; background: none; border: none; color: #00d4ff; font-size: 2rem; font-weight: bold; cursor: pointer; opacity: 0.7; transition: opacity 0.2s; z-index: 10; }
      .modal-close:hover { opacity: 1; }
      .comparison-table { width: 100%; border-collapse: collapse; margin-top: 18px; }
      .comparison-table th, .comparison-table td { padding: 10px 8px; text-align: center; font-size: 1rem; }
      .comparison-table th { background: linear-gradient(135deg, #0ea5e9, #00d4ff); color: white; font-weight: 700; }
      .comparison-table td { background: rgba(0,212,255,0.04); color: #e2e8f0; font-weight: 500; }
      .comparison-table .stat-label { text-align: left; font-weight: 600; color: #00d4ff; }
      .comparison-table .percent-up { color: #22c55e; font-weight: 700; }
      .comparison-table .percent-down { color: #ef4444; font-weight: 700; }
      .comparison-table .percent-same { color: #f59e0b; font-weight: 700; }
      .comparison-table .arrow { font-size: 1.1em; margin-right: 2px; }
    </style>
    <div class="modal-content">
      <button class="modal-close" onclick="document.getElementById('query-modal').remove()" aria-label="Close">×</button>
      <h2 style="color:#00d4ff;text-align:center;font-size:1.4rem;font-weight:700;margin-bottom:10px;">${data.text ? data.text : 'Query Results'}</h2>
      <div style="margin-bottom:10px;text-align:center;color:#22c55e;font-size:1.1rem;font-weight:600;">${data.question ? data.question : ''}</div>
      <div id="modal-body-content"></div>
    </div>`;
    document.body.appendChild(modal);

    // Render content
    let body = modal.querySelector('#modal-body-content');
    
    console.log('🔍 Checking comparison conditions...');
    console.log('🔍 data.comparison:', data.comparison);
    console.log('🔍 Array.isArray(data.reports):', Array.isArray(data.reports));
    console.log('🔍 data.reports.length === 2:', data.reports ? data.reports.length === 2 : 'N/A');
    console.log('🔍 data.percent_changes:', !!data.percent_changes);
    
    if (data.comparison && Array.isArray(data.reports) && data.reports.length === 2 && data.percent_changes) {
      console.log('✅ Comparison conditions met, rendering comparison table');
      // Side-by-side comparison table
      const years = data.years;
      const reports = data.reports;
      const percentChanges = data.percent_changes;
      
      console.log('🔍 Years:', years);
      console.log('🔍 Reports:', reports);
      console.log('🔍 Percent changes:', percentChanges);
      
      // Collect all stat labels
      let statMap = {};
      reports.forEach((rep, i) => {
        console.log(`🔍 Processing report ${i}:`, rep);
        (rep.report || []).forEach(row => {
          statMap[row.stat] = row.label;
        });
      });
      
      console.log('🔍 Stat map:', statMap);
      const statKeys = Object.keys(statMap);
      
      let table = `<table class="comparison-table"><thead><tr><th class="stat-label">Stat</th><th>${years[0]}</th><th>${years[1]}</th><th>Change</th></tr></thead><tbody>`;
      
      statKeys.forEach(stat => {
        const label = statMap[stat];
        const row1 = (reports[0].report || []).find(r => r.stat === stat);
        const row2 = (reports[1].report || []).find(r => r.stat === stat);
        const val1 = row1 ? row1.total : '-';
        const val2 = row2 ? row2.total : '-';
        let pct = percentChanges[stat];
        let pctCell = '';
        
        if (pct === null || pct === undefined) {
          pctCell = '<span class="percent-same">–</span>';
        } else if (pct > 0.01) {
          pctCell = `<span class="percent-up"><span class="arrow">▲</span>${pct.toFixed(1)}%</span>`;
        } else if (pct < -0.01) {
          pctCell = `<span class="percent-down"><span class="arrow">▼</span>${pct.toFixed(1)}%</span>`;
        } else {
          pctCell = `<span class="percent-same">0%</span>`;
        }
        
        table += `<tr><td class="stat-label">${label}</td><td>${val1}</td><td>${val2}</td><td>${pctCell}</td></tr>`;
      });
      
      table += '</tbody></table>';
      body.innerHTML = table;
      console.log('✅ Comparison table rendered');
      
    } else if (data.report) {
      console.log('✅ Rendering report table');
      // Fallback to existing report table
      body.innerHTML = renderReportTable(data.report);
    } else if (data.stats && Object.keys(data.stats).length > 0) {
      console.log('✅ Rendering stat cards');
      // Fallback to stat cards
      body.innerHTML = Object.entries(data.stats).map(([key, value]) => `<div style="background:rgba(0,212,255,0.08);border-radius:8px;padding:10px 18px;font-size:1rem;color:#00d4ff;font-weight:600;min-width:120px;text-align:center;display:inline-block;margin:4px;">${key.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}: <span style='color:#22c55e;'>${value}</span></div>`).join('');
    } else {
      console.log('⚠️ No recognized data format, showing text only');
      body.innerHTML = '<div style="text-align:center;color:#e2e8f0;font-size:1.1rem;">No data available for this query.</div>';
    }
    
    if (data.insights && data.insights.length > 0) {
      body.innerHTML += `<div style="margin-top:10px;">${data.insights.map(i=>`<div style='color:#0ea5e9;font-size:0.95rem;margin-bottom:4px;'>${i}</div>`).join('')}</div>`;
    }
    
    console.log('✅ Modal rendered successfully');
  };

  // NANITE ORB PARTICLE ANIMATION
  (function() {
    const canvas = document.getElementById('nanite-orb');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Responsive sizing
    function resizeCanvas() {
      const dpr = window.devicePixelRatio || 1;
      const size = Math.min(canvas.parentElement.offsetWidth, canvas.parentElement.offsetHeight);
      canvas.width = size * dpr;
      canvas.height = size * dpr;
      canvas.style.width = size + 'px';
      canvas.style.height = size + 'px';
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Parameters
    const PARTICLE_COUNT = 72;
    const ORB_RADIUS = 140;
    const PARTICLE_BASE_SIZE = 4;
    const PARTICLE_GLOW = 18;
    const CENTER_FORCE = 0.07;
    const REPULSION = 0.13;
    const DRIFT = 0.09;
    const COLOR_SPEED = 0.002;

    // Particle class
    class Particle {
      constructor(i) {
        const angle = (i / PARTICLE_COUNT) * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1); // Spherical
        this.base = {
          r: ORB_RADIUS * (0.82 + 0.18 * Math.random()),
          theta: angle,
          phi: phi
        };
        this.r = this.base.r;
        this.theta = this.base.theta;
        this.phi = this.base.phi;
        this.size = PARTICLE_BASE_SIZE * (0.7 + 0.6 * Math.random());
        this.colorSeed = Math.random();
        this.vr = 0;
        this.vtheta = 0;
        this.vphi = 0;
      }
      update(particles, t, listening) {
        // Orbit motion
        this.theta += 0.008 + 0.002 * Math.sin(t + this.colorSeed * 10);
        this.phi += 0.002 * Math.cos(t + this.colorSeed * 7);
        // Center attraction
        this.r += (this.base.r - this.r) * CENTER_FORCE;
        // Repulsion
        for (let p of particles) {
          if (p === this) continue;
          const dx = this.x - p.x;
          const dy = this.y - p.y;
          const dist = Math.sqrt(dx*dx + dy*dy);
          if (dist < 18) {
            this.r += REPULSION * (18 - dist) * 0.1;
          }
        }
        // Random drift
        this.r += (Math.random() - 0.5) * DRIFT;
        // Listening pulse
        if (listening) {
          this.size += Math.sin(t * 4 + this.colorSeed * 10) * 0.12;
        }
      }
      get x() {
        return this.r * Math.sin(this.phi) * Math.cos(this.theta);
      }
      get y() {
        return this.r * Math.sin(this.phi) * Math.sin(this.theta);
      }
      get z() {
        return this.r * Math.cos(this.phi);
      }
      draw(ctx, cx, cy, t) {
        // 3D to 2D projection
        const perspective = 0.7 + 0.3 * (this.z / ORB_RADIUS);
        const px = cx + this.x * perspective;
        const py = cy + this.y * perspective;
        // Color cycling
        const hue = (t * 40 + this.colorSeed * 360) % 360;
        ctx.save();
        ctx.globalAlpha = 0.7 + 0.3 * (this.z / ORB_RADIUS);
        ctx.beginPath();
        ctx.arc(px, py, this.size, 0, Math.PI * 2);
        ctx.closePath();
        ctx.shadowColor = `hsl(${hue}, 100%, 65%)`;
        ctx.shadowBlur = PARTICLE_GLOW;
        ctx.fillStyle = `hsl(${hue}, 100%, 60%)`;
        ctx.fill();
        ctx.restore();
      }
    }

    // Particle system
    let particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(new Particle(i));
    }

    // Animation loop
    function animate() {
      resizeCanvas();
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const t = performance.now() * COLOR_SPEED;
      const cx = canvas.width / (2 * (window.devicePixelRatio || 1));
      const cy = canvas.height / (2 * (window.devicePixelRatio || 1));
      // Placeholder: listening state (can be set from outside)
      const listening = window.naniteOrbListening || false;
      for (let p of particles) {
        p.update(particles, t, listening);
      }
      // Sort by z for depth
      particles.sort((a, b) => a.z - b.z);
      for (let p of particles) {
        p.draw(ctx, cx, cy, t);
      }
      requestAnimationFrame(animate);
    }
    animate();

    // Optional: add hover/click/touch interaction for scatter/regroup
    let scattered = false;
    canvas.addEventListener('pointerdown', () => {
      if (!scattered) {
        for (let p of particles) {
          p.r += 40 + 40 * Math.random();
        }
        scattered = true;
        setTimeout(() => { scattered = false; }, 900);
      }
    });
  })();

  // --- tsparticles nanite orb ---
  (function() {
    if (!window.tsParticles) return;
    window.tsParticles.load('tsparticles-orb', {
      fullScreen: { enable: false },
      background: { color: 'transparent' },
      fpsLimit: 60,
      particles: {
        number: { value: 80, density: { enable: false } },
        color: { value: ["#00d4ff", "#7f5fff", "#ff7ee0", "#00fff0"] },
        shape: { type: "circle" },
        opacity: { value: 0.7, anim: { enable: true, speed: 0.8, opacity_min: 0.4, sync: false } },
        size: { value: 5, random: { enable: true, minimumValue: 2 }, anim: { enable: true, speed: 2, size_min: 2, sync: false } },
        links: { enable: false },
        move: {
          enable: true,
          speed: 1.2,
          direction: "none",
          random: true,
          straight: false,
          outModes: { default: "bounce" },
          attract: { enable: true, rotateX: 1200, rotateY: 1200 }
        },
        shadow: {
          enable: true,
          color: "#00d4ff",
          blur: 12
        },
        zIndex: { value: 10 }
      },
      interactivity: {
        detectsOn: "canvas",
        events: {
          onHover: { enable: true, mode: "bubble" },
          onClick: { enable: true, mode: "repulse" },
          resize: true
        },
        modes: {
          bubble: { distance: 80, size: 8, duration: 0.4, opacity: 1 },
          repulse: { distance: 120, duration: 0.6 }
        }
      },
      detectRetina: true,
      style: {
        position: 'absolute',
        left: 0,
        top: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 21
      }
    });
  })();

  // --- Minimal tsparticles orb ---
  document.addEventListener('DOMContentLoaded', function() {
    if (!window.tsParticles) return;
    window.tsParticles.load('tsparticles-orb', {
      fullScreen: { enable: false },
      background: { color: 'transparent' },
      particles: {
        number: { value: 60 },
        color: { value: ["#00d4ff", "#7f5fff", "#ff7ee0", "#00fff0"] },
        shape: { type: "circle" },
        opacity: { value: 0.7 },
        size: { value: 5, random: { enable: true, minimumValue: 2 } },
        move: { enable: true, speed: 1.2, random: true, attract: { enable: true, rotateX: 1200, rotateY: 1200 } },
        shadow: { enable: true, color: "#00d4ff", blur: 12 }
      },
      detectRetina: true
    });
  });
});

// Add global closeAnnualReview function
window.closeAnnualReview = function() {
  const panel = document.getElementById('annual-review-panel');
  if (panel) {
    panel.style.display = 'none';
  }
};