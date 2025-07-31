import React, { useState, useEffect } from 'react';
import { UserCircleIcon, MapIcon, FlagIcon, StarIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

const Passport = () => {
  const [journeyData, setJourneyData] = useState(null);
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
    fetchJourneyData();
  }, [selectedCampus]);

  const fetchJourneyData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/stats?campus=${selectedCampus}`);
      const data = await response.json();
      
      if (data.stats) {
        setJourneyData(data.stats);
      }
    } catch (error) {
      console.error('Error fetching journey data:', error);
    } finally {
      setLoading(false);
    }
  };

  const journeyStages = [
    {
      id: 'visitor',
      name: 'Visitor',
      icon: UserCircleIcon,
      color: 'blue',
      description: 'First-time visitors to the church',
      count: journeyData?.new_people || 0
    },
    {
      id: 'new_christian',
      name: 'New Christian',
      icon: StarIcon,
      color: 'purple',
      description: 'New believers and rededications',
      count: journeyData?.new_christians || 0
    },
    {
      id: 'connected',
      name: 'Connected',
      icon: MapIcon,
      color: 'green',
      description: 'People in connect groups',
      count: journeyData?.connect_groups || 0
    },
    {
      id: 'serving',
      name: 'Serving',
      icon: FlagIcon,
      color: 'orange',
      description: 'Dream team members',
      count: journeyData?.dream_team || 0
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
      purple: 'bg-purple-500/10 border-purple-500/20 text-purple-400',
      green: 'bg-green-500/10 border-green-500/20 text-green-400',
      orange: 'bg-orange-500/10 border-orange-500/20 text-orange-400'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Passport</h1>
        <p className="text-slate-400 mt-1">Track member journey and spiritual growth</p>
      </div>

      {/* Campus Selector */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">Journey Overview</h2>
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
              <span>Loading journey data...</span>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Journey Stages */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {journeyStages.map((stage, index) => (
                <div key={stage.id} className={`${getColorClasses(stage.color)} border rounded-xl p-6`}>
                  <div className="flex items-center justify-between mb-4">
                    <stage.icon className="w-8 h-8" />
                    {index < journeyStages.length - 1 && (
                      <ArrowRightIcon className="w-5 h-5 text-slate-400" />
                    )}
                  </div>
                  <div className="text-2xl font-bold text-white mb-2">
                    {stage.count}
                  </div>
                  <div className="text-white font-medium mb-1">{stage.name}</div>
                  <div className="text-slate-400 text-sm">{stage.description}</div>
                </div>
              ))}
            </div>

            {/* Journey Flow */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-6">Journey Flow</h3>
              <div className="flex items-center justify-center space-x-4">
                {journeyStages.map((stage, index) => (
                  <div key={stage.id} className="flex items-center">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center ${getColorClasses(stage.color)}`}>
                      <stage.icon className="w-8 h-8" />
                    </div>
                    {index < journeyStages.length - 1 && (
                      <div className="w-12 h-0.5 bg-slate-600 mx-2"></div>
                    )}
                  </div>
                ))}
              </div>
              <div className="flex justify-center mt-4 space-x-8">
                {journeyStages.map((stage) => (
                  <div key={stage.id} className="text-center">
                    <div className="text-white font-medium">{stage.name}</div>
                    <div className="text-slate-400 text-sm">{stage.count}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Journey Insights */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-white mb-4">Growth Metrics</h4>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-slate-700/30 rounded-lg">
                    <span className="text-slate-300">Conversion Rate</span>
                    <span className="text-white font-semibold">
                      {journeyData?.new_christians > 0 && journeyData?.new_people > 0 
                        ? `${Math.round((journeyData.new_christians / journeyData.new_people) * 100)}%`
                        : '0%'
                      }
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-slate-700/30 rounded-lg">
                    <span className="text-slate-300">Connection Rate</span>
                    <span className="text-white font-semibold">
                      {journeyData?.connect_groups > 0 && journeyData?.total_attendance > 0
                        ? `${Math.round((journeyData.connect_groups / journeyData.total_attendance) * 100)}%`
                        : '0%'
                      }
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-white mb-4">Journey Health</h4>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-slate-700/30 rounded-lg">
                    <span className="text-slate-300">Visitor Engagement</span>
                    <span className="text-white font-semibold">
                      {journeyData?.new_people > 0 ? 'Active' : 'Needs Focus'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-slate-700/30 rounded-lg">
                    <span className="text-slate-300">Spiritual Growth</span>
                    <span className="text-white font-semibold">
                      {journeyData?.new_christians > 0 ? 'Strong' : 'Opportunity'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Journey Goals */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Journey Goals</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-slate-700/30 rounded-lg">
            <div className="text-2xl font-bold text-blue-400 mb-2">25%</div>
            <div className="text-white font-medium">Visitor to Christian</div>
            <div className="text-slate-400 text-sm">Conversion Target</div>
          </div>
          <div className="text-center p-4 bg-slate-700/30 rounded-lg">
            <div className="text-2xl font-bold text-green-400 mb-2">60%</div>
            <div className="text-white font-medium">Connected Members</div>
            <div className="text-slate-400 text-sm">Group Participation</div>
          </div>
          <div className="text-center p-4 bg-slate-700/30 rounded-lg">
            <div className="text-2xl font-bold text-orange-400 mb-2">40%</div>
            <div className="text-white font-medium">Serving Members</div>
            <div className="text-slate-400 text-sm">Dream Team Target</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Passport; 