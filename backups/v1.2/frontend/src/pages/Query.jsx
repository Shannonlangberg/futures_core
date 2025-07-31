import React, { useState, useEffect, useRef } from 'react';
import { MicrophoneIcon, XMarkIcon, PlayIcon, PauseIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

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
    fetch('/api/campuses')
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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Pulse</h1>
          <p className="text-slate-400 mt-1">Ask questions about your church statistics using voice or text</p>
        </div>
        <button
          onClick={() => setShowExamples(!showExamples)}
          className="flex items-center space-x-2 bg-slate-700/50 hover:bg-slate-600/50 rounded-lg px-4 py-2 text-white transition-colors"
        >
          <QuestionMarkCircleIcon className="w-5 h-5" />
          <span>Examples</span>
        </button>
      </div>

      {/* Example Queries */}
      {showExamples && (
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Example Queries</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {exampleQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => processQuery(query)}
                className="text-left p-4 bg-slate-700/30 hover:bg-slate-600/30 rounded-lg border border-slate-600/50 transition-colors"
              >
                <div className="text-white font-medium">{query}</div>
                <div className="text-slate-400 text-sm mt-1">Click to try this query</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Campus Selector */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">Query Settings</h2>
                                <select
                        value={currentCampus}
                        onChange={(e) => setCurrentCampus(e.target.value)}
                        className="bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-2 text-white"
                      >
                        {/* Only show "All Campuses" for users with multiple campus access */}
                        {campuses.length > 1 && (
                          <option value="all_campuses">All Campuses</option>
                        )}
                        {campuses.map(campus => (
                          <option key={campus.id} value={campus.id}>
                            {campus.name}
                          </option>
                        ))}
                      </select>
        </div>

        {/* Voice Interface */}
        <div className="text-center space-y-6">
          {/* Voice Button */}
          <div className="relative">
            <button
              onClick={isListening ? stopListening : startListening}
              disabled={isProcessing}
              className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 ${
                isListening 
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                  : 'bg-blue-500 hover:bg-blue-600'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <MicrophoneIcon className="w-8 h-8 text-white" />
            </button>
            <div className="mt-4 text-slate-300">
              {isListening ? 'Listening...' : isProcessing ? 'Processing...' : 'Click to speak'}
            </div>
          </div>

          {/* Transcript Display */}
          {transcript && (
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="text-slate-300 text-sm mb-2">Heard:</div>
              <div className="text-white font-medium">{transcript}</div>
            </div>
          )}

          {/* Text Input Fallback */}
          <div className="max-w-md mx-auto">
            <input
              type="text"
              placeholder="Or type your question here..."
              className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  processQuery(e.target.value);
                  e.target.value = '';
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Response Display */}
      {response && !showPopup && (
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Response</h3>
            {audioUrl && (
              <button
                onClick={() => isPlaying ? audioRef.current?.pause() : audioRef.current?.play()}
                className="flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 rounded-lg px-3 py-2 text-white"
              >
                {isPlaying ? <PauseIcon className="w-4 h-4" /> : <PlayIcon className="w-4 h-4" />}
                <span>{isPlaying ? 'Pause' : 'Play'}</span>
              </button>
            )}
          </div>
          <div className="text-white">{response.text}</div>
        </div>
      )}

      {/* Query Popup Modal */}
      {showPopup && response && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-white">Query Results</h3>
                <div className="flex items-center space-x-4">
                  {audioUrl && (
                    <button
                      onClick={() => isPlaying ? audioRef.current?.pause() : audioRef.current?.play()}
                      className="flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 rounded-lg px-3 py-2 text-white"
                    >
                      {isPlaying ? <PauseIcon className="w-4 h-4" /> : <PlayIcon className="w-4 h-4" />}
                      <span>{isPlaying ? 'Pause' : 'Play'}</span>
                    </button>
                  )}
                  <button
                    onClick={closePopup}
                    className="text-slate-400 hover:text-white"
                  >
                    <XMarkIcon className="w-6 h-6" />
                  </button>
                </div>
              </div>

              <div className="space-y-6">
                {/* Response Text */}
                {response.text && (
                  <div className="bg-slate-800/50 rounded-lg p-4">
                    <div className="text-white">{response.text}</div>
                  </div>
                )}

                {/* Regular Report Table */}
                {response.report && !response.comparison && (
                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Report Results</h4>
                    <div className="bg-slate-800/50 rounded-lg p-4">
                      {response.report.summary && (
                        <h5 className="text-blue-400 font-semibold mb-3">{response.report.summary}</h5>
                      )}
                      {response.report.stats && (
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                          {Object.entries(response.report.stats).map(([key, value]) => (
                            <div key={key} className="bg-slate-700/50 rounded-lg p-3">
                              <div className="text-slate-400 text-sm">{value.label}</div>
                              <div className="text-white font-semibold text-lg">
                                {value.total?.toLocaleString() || '—'}
                              </div>
                              {value.average && (
                                <div className="text-slate-300 text-sm">
                                  Avg: {value.average.toFixed(1)}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                      {response.report.report && renderReportTable(response.report.report)}
                    </div>
                  </div>
                )}

                {/* Cross-Location Comparison */}
                {response.comparison && response.cross_location && response.data && (
                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-white">Cross-Location Comparison</h4>
                    <div className="bg-slate-800/50 rounded-lg p-4">
                      <h5 className="text-blue-400 font-semibold mb-3">{response.summary}</h5>
                      

                      
                      <div className="overflow-x-auto">
                        <table className="min-w-full bg-slate-700/50 rounded-lg">
                          <thead>
                            <tr className="border-b border-slate-600">
                              <th className="px-4 py-3 text-left text-slate-300 font-medium">Metric</th>
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
                                    {row[campus]?.toLocaleString() || '—'}
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
                      <div key={index} className="bg-slate-800/50 rounded-lg p-4">
                        <h5 className="text-blue-400 font-semibold mb-3">{reportData.text}</h5>
                        {renderReportTable(reportData.report)}
                      </div>
                    ))}
                    
                    {/* Percentage Changes */}
                    {response.percent_changes && (
                      <div className="bg-slate-800/50 rounded-lg p-4">
                        <h5 className="text-blue-400 font-semibold mb-3">Year-over-Year Changes</h5>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                          {Object.entries(response.percent_changes).map(([key, value]) => (
                            <div key={key} className="bg-slate-700/50 rounded-lg p-3">
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
                      <div key={key} className="bg-slate-800/50 rounded-lg p-4">
                        <div className="text-slate-400 text-sm">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</div>
                        <div className="text-white font-semibold text-lg">{value}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Insights */}
                {response.insights && response.insights.length > 0 && (
                  <div className="bg-slate-800/50 rounded-lg p-4">
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
  );
};

export default Query; 