import React, { useState, useEffect } from 'react';
import { HeartIcon, ChartBarIcon, ArrowTrendingUpIcon, UsersIcon } from '@heroicons/react/24/outline';

const Pulse = () => {
  const [pulseData, setPulseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCampus, setSelectedCampus] = useState('all_campuses');
  const [campuses, setCampuses] = useState([]);

  useEffect(() => {
    // Load campuses
    fetch('/api/campuses')
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
      const response = await fetch(`/api/stats?campus=${selectedCampus}`);
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
      return { status: 'strong', color: 'text-green-400', bgColor: 'bg-green-500/20' };
    } else if (attendance > 0 && (newPeople > 0 || newChristians > 0)) {
      return { status: 'steady', color: 'text-yellow-400', bgColor: 'bg-yellow-500/20' };
    } else if (attendance > 0) {
      return { status: 'stable', color: 'text-blue-400', bgColor: 'bg-blue-500/20' };
    } else {
      return { status: 'no data', color: 'text-slate-400', bgColor: 'bg-slate-500/20' };
    }
  };

  const pulseStatus = pulseData ? getPulseStatus(
    pulseData.total_attendance || 0,
    pulseData.new_people || 0,
    pulseData.new_christians || 0
  ) : { status: 'loading', color: 'text-slate-400', bgColor: 'bg-slate-500/20' };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Heartbeat</h1>
        <p className="text-slate-400 mt-1">Real-time church pulse and heartbeat</p>
      </div>

      {/* Campus Selector */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">Campus Pulse</h2>
          <select
            value={selectedCampus}
            onChange={(e) => setSelectedCampus(e.target.value)}
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

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-flex items-center space-x-2 text-blue-400">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>
              <span>Loading pulse data...</span>
            </div>
          </div>
        ) : pulseData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Pulse Status */}
            <div className={`${pulseStatus.bgColor} border border-slate-600 rounded-xl p-6`}>
              <div className="flex items-center justify-between mb-4">
                <HeartIcon className={`w-8 h-8 ${pulseStatus.color}`} />
                <div className={`text-sm font-medium ${pulseStatus.color} capitalize`}>
                  {pulseStatus.status}
                </div>
              </div>
              <div className="text-2xl font-bold text-white">
                {pulseData.total_attendance || 0}
              </div>
              <div className="text-slate-400 text-sm">Total Attendance</div>
            </div>

            {/* New People */}
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <UsersIcon className="w-8 h-8 text-blue-400" />
                <ArrowTrendingUpIcon className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-2xl font-bold text-white">
                {pulseData.new_people || 0}
              </div>
              <div className="text-slate-400 text-sm">New People</div>
            </div>

            {/* New Christians */}
            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <HeartIcon className="w-8 h-8 text-purple-400" />
                <ArrowTrendingUpIcon className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-2xl font-bold text-white">
                {pulseData.new_christians || 0}
              </div>
              <div className="text-slate-400 text-sm">New Christians</div>
            </div>

            {/* Youth */}
            <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <UsersIcon className="w-8 h-8 text-orange-400" />
                <ChartBarIcon className="w-5 h-5 text-orange-400" />
              </div>
              <div className="text-2xl font-bold text-white">
                {pulseData.youth_attendance || 0}
              </div>
              <div className="text-slate-400 text-sm">Youth Attendance</div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-slate-700/50 rounded-full flex items-center justify-center mx-auto mb-4">
              <HeartIcon className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">No Pulse Data</h3>
            <p className="text-slate-400">No recent data available for this campus</p>
          </div>
        )}
      </div>

      {/* Pulse Insights */}
      {pulseData && (
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Pulse Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <span className="text-slate-300">Growth Rate</span>
                <span className="text-white font-semibold">
                  {pulseData.new_people > 0 ? 'Positive' : 'Stable'}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <span className="text-slate-300">Spiritual Impact</span>
                <span className="text-white font-semibold">
                  {pulseData.new_christians > 0 ? 'Strong' : 'Needs Focus'}
                </span>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <span className="text-slate-300">Youth Engagement</span>
                <span className="text-white font-semibold">
                  {pulseData.youth_attendance > 0 ? 'Active' : 'Limited'}
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <span className="text-slate-300">Overall Health</span>
                <span className={`font-semibold capitalize ${pulseStatus.color}`}>
                  {pulseStatus.status}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Live Pulse Animation */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Live Pulse</h3>
        <div className="flex justify-center">
          <div className="relative">
            <div className={`w-24 h-24 rounded-full flex items-center justify-center ${pulseStatus.bgColor} border-2 ${pulseStatus.color.replace('text-', 'border-')}`}>
              <HeartIcon className={`w-12 h-12 ${pulseStatus.color} ${pulseStatus.status === 'strong' ? 'animate-pulse' : ''}`} />
            </div>
            {pulseStatus.status === 'strong' && (
              <div className="absolute inset-0 rounded-full border-2 border-green-400 animate-ping"></div>
            )}
          </div>
        </div>
        <div className="text-center mt-4">
          <p className="text-slate-400">Church pulse is {pulseStatus.status}</p>
        </div>
      </div>
    </div>
  );
};

export default Pulse; 