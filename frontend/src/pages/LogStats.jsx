import React, { useState, useEffect, useRef } from 'react';
import { MicrophoneIcon, PaperAirplaneIcon, XMarkIcon, PlayIcon, SpeakerWaveIcon, PlusIcon, CalendarIcon } from '@heroicons/react/24/outline';
import DynamicBackground from '../components/DynamicBackground';
import ThreeParticleEffect from '../components/ThreeParticleEffect';

const LogStats = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showResponse, setShowResponse] = useState(false);
  const [selectedCampus, setSelectedCampus] = useState('');
  const [campuses, setCampuses] = useState([]);
  const [audioUrl, setAudioUrl] = useState('');
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [loggedStats, setLoggedStats] = useState({});
  const [missingStats, setMissingStats] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [sessionStats, setSessionStats] = useState([]);
  const [showQuickInput, setShowQuickInput] = useState(false);
  const [quickInputDate, setQuickInputDate] = useState('');
  const [quickInputStats, setQuickInputStats] = useState({
    'Sunday Total': '',
    'New People': '',
    'Salvations': '',
    'Kids Total': '',
    'New Kids': '',
    'Kids Salvations': '',
    'Youth Total': '',
    'Youth NP': '',
    'Youth Salvations': '',
    'Connect Groups': '',
    'Baptisms': ''
  });
  const [isSubmittingQuickInput, setIsSubmittingQuickInput] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const audioRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Load campuses
    fetch('/api/campuses', {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        if (data.campuses) {
          setCampuses(data.campuses);
          // Set the default campus from the API response
          if (data.default) {
            setSelectedCampus(data.default);
          } else if (data.campuses.length > 0) {
            setSelectedCampus(data.campuses[0].id);
          }
        }
      })
      .catch(err => console.error('Error loading campuses:', err));

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => {
        setIsRecording(true);
        setTranscript('');
      };

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        setTranscript(finalTranscript || interimTranscript);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
        if (transcript.trim()) {
          processVoiceInput();
        }
      };
    }
  }, []);

  const startRecording = () => {
    setIsRecording(true);
    setTranscript('');
    setResponse('');
    setShowResponse(false);
    setAudioUrl('');
    setLoggedStats({});
    setMissingStats([]);
    setSuggestions([]);
    
    try {
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (transcript.trim()) {
      processVoiceInput();
    }
  };

  const processVoiceInput = async () => {
    if (!transcript.trim()) return;
    
    setIsProcessing(true);
    try {
      const response = await fetch('/api/process_voice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          text: transcript,
          campus: selectedCampus
        }),
      });
      
      // Check if we got redirected to login
      if (response.redirected || response.status === 302) {
        setResponse('Please log in to use voice logging. Redirecting to login...');
        setShowResponse(true);
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
        return;
      }
      
      // Check for other error status codes
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          setResponse('Authentication required. Please log in.');
          setShowResponse(true);
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
          return;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success !== false) {
        setResponse(data.text || data.response || 'Stats logged successfully!');
        setShowResponse(true);
        setTranscript('');
        
        // Handle audio response
        if (data.audio_url) {
          setAudioUrl(data.audio_url);
        }
        
        // Handle logged stats
        if (data.stats) {
          setLoggedStats(data.stats);
        }
        
        // Handle missing stats
        if (data.missing_stats) {
          setMissingStats(data.missing_stats);
        }
        
        // Handle suggestions
        if (data.suggestions) {
          setSuggestions(data.suggestions);
        }
        
        // Update session stats
        if (data.session_stats) {
          setSessionStats(data.session_stats);
        }
      } else {
        setResponse(data.error || 'Failed to process voice input');
        setShowResponse(true);
      }
    } catch (error) {
      console.error('Error processing voice input:', error);
      if (error.message.includes('Unexpected token')) {
        setResponse('Authentication error. Please log in to continue.');
        setShowResponse(true);
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        setResponse(`Error processing voice input: ${error.message}`);
        setShowResponse(true);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const playAudio = () => {
    if (audioUrl) {
      setIsPlayingAudio(true);
      const audio = new Audio(audioUrl);
      audio.onended = () => setIsPlayingAudio(false);
      audio.onerror = () => setIsPlayingAudio(false);
      audio.play().catch(err => {
        console.error('Error playing audio:', err);
        setIsPlayingAudio(false);
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (transcript.trim()) {
      processVoiceInput();
    }
  };

  const clearResponse = () => {
    setShowResponse(false);
    setResponse('');
    setAudioUrl('');
    setLoggedStats({});
    setMissingStats([]);
    setSuggestions([]);
  };

  const formatStatValue = (value) => {
    if (typeof value === 'number') {
      return value.toLocaleString();
    }
    return value;
  };

  const handleQuickInputSubmit = async () => {
    if (!quickInputDate) {
      alert('Please select a date for the quick input.');
      return;
    }

    setIsSubmittingQuickInput(true);
    try {
      const response = await fetch('/api/quick_input', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          date: quickInputDate,
          stats: quickInputStats,
          campus: selectedCampus
        }),
      });

      if (response.redirected || response.status === 302) {
        setResponse('Please log in to use quick input. Redirecting to login...');
        setShowResponse(true);
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
        return;
      }

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          setResponse('Authentication required. Please log in.');
          setShowResponse(true);
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
          return;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success !== false) {
        // Close the modal
        setShowQuickInput(false);
        
        // Reset form
        setQuickInputDate('');
        setQuickInputStats({
          'Sunday Total': '',
          'New People': '',
          'Salvations': '',
          'Kids Total': '',
          'New Kids': '',
          'Kids Salvations': '',
          'Youth Total': '',
          'Youth NP': '',
          'Youth Salvations': '',
          'Connect Groups': '',
          'Baptisms': ''
        });
        
        // Show success message
        setResponse(data.text || 'Quick input successful!');
        setShowResponse(true);
        
        // Update session stats with the new input
        const newSessionStat = {
          campus: selectedCampus,
          text: `Quick input: ${Object.entries(quickInputStats).filter(([_, value]) => value && value.trim()).map(([key, value]) => `${key}: ${value}`).join(', ')}`,
          timestamp: new Date().toISOString()
        };
        setSessionStats(prev => [newSessionStat, ...prev]);
        
      } else {
        setResponse(data.error || 'Failed to process quick input');
        setShowResponse(true);
      }
    } catch (error) {
      console.error('Error processing quick input:', error);
      if (error.message.includes('Unexpected token')) {
        setResponse('Authentication error. Please log in to continue.');
        setShowResponse(true);
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        setResponse(`Error processing quick input: ${error.message}`);
        setShowResponse(true);
      }
    } finally {
      setIsSubmittingQuickInput(false);
    }
  };

  return (
    <ThreeParticleEffect
      isRecording={isRecording || isProcessing}
      isHovered={isHovered}
    >
      <div className="min-h-screen p-6">
        <DynamicBackground />
        <div className="clean-layout">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-2">Input</h1>
            <p className="text-slate-400">Input church statistics and attendance data</p>
          </div>

          {/* Main Card */}
          <div className="main-card">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-white mb-2">Voice Input</h2>
                <p className="text-slate-400">Speak your stats naturally</p>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowQuickInput(true)}
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                  className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-xl flex items-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  <PlusIcon className="w-5 h-5" />
                  <span>Quick Input</span>
                </button>
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-slate-400 font-medium">Campus:</span>
                  <select
                    value={selectedCampus}
                    onChange={(e) => setSelectedCampus(e.target.value)}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    className="bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-2 text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {campuses.map(campus => (
                      <option key={campus.id} value={campus.id}>
                        {campus.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            
            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left Column - Voice Input */}
              <div className="text-center">
                <div className="relative">
                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={isProcessing}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    className={`
                      voice-button-large
                      ${isRecording 
                        ? 'bg-red-500 hover:bg-red-600 recording-active' 
                        : 'bg-blue-500 hover:bg-blue-600 shadow-blue-500/50'
                      }
                      ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}
                    `}
                  >
                    <MicrophoneIcon className="w-8 h-8 text-white" />
                    {isRecording && (
                      <div className="absolute inset-0 rounded-full border-4 border-red-400 animate-ping"></div>
                    )}
                  </button>
                </div>
              </div>

              {/* Right Column - Manual Input */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Type your stats:
                  </label>
                  <textarea
                    value={transcript}
                    onChange={(e) => setTranscript(e.target.value)}
                    placeholder="Type or speak your stats here... (e.g., '150 people at Salisbury campus, 25 first time visitors, 5 salvations')"
                    onFocus={() => setIsHovered(true)}
                    onBlur={() => setIsHovered(false)}
                    className="w-full bg-slate-700/50 border border-slate-600 rounded-xl p-4 text-white placeholder-slate-400 min-h-[120px] resize-none input-focus"
                  />
                </div>
                
                <div className="flex justify-end">
                  <button
                    type="submit"
                    onClick={handleSubmit}
                    disabled={!transcript.trim() || isProcessing}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    className="bg-blue-500 hover:bg-blue-600 disabled:bg-slate-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl flex items-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    <PaperAirplaneIcon className="w-5 h-5" />
                    <span>Submit</span>
                  </button>
                </div>
              </div>
            </div>
            
            {/* Processing Indicator */}
            {isProcessing && (
              <div className="mt-6 text-center">
                <div className="inline-flex items-center space-x-3 text-blue-400">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-400"></div>
                  <span className="font-medium">Processing...</span>
                </div>
              </div>
            )}
          </div>

          {/* Session Stats */}
          <div className="main-card">
            <h3 className="text-xl font-semibold text-white mb-6">Session Stats</h3>
            {sessionStats.length > 0 ? (
              <div className="space-y-4">
                {sessionStats.map((stat, index) => (
                  <div key={index} className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/50">
                    <div className="text-sm text-slate-400 font-medium mb-1">{stat.campus}</div>
                    <div className="text-white">{stat.text}</div>
                    <div className="text-xs text-slate-500 mt-2">
                      {new Date(stat.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-slate-400 text-lg mb-2">No stats logged yet</div>
                <p className="text-slate-500 text-sm">Start by using voice input or manual entry above</p>
              </div>
            )}
          </div>
        </div>

        {/* Response Modal */}
        {showResponse && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-white">Response</h3>
                <button
                  onClick={clearResponse}
                  className="text-slate-400 hover:text-white"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>

              {/* Audio Playback */}
              {audioUrl && (
                <div className="mb-4">
                  <button
                    onClick={playAudio}
                    disabled={isPlayingAudio}
                    className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
                  >
                    {isPlayingAudio ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <PlayIcon className="w-4 h-4" />
                    )}
                    <span>{isPlayingAudio ? 'Playing...' : 'Play Audio Response'}</span>
                  </button>
                </div>
              )}

              {/* Response Text */}
              <p className="text-white mb-4">{response}</p>
              
              {/* Input Stats */}
              {Object.keys(loggedStats).length > 0 && (
                <div className="mb-4">
                  <h4 className="text-md font-semibold text-white mb-2">Input Stats:</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(loggedStats).map(([key, value]) => (
                      <div key={key} className="bg-slate-700/30 rounded-lg p-2">
                        <div className="text-sm text-slate-400 capitalize">{key.replace(/_/g, ' ')}</div>
                        <div className="text-white font-medium">{formatStatValue(value)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Missing Stats */}
              {missingStats.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-md font-semibold text-yellow-400 mb-2">Missing Stats:</h4>
                  <ul className="list-disc list-inside text-yellow-300 space-y-1">
                    {missingStats.map((stat, index) => (
                      <li key={index}>{stat}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Suggestions */}
              {suggestions.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-md font-semibold text-blue-400 mb-2">Suggestions:</h4>
                  <ul className="list-disc list-inside text-blue-300 space-y-1">
                    {suggestions.map((suggestion, index) => (
                      <li key={index}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Quick Input Modal */}
        {showQuickInput && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-6">
                <h3 className="text-xl font-semibold text-white">Quick Input</h3>
                <button
                  onClick={() => setShowQuickInput(false)}
                  className="text-slate-400 hover:text-white"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>
              
              {/* Campus Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Campus:
                </label>
                <select
                  value={selectedCampus}
                  onChange={(e) => setSelectedCampus(e.target.value)}
                  className="bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white w-full"
                >
                  {campuses.map(campus => (
                    <option key={campus.id} value={campus.id}>
                      {campus.name}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Date Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Week of:
                </label>
                <div className="flex items-center space-x-2">
                  <CalendarIcon className="w-5 h-5 text-slate-400" />
                  <input
                    type="date"
                    value={quickInputDate}
                    onChange={(e) => setQuickInputDate(e.target.value)}
                    className="bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  />
                </div>
              </div>
              
              {/* Stats Form */}
              <div className="space-y-4">
                {Object.entries(quickInputStats).map(([statName, value]) => (
                  <div key={statName} className="flex items-center justify-between">
                    <label className="text-white font-medium min-w-[150px]">
                      {statName}:
                    </label>
                    <input
                      type="text"
                      inputMode="numeric"
                      value={value}
                      onChange={(e) => setQuickInputStats(prev => ({
                        ...prev,
                        [statName]: e.target.value
                      }))}
                      placeholder="0"
                      className="bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white text-right w-32 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                    />
                  </div>
                ))}
              </div>
              
              {/* Validation Hint */}
              <div className="mt-6 p-3 bg-slate-700/30 rounded-lg">
                <p className="text-sm text-slate-400">
                  Your number should not have commas or currency symbols
                </p>
              </div>
              
              {/* Submit Button */}
              <div className="flex justify-end mt-6">
                <button
                  onClick={handleQuickInputSubmit}
                  disabled={isSubmittingQuickInput}
                  className="bg-green-500 hover:bg-green-600 disabled:bg-slate-600 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg flex items-center space-x-2 transition-colors"
                >
                  {isSubmittingQuickInput ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <PlusIcon className="w-4 h-4" />
                  )}
                  <span>{isSubmittingQuickInput ? 'Submitting...' : 'Submit'}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </ThreeParticleEffect>
  );
};

export default LogStats; 