import React, { useState, useEffect } from 'react';
import { HeartIcon, ChartBarIcon, ArrowTrendingUpIcon, UsersIcon } from '@heroicons/react/24/outline';
import DynamicBackground from '../components/DynamicBackground';
import { MicrophoneIcon, PaperAirplaneIcon } from '@heroicons/react/24/solid';

const Heartbeat = () => {
  const [pulseData, setPulseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCampus, setSelectedCampus] = useState('all_campuses');
  const [campuses, setCampuses] = useState([]);

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
          if (data.default && selectedCampus === 'all_campuses') {
            setSelectedCampus(data.default);
          }
        }
      })
      .catch(err => console.error('Error loading campuses:', err));
  }, []);

  useEffect(() => {
    fetchPulseData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchPulseData, 30000);
    return () => clearInterval(interval);
  }, [selectedCampus]);

  const fetchPulseData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/stats?campus=${selectedCampus}`, {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (data.stats) {
        setPulseData(data.stats);
      }
    } catch (error) {
      console.error('Error fetching pulse data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPulseStatus = (attendance, newPeople, newChristians) => {
    if (attendance > 0 && newPeople > 0 && newChristians > 0) {
      return { status: 'strong', color: 'text-green-400', bgColor: 'bg-green-500/20', icon: 'text-green-400' };
    } else if (attendance > 0 && (newPeople > 0 || newChristians > 0)) {
      return { status: 'steady', color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', icon: 'text-yellow-400' };
    } else if (attendance > 0) {
      return { status: 'stable', color: 'text-blue-400', bgColor: 'bg-blue-500/20', icon: 'text-blue-400' };
    } else {
      return { status: 'no data', color: 'text-slate-400', bgColor: 'bg-slate-500/20', icon: 'text-slate-400' };
    }
  };

  const pulseStatus = pulseData ? getPulseStatus(
    pulseData.total_attendance || 0,
    pulseData.new_people || 0,
    pulseData.new_christians || 0
  ) : { status: 'loading', color: 'text-slate-400', bgColor: 'bg-slate-500/20', icon: 'text-slate-400' };

  return (
    <div className="relative min-h-screen">
      <DynamicBackground />
      <div className="relative z-10 space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-2">Heartbeat</h1>
          <p className="text-slate-400 text-lg">Real-time church pulse and heartbeat</p>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Campus Selector Card */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-xl mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold text-white mb-2">Campus Pulse</h2>
                <p className="text-slate-400">Monitor real-time statistics</p>
              </div>
              <select
                value={selectedCampus}
                onChange={(e) => setSelectedCampus(e.target.value)}
                className="bg-slate-700/50 border border-slate-600 rounded-xl px-6 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
          </div>
          
          {loading ? (
            <div className="text-center py-16">
              <div className="inline-flex items-center space-x-3 text-blue-400">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
                <span className="text-xl font-medium">Loading pulse data...</span>
              </div>
            </div>
          ) : pulseData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {/* Main Pulse Card */}
              <div className="md:col-span-2 lg:col-span-1">
                <div className={`${pulseStatus.bgColor} backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-xl`}>
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h3 className="text-2xl font-semibold text-white mb-2">Pulse Status</h3>
                      <p className={`text-lg font-medium ${pulseStatus.color}`}>
                        {pulseStatus.status.charAt(0).toUpperCase() + pulseStatus.status.slice(1)}
                      </p>
                    </div>
                    <HeartIcon className={`w-12 h-12 ${pulseStatus.icon} animate-pulse`} />
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Total Attendance</span>
                      <span className="text-white font-semibold text-lg">
                        {pulseData.total_attendance?.toLocaleString() || '0'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">New People</span>
                      <span className="text-white font-semibold text-lg">
                        {pulseData.new_people?.toLocaleString() || '0'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">New Christians</span>
                      <span className="text-white font-semibold text-lg">
                        {pulseData.new_christians?.toLocaleString() || '0'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Detailed Stats Cards */}
              <div className="space-y-6">
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-xl">
                  <div className="flex items-center space-x-3 mb-4">
                    <UsersIcon className="w-6 h-6 text-blue-400" />
                    <h4 className="text-lg font-semibold text-white">Attendance</h4>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Total</span>
                      <span className="text-white font-medium">{pulseData.total_attendance?.toLocaleString() || '0'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">First Time</span>
                      <span className="text-white font-medium">{pulseData.first_time_visitors?.toLocaleString() || '0'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Information</span>
                      <span className="text-white font-medium">{pulseData.information_gathered?.toLocaleString() || '0'}</span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-xl">
                  <div className="flex items-center space-x-3 mb-4">
                    <ArrowTrendingUpIcon className="w-6 h-6 text-green-400" />
                    <h4 className="text-lg font-semibold text-white">Growth</h4>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-slate-400">New People</span>
                      <span className="text-white font-medium">{pulseData.new_people?.toLocaleString() || '0'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">New Christians</span>
                      <span className="text-white font-medium">{pulseData.new_christians?.toLocaleString() || '0'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Rededications</span>
                      <span className="text-white font-medium">{pulseData.rededications?.toLocaleString() || '0'}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Additional Stats */}
              <div className="space-y-6">
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-xl">
                  <div className="flex items-center space-x-3 mb-4">
                    <ChartBarIcon className="w-6 h-6 text-purple-400" />
                    <h4 className="text-lg font-semibold text-white">Youth & Kids</h4>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Youth Attendance</span>
                      <span className="text-white font-medium">{pulseData.youth_attendance?.toLocaleString() || '0'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Youth Salvations</span>
                      <span className="text-white font-medium">{pulseData.youth_salvations?.toLocaleString() || '0'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Kids Attendance</span>
                      <span className="text-white font-medium">{pulseData.kids_attendance?.toLocaleString() || '0'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Kids Salvations</span>
                      <span className="text-white font-medium">{pulseData.kids_salvations?.toLocaleString() || '0'}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-xl">
                  <div className="flex items-center space-x-3 mb-4">
                    <HeartIcon className="w-6 h-6 text-red-400" />
                    <h4 className="text-lg font-semibold text-white">Engagement</h4>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Connect Groups</span>
                      <span className="text-white font-medium">{pulseData.connect_groups?.toLocaleString() || '0'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Dream Team</span>
                      <span className="text-white font-medium">{pulseData.dream_team?.toLocaleString() || '0'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Baptisms</span>
                      <span className="text-white font-medium">{pulseData.baptisms?.toLocaleString() || '0'}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-16">
              <div className="text-slate-400 text-xl mb-4">No pulse data available</div>
              <p className="text-slate-500">Try selecting a different campus or check back later</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Heartbeat; 