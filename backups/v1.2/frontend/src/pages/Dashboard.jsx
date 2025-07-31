import React, { useState, useEffect } from 'react';
import { ChevronDownIcon, PlusIcon, CalendarIcon } from '@heroicons/react/24/outline';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCampus, setSelectedCampus] = useState('all_campuses');
  const [dateFilter, setDateFilter] = useState('last_7_days');
  const [campuses, setCampuses] = useState([]);
  const [showBreakdownModal, setShowBreakdownModal] = useState(false);
  const [selectedStat, setSelectedStat] = useState(null);
  
  // Custom date range state
  const [showCustomDateModal, setShowCustomDateModal] = useState(false);
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');

  useEffect(() => {
    fetchCampuses();
    fetchDashboardData();
  }, [selectedCampus, dateFilter, customStartDate, customEndDate]);

  const fetchCampuses = async () => {
    try {
      const response = await fetch('/api/campuses');
      const data = await response.json();
      if (data.campuses) {
        setCampuses(data.campuses);
        // Set the default campus from the API response
        if (data.default && selectedCampus === 'all_campuses') {
          setSelectedCampus(data.default);
        }
      }
    } catch (error) {
      console.error('Error fetching campuses:', error);
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      let url = `/api/dashboard/data?campus=${selectedCampus}&date_filter=${dateFilter}`;
      
      // Add custom date parameters if using custom date range
      if (dateFilter === 'custom' && customStartDate && customEndDate) {
        url += `&custom_start_date=${customStartDate}&custom_end_date=${customEndDate}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setDashboardData({ stats: {}, chart_data: { attendance_labels: [], attendance_values: [] } });
    } finally {
      setLoading(false);
    }
  };

  const handleStatCardClick = (statType) => {
    setSelectedStat(statType);
    setShowBreakdownModal(true);
  };

  const getBreakdownData = (statType) => {
    if (!dashboardData?.stats) return {};
    
    const breakdowns = {
      'total_attendance': {
        title: 'Total Attendance Breakdown',
        items: [
          { label: 'Total Attendance', value: dashboardData.stats.total_attendance }
        ]
      },
      'new_people': {
        title: 'New People Breakdown',
        items: [
          { label: 'First Time Visitors', value: dashboardData.stats.first_time_visitors || 0 },
          { label: 'Visitors', value: dashboardData.stats.visitors || 0 },
          { label: 'Total New People', value: dashboardData.stats.total_new_people }
        ]
      },
      'new_christians': {
        title: 'New Christians Breakdown',
        items: [
          { label: 'First Time Christians', value: dashboardData.stats.first_time_christians || 0 },
          { label: 'Rededications', value: dashboardData.stats.rededications || 0 },
          { label: 'Total New Christians', value: dashboardData.stats.total_new_christians }
        ]
      },
      'youth_attendance': {
        title: 'Youth Breakdown',
        items: [
          { label: 'Youth Attendance', value: dashboardData.stats.youth_attendance || 0 },
          { label: 'Youth New People', value: dashboardData.stats.youth_new_people || 0 },
          { label: 'Youth Salvations', value: dashboardData.stats.youth_salvations || 0 }
        ]
      },
      'kids_total': {
        title: 'Kids Breakdown',
        items: [
          { label: 'Kids Attendance', value: dashboardData.stats.kids_attendance || 0 },
          { label: 'New Kids', value: dashboardData.stats.new_kids || 0 },
          { label: 'Kids Leaders', value: dashboardData.stats.kids_leaders || 0 },
          { label: 'New Kids Salvations', value: dashboardData.stats.new_kids_salvations || 0 }
        ]
      }
    };
    
    return breakdowns[statType] || { title: 'Breakdown', items: [] };
  };

  const handleDateFilterChange = (newDateFilter) => {
    setDateFilter(newDateFilter);
    // Clear custom dates if not using custom filter
    if (newDateFilter !== 'custom') {
      setCustomStartDate('');
      setCustomEndDate('');
    } else {
      // Automatically open the custom date modal when "Custom Date Range" is selected
      setShowCustomDateModal(true);
    }
  };

  const handleCustomDateSubmit = () => {
    if (customStartDate && customEndDate) {
      setDateFilter('custom');
      setShowCustomDateModal(false);
    }
  };

  const formatDateRange = () => {
    if (dateFilter === 'custom' && customStartDate && customEndDate) {
      const start = new Date(customStartDate).toLocaleDateString();
      const end = new Date(customEndDate).toLocaleDateString();
      return `${start} - ${end}`;
    }
    return null;
  };

  const statCards = [
    {
      title: 'Total Attendance',
      value: dashboardData?.stats?.total_attendance || 0,
      average: dashboardData?.stats?.avg_attendance || 0,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
      statType: 'total_attendance'
    },
    {
      title: 'New People',
      value: dashboardData?.stats?.total_new_people || 0,
      average: dashboardData?.stats?.avg_new_people || 0,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/20',
      statType: 'new_people'
    },
    {
      title: 'New Christians',
      value: dashboardData?.stats?.total_new_christians || 0,
      average: dashboardData?.stats?.avg_new_christians || 0,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
      statType: 'new_christians'
    },
    {
      title: 'Youth Attendance',
      value: dashboardData?.stats?.total_youth || 0,
      average: dashboardData?.stats?.avg_youth || 0,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/20',
      statType: 'youth_attendance'
    },
    {
      title: 'Kids Total',
      value: dashboardData?.stats?.total_kids || 0,
      average: dashboardData?.stats?.avg_kids || 0,
      color: 'from-pink-500 to-pink-600',
      bgColor: 'bg-pink-500/10',
      borderColor: 'border-pink-500/20',
      statType: 'kids_total'
    },
    {
      title: 'Connect Groups',
      value: dashboardData?.stats?.total_connect_groups || 0,
      average: dashboardData?.stats?.avg_connect_groups || 0,
      color: 'from-indigo-500 to-indigo-600',
      bgColor: 'bg-indigo-500/10',
      borderColor: 'border-indigo-500/20',
      statType: 'connect_groups'
    },
    {
      title: 'Dream Team',
      value: dashboardData?.stats?.total_dream_team || 0,
      average: dashboardData?.stats?.avg_dream_team || 0,
      color: 'from-teal-500 to-teal-600',
      bgColor: 'bg-teal-500/10',
      borderColor: 'border-teal-500/20',
      statType: 'dream_team'
    },
    {
      title: 'Tithe',
      value: dashboardData?.stats?.total_tithe || 0,
      average: dashboardData?.stats?.avg_tithe || 0,
      color: 'from-emerald-500 to-emerald-600',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
      statType: 'tithe'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 mt-1">Monitor your church statistics and performance</p>
        </div>
        
        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Campus Selector */}
          <div className="relative">
            <select
              value={selectedCampus}
              onChange={(e) => setSelectedCampus(e.target.value)}
              className="appearance-none bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 pr-10 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
            <ChevronDownIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
          </div>

          {/* Date Filter */}
          <div className="relative">
            <select
              value={dateFilter}
              onChange={(e) => handleDateFilterChange(e.target.value)}
              className="appearance-none bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 pr-10 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="last_7_days">Last 7 Days</option>
              <option value="last_30_days">Last 30 Days</option>
              <option value="last_90_days">Last 90 Days</option>
              <option value="this_year">This Year</option>
              <option value="custom">Custom Date Range</option>
            </select>
            <ChevronDownIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
            
            {/* Custom date range display */}
            {dateFilter === 'custom' && formatDateRange() && (
              <div className="absolute -bottom-8 left-0 text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded">
                {formatDateRange()}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <div
            key={index}
            className={`
              relative group cursor-pointer
              bg-slate-800/50 backdrop-blur-sm
              border border-slate-700/50 rounded-xl
              p-6 transition-all duration-300
              hover:border-slate-600/50 hover:shadow-xl hover:shadow-slate-900/20
              ${card.bgColor} ${card.borderColor}
            `}
            onClick={() => handleStatCardClick(card.statType)}
          >
            {/* Glow effect */}
            <div className={`absolute inset-0 bg-gradient-to-r ${card.color} opacity-0 group-hover:opacity-10 rounded-xl transition-opacity duration-300`} />
            
            <div className="relative z-10">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-slate-300 text-sm font-medium">{card.title}</h3>
                <button className="p-1 rounded-full bg-slate-700/50 hover:bg-slate-600/50 transition-colors">
                  <PlusIcon className="h-4 w-4 text-slate-400" />
                </button>
              </div>

              {/* Main stat */}
              <div className="mb-2">
                <span className="text-2xl font-bold text-white">
                  {card.value.toLocaleString()}
                </span>
              </div>

              {/* Average */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">
                  Avg: {card.average.toFixed(1)}
                </span>
                <div className="w-16 h-1 bg-slate-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full bg-gradient-to-r ${card.color} rounded-full`}
                    style={{ width: `${Math.min((card.value / (card.average * 10)) * 100, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Attendance Trends</h3>
          <div className="h-64 bg-slate-700/30 rounded-lg flex items-center justify-center">
            <span className="text-slate-400">Chart placeholder</span>
          </div>
        </div>
        
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Weekly Breakdown</h3>
          <div className="h-64 bg-slate-700/30 rounded-lg flex items-center justify-center">
            <span className="text-slate-400">Chart placeholder</span>
          </div>
        </div>
      </div>

      {/* Custom Date Range Modal */}
      {showCustomDateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-white">Custom Date Range</h3>
              <button
                onClick={() => setShowCustomDateModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={customStartDate}
                  onChange={(e) => setCustomStartDate(e.target.value)}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={customEndDate}
                  onChange={(e) => setCustomEndDate(e.target.value)}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleCustomDateSubmit}
                  disabled={!customStartDate || !customEndDate}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Apply Date Range
                </button>
                <button
                  onClick={() => setShowCustomDateModal(false)}
                  className="flex-1 bg-slate-600 hover:bg-slate-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Breakdown Modal */}
      {showBreakdownModal && selectedStat && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-white">
                {getBreakdownData(selectedStat).title}
              </h3>
              <button
                onClick={() => setShowBreakdownModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ×
              </button>
            </div>
            <div className="space-y-3">
              {getBreakdownData(selectedStat).items.map((item, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-slate-700/30 rounded-lg">
                  <span className="text-slate-300">{item.label}</span>
                  <span className="text-white font-semibold">{item.value.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 