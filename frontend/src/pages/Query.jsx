import React, { useState, useEffect, useRef } from 'react';
import { MicrophoneIcon, XMarkIcon, PlayIcon, PauseIcon, QuestionMarkCircleIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline';
import ThreeParticleEffect from '../components/ThreeParticleEffect';
import DynamicBackground from '../components/DynamicBackground';

const Query = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [currentCampus, setCurrentCampus] = useState('all_campuses');
  const [campuses, setCampuses] = useState([]);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showExamples, setShowExamples] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const audioRef = useRef(null);
  const recognitionRef = useRef(null);

  const exampleQueries = [
    "What was the average attendance at South campus last month?",
    "How many new people did we have across all campuses this year?",
    "Show me a comparison of youth attendance between Salisbury and Paradise",
    "What's the trend in connect groups over the last 6 months?",
    "Give me a quarterly report for all campuses",
    "How many salvations did we have at Adelaide City campus?",
    "What was our total attendance last week?",
    "Show me the annual review for South campus"
  ];

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
          if (data.default && currentCampus === 'all_campuses') {
            setCurrentCampus(data.default);
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
        setIsListening(true);
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
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        if (transcript.trim()) {
          processQuery(transcript);
        }
      };
    }
  }, []);

  const startListening = async () => {
    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
    } catch (error) {
      console.error('Microphone permission denied:', error);
      alert('Please allow microphone access to use voice queries.');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const processQuery = async (queryText) => {
    if (!queryText.trim()) return;

    setIsProcessing(true);
    setResponse(null);
    setAudioUrl(null);

    try {
      const response = await fetch('/api/process_voice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          text: queryText,
          campus: currentCampus
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      console.log('API Response:', data); // Debug log
      console.log('Comparison data:', data.comparison); // Debug log
      console.log('Reports data:', data.reports); // Debug log
      console.log('Percent changes:', data.percent_changes); // Debug log
      
      // Check if this is a query response that should show popup
      const isQueryResponse = data.popup === true || data.report || data.analysis || 
                            data.question || data.comparison || data.reports || 
                            data.percent_changes || data.years;

      console.log('Is Query Response:', isQueryResponse); // Debug log

      if (isQueryResponse) {
        console.log('Setting popup to true'); // Debug log
        setResponse(data);
        setShowPopup(true);
        
        // Play audio response if available
        if (data.audio_url) {
          console.log('Playing audio:', data.audio_url); // Debug log
          setAudioUrl(data.audio_url);
          playAudio(data.audio_url);
        } else if (data.text) {
          // Generate audio with ElevenLabs if no audio URL provided
          generateAudio(data.text);
        }
      } else {
        console.log('Regular response - no popup'); // Debug log
        // Regular response
        setResponse(data);
        if (data.audio_url) {
          setAudioUrl(data.audio_url);
          playAudio(data.audio_url);
        }
      }
    } catch (error) {
      console.error('Error processing query:', error);
      setResponse({
        text: 'Sorry, there was an error processing your query. Please try again.',
        error: true
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const generateAudio = async (text) => {
    try {
      const response = await fetch('/api/generate_audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ text })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.audio_url) {
          setAudioUrl(data.audio_url);
          playAudio(data.audio_url);
        }
      }
    } catch (error) {
      console.error('Error generating audio:', error);
    }
  };

  const playAudio = (url) => {
    console.log('playAudio called with URL:', url); // Debug log
    if (audioRef.current) {
      // Ensure the audio URL is properly constructed for the backend
      const fullUrl = url.startsWith('http') ? url : `http://localhost:5002${url}`;
      console.log('Full audio URL:', fullUrl); // Debug log
      audioRef.current.src = fullUrl;
      audioRef.current.play().catch(error => {
        console.error('Error playing audio:', error);
      });
      setIsPlaying(true);
    } else {
      console.error('audioRef.current is null'); // Debug log
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const handleAudioPlay = () => {
    setIsPlaying(true);
  };

  const handleAudioPause = () => {
    setIsPlaying(false);
  };

  const closePopup = () => {
    setShowPopup(false);
    setResponse(null);
    setAudioUrl(null);
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const renderReportTable = (report) => {
    if (!report || !Array.isArray(report)) return null;

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full bg-slate-800/50 rounded-lg">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="px-4 py-3 text-left text-slate-300 font-medium">Metric</th>
              <th className="px-4 py-3 text-left text-slate-300 font-medium">Total</th>
              <th className="px-4 py-3 text-left text-slate-300 font-medium">Average</th>
              <th className="px-4 py-3 text-left text-slate-300 font-medium">Count</th>
            </tr>
          </thead>
          <tbody>
            {report.map((item, index) => (
              <tr key={index} className="border-b border-slate-700/50">
                <td className="px-4 py-3 text-blue-400 font-medium">{item.label}</td>
                <td className="px-4 py-3 text-white">{item.total?.toLocaleString() || '—'}</td>
                <td className="px-4 py-3 text-white">{item.average?.toFixed(1) || '—'}</td>
                <td className="px-4 py-3 text-white">{item.count || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <ThreeParticleEffect 
      isRecording={isListening || isProcessing}
      isHovered={isHovered}
    >
      <div className="min-h-screen p-6">
        <DynamicBackground />
        <div className="clean-layout">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-2">Pulse</h1>
            <p className="text-slate-400">Ask questions about your church statistics using voice or text</p>
          </div>
          
          {/* Main Card */}
          <div className="main-card">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-white mb-2">Query Settings</h2>
                <p className="text-slate-400">Ask questions about your data</p>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowExamples(!showExamples)}
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                  className="flex items-center space-x-2 bg-slate-700/50 hover:bg-slate-600/50 rounded-lg px-4 py-2 text-white transition-colors"
                >
                  <QuestionMarkCircleIcon className="w-5 h-5" />
                  <span>Examples</span>
                </button>
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-slate-400 font-medium">Campus:</span>
                  <select
                    value={currentCampus}
                    onChange={(e) => setCurrentCampus(e.target.value)}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    className="bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-2 text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {campuses.length > 1 && (
                      <option value="all_campuses">All</option>
                    )}
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
                    onClick={isListening ? stopListening : startListening}
                    disabled={isProcessing}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    className={`
                      voice-button-large
                      ${isListening 
                        ? 'bg-red-500 hover:bg-red-600 voice-button-active' 
                        : 'bg-blue-500 hover:bg-blue-600 voice-button-idle'
                      }
                      ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}
                    `}
                  >
                    <MicrophoneIcon className="w-8 h-8 text-white" />
                    {isListening && (
                      <div className="absolute inset-0 rounded-full border-4 border-red-400 animate-ping"></div>
                    )}
                  </button>
                </div>
              </div>

              {/* Right Column - Text Input */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Or type your question:
                  </label>
                  <input
                    type="text"
                    placeholder="Or type your question here..."
                    className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-all duration-300 hover:border-blue-400 focus:shadow-lg focus:shadow-blue-500/25"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        processQuery(e.target.value);
                        e.target.value = '';
                      }
                    }}
                    onFocus={() => setIsHovered(true)}
                    onBlur={() => setIsHovered(false)}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Additional context:
                  </label>
                  <input
                    type="text"
                    placeholder="Or type your question here..."
                    className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-all duration-300 hover:border-blue-400 focus:shadow-lg focus:shadow-blue-500/25"
                    onFocus={() => setIsHovered(true)}
                    onBlur={() => setIsHovered(false)}
                  />
                </div>

                <div className="flex justify-end">
                  <button
                    onClick={() => processQuery(document.querySelector('input[placeholder="Or type your question here..."]').value)}
                    disabled={isProcessing}
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

            {/* Transcript Display */}
            {transcript && (
              <div className="bg-slate-700/50 rounded-lg p-4 mt-6">
                <div className="text-slate-300 text-sm mb-2">Heard:</div>
                <div className="text-white font-medium">{transcript}</div>
              </div>
            )}
          </div>
          
          {/* Example Queries */}
          {showExamples && (
            <div className="main-card">
              <h3 className="text-xl font-semibold text-white mb-6">Example Queries</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {exampleQueries.map((query, index) => (
                  <button
                    key={index}
                    onClick={() => processQuery(query)}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    className="text-left p-4 bg-slate-700/30 hover:bg-slate-600/30 rounded-lg border border-slate-600/50 transition-all duration-300 hover:border-blue-400 hover:shadow-lg hover:shadow-blue-500/25"
                  >
                    <div className="text-white font-medium">{query}</div>
                    <div className="text-slate-400 text-sm mt-1">Click to try this query</div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Response Modal */}
        {showPopup && response && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-white">Response</h3>
                <button
                  onClick={closePopup}
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
                    disabled={isPlaying}
                    className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
                  >
                    {isPlaying ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <PlayIcon className="w-4 h-4" />
                    )}
                    <span>{isPlaying ? 'Playing...' : 'Play Audio Response'}</span>
                  </button>
                </div>
              )}
              
              {/* Response Text */}
              <p className="text-white mb-4">{response.text}</p>
              
              {/* Cross Location Reports */}
              {response.cross_location && response.data && (
                <div className="space-y-6">
                  <h4 className="text-lg font-semibold text-white">Cross-Location Comparison</h4>
                  <div className="bg-slate-700/50 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="bg-slate-600/50">
                            <th className="px-4 py-3 text-left text-slate-300 font-medium">Stat</th>
                            {response.campuses && response.campuses.map((campus, index) => (
                              <th key={index} className="px-4 py-3 text-left text-slate-300 font-medium">
                                {campus.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {response.data.map((row, index) => (
                            <tr key={index} className="border-b border-slate-600/50">
                              <td className="px-4 py-3 text-blue-400 font-medium">{row.stat}</td>
                              {response.campuses && response.campuses.map((campus, campusIndex) => (
                                <td key={campusIndex} className="px-4 py-3 text-white">
                                  {row[campus]?.toLocaleString() || 
                                   row[campus.replace(/_/g, '')]?.toLocaleString() || 
                                   row[campus.replace(/_/g, ' ')]?.toLocaleString() || 
                                   row[campus.toLowerCase()]?.toLocaleString() || 
                                   '—'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Comparison Reports */}
              {response.comparison && response.reports && !response.cross_location && (
                <div className="space-y-6">
                  <h4 className="text-lg font-semibold text-white">Comparison Results</h4>
                  {response.reports.map((reportData, index) => (
                    <div key={index} className="bg-slate-700/50 rounded-lg p-4">
                      <h5 className="text-blue-400 font-semibold mb-3">{reportData.text}</h5>
                      {renderReportTable(reportData.report)}
                    </div>
                  ))}
                  
                  {/* Percentage Changes */}
                  {response.percent_changes && (
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <h5 className="text-blue-400 font-semibold mb-3">Year-over-Year Changes</h5>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {Object.entries(response.percent_changes).map(([key, value]) => (
                          <div key={key} className="bg-slate-600/50 rounded-lg p-3">
                            <div className="text-slate-400 text-sm">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</div>
                            <div className={`font-semibold text-lg ${value > 0 ? 'text-green-400' : value < 0 ? 'text-red-400' : 'text-white'}`}>
                              {value > 0 ? '+' : ''}{value.toFixed(1)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Stats Display */}
              {response.stats && Object.keys(response.stats).length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(response.stats).map(([key, value]) => (
                    <div key={key} className="bg-slate-700/50 rounded-lg p-4">
                      <div className="text-slate-400 text-sm">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</div>
                      <div className="text-white font-semibold text-lg">{value}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* Insights */}
              {response.insights && response.insights.length > 0 && (
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <h4 className="text-blue-400 font-semibold mb-2">Insights</h4>
                  <div className="space-y-2">
                    {response.insights.map((insight, index) => (
                      <div key={index} className="text-slate-300">• {insight}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Hidden Audio Element */}
        <audio
          ref={audioRef}
          onEnded={handleAudioEnded}
          onPlay={handleAudioPlay}
          onPause={handleAudioPause}
          style={{ display: 'none' }}
        />
      </div>
    </ThreeParticleEffect>
  );
};

export default Query; 