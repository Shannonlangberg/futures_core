import React, { useState, useEffect, useRef } from 'react';
import { MicrophoneIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline';
import DynamicBackground from '../components/DynamicBackground';
import ThreeParticleEffect from '../components/ThreeParticleEffect';

const Pulse = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const [audioUrl, setAudioUrl] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [campuses, setCampuses] = useState([]);
  const [selectedCampus, setSelectedCampus] = useState('all_campuses');
  const recognitionRef = useRef(null);

  // Fetch campuses
  useEffect(() => {
    fetch('/api/campuses', {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        if (data.campuses) {
          setCampuses(data.campuses);
          if (data.campuses.length > 0) {
            setSelectedCampus(data.campuses[0].id);
          }
        }
      })
      .catch(err => console.error('Error fetching campuses:', err));
  }, []);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setTranscript(finalTranscript);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };
    }
  }, []);

  const startRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  const processQuery = async (query) => {
    if (!query.trim()) return;

    setIsProcessing(true);
    try {
      const response = await fetch('/api/process_voice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          query: query,
          campus: selectedCampus
        }),
      });

      const data = await response.json();
      setResponse(data);

      if (data.audio_url) {
        setAudioUrl(data.audio_url);
      }

      setShowPopup(true);
    } catch (error) {
      console.error('Error processing query:', error);
      setResponse({ error: 'Failed to process query' });
      setShowPopup(true);
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
        body: JSON.stringify({ text }),
      });

      const data = await response.json();
      if (data.audio_url) {
        setAudioUrl(data.audio_url);
      }
    } catch (error) {
      console.error('Error generating audio:', error);
    }
  };

  const playAudio = () => {
    if (audioUrl) {
      setIsPlaying(true);
      const audio = new Audio(audioUrl);
      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => setIsPlaying(false);
      audio.play().catch(err => {
        console.error('Error playing audio:', err);
        setIsPlaying(false);
      });
    }
  };

  const closePopup = () => {
    setShowPopup(false);
    setResponse(null);
    setAudioUrl('');
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
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-slate-400 font-medium">Campus:</span>
                  <select
                    value={selectedCampus}
                    onChange={(e) => setSelectedCampus(e.target.value)}
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
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={isProcessing}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    className={`
                      voice-button-large
                      ${isRecording
                        ? 'bg-red-500 hover:bg-red-600 voice-button-active'
                        : 'bg-blue-500 hover:bg-blue-600 voice-button-idle'
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

              {/* Right Column - Text Input */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Or type your question here:
                  </label>
                  <textarea
                    value={transcript}
                    onChange={(e) => setTranscript(e.target.value)}
                    placeholder="Or type your question here..."
                    onFocus={() => setIsHovered(true)}
                    onBlur={() => setIsHovered(false)}
                    className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-all duration-300 hover:border-blue-400 focus:shadow-lg focus:shadow-blue-500/25"
                    rows="4"
                  ></textarea>
                </div>
                <div className="flex justify-end">
                  <button
                    onClick={() => processQuery(transcript)}
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
        </div>
      </div>

      {/* Query Results Popup */}
      {showPopup && response && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800/95 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold text-white">Query Results</h3>
              <button
                onClick={closePopup}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Audio Player */}
            {audioUrl && (
              <div className="mb-6 p-4 bg-slate-700/50 rounded-xl">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={playAudio}
                    disabled={isPlaying}
                    className="bg-blue-500 hover:bg-blue-600 disabled:bg-slate-600 text-white p-3 rounded-full transition-colors"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                    </svg>
                  </button>
                  <span className="text-white">Listen to response</span>
                </div>
              </div>
            )}

            {/* Response Content */}
            <div className="space-y-6">
              {/* Summary */}
              {response.summary && (
                <div className="bg-slate-700/50 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-white mb-3">Summary</h4>
                  <p className="text-slate-300 leading-relaxed">{response.summary}</p>
                </div>
              )}

              {/* Cross-Location Comparison Table */}
              {response.comparison && response.cross_location && response.data && (
                <div className="bg-slate-700/50 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-white mb-4">Cross-Location Comparison</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-600">
                          <th className="text-left py-3 px-4 text-slate-300 font-medium">Stat</th>
                          {response.campuses && response.campuses.map(campus => (
                            <th key={campus} className="text-right py-3 px-4 text-slate-300 font-medium">
                              {campus}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {response.data && response.data.map((row, index) => (
                          <tr key={index} className="border-b border-slate-600/50">
                            <td className="py-3 px-4 text-white font-medium">{row.stat}</td>
                            {response.campuses && response.campuses.map(campus => (
                              <td key={campus} className="text-right py-3 px-4 text-slate-300">
                                {row[campus] || row[campus.replace(/_/g, '')] || row[campus.replace(/_/g, ' ')] || row[campus.toLowerCase()] || '0'}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Regular Data Table */}
              {response.data && !response.cross_location && (
                <div className="bg-slate-700/50 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-white mb-4">Data</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-600">
                          <th className="text-left py-3 px-4 text-slate-300 font-medium">Stat</th>
                          <th className="text-right py-3 px-4 text-slate-300 font-medium">Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {response.data.map((item, index) => (
                          <tr key={index} className="border-b border-slate-600/50">
                            <td className="py-3 px-4 text-white font-medium">{item.stat}</td>
                            <td className="text-right py-3 px-4 text-slate-300">{item.value}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Comparison Reports */}
              {response.comparison && !response.cross_location && (
                <div className="bg-slate-700/50 rounded-xl p-6">
                  <h4 className="text-lg font-semibold text-white mb-4">Comparison Reports</h4>
                  <div className="space-y-4">
                    {response.data && response.data.map((report, index) => (
                      <div key={index} className="border border-slate-600 rounded-lg p-4">
                        <h5 className="text-white font-medium mb-2">{report.period}</h5>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                          {Object.entries(report.stats).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-slate-400">{key}</span>
                              <span className="text-white font-medium">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </ThreeParticleEffect>
  );
};

export default Pulse; 