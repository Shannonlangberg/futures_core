import React, { useState, useEffect } from 'react';
import { MapPinIcon, PlusIcon, PencilIcon, TrashIcon, BuildingOfficeIcon } from '@heroicons/react/24/outline';

const Campuses = () => {
  const [campuses, setCampuses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedCampus, setSelectedCampus] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    status: 'active',
    pastor: ''
  });

  useEffect(() => {
    fetchCampuses();
  }, []);

  const fetchCampuses = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/campuses', {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setCampuses(data.campuses || []);
      }
    } catch (error) {
      console.error('Error fetching campuses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCampus = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/campuses/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        credentials: 'include',
      });
      
      if (response.ok) {
        setShowCreateModal(false);
        setFormData({ name: '', address: '', status: 'active', pastor: '' });
        fetchCampuses();
      }
    } catch (error) {
      console.error('Error creating campus:', error);
    }
  };

  const handleEditCampus = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`/api/campuses/${selectedCampus.id}/edit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        credentials: 'include',
      });
      
      if (response.ok) {
        setShowEditModal(false);
        setSelectedCampus(null);
        setFormData({ name: '', address: '', status: 'active', pastor: '' });
        fetchCampuses();
      }
    } catch (error) {
      console.error('Error updating campus:', error);
    }
  };

  const handleDeleteCampus = async (campusId) => {
    if (window.confirm('Are you sure you want to delete this campus?')) {
      try {
        const response = await fetch(`/api/campuses/${campusId}/delete`, {
          method: 'POST',
          credentials: 'include',
        });
        
        if (response.ok) {
          fetchCampuses();
        }
      } catch (error) {
        console.error('Error deleting campus:', error);
      }
    }
  };

  const openEditModal = (campus) => {
    setSelectedCampus(campus);
    setFormData({
      name: campus.name,
      address: campus.address || '',
      status: campus.status || 'active',
      pastor: campus.pastor || ''
    });
    setShowEditModal(true);
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'bg-green-500/10 text-green-400 border-green-500/20',
      inactive: 'bg-red-500/10 text-red-400 border-red-500/20',
      pending: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
    };
    return colors[status] || colors.active;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Campuses</h1>
          <p className="text-slate-400 mt-1">Manage church campuses and locations</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <PlusIcon className="w-4 h-4" />
          <span>Add Campus</span>
        </button>
      </div>

      {/* Campuses Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full text-center py-12">
            <div className="inline-flex items-center space-x-2 text-blue-400">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>
              <span>Loading campuses...</span>
            </div>
          </div>
        ) : campuses.length > 0 ? (
          campuses.map((campus) => (
            <div key={campus.id} className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center">
                    <BuildingOfficeIcon className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">{campus.name}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(campus.status)}`}>
                      {campus.status}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => openEditModal(campus)}
                    className="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteCampus(campus.id)}
                    className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-700/50 rounded-lg transition-colors"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="space-y-3">
                {campus.address && (
                  <div className="flex items-start space-x-2">
                    <MapPinIcon className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-300 text-sm">{campus.address}</span>
                  </div>
                )}
                
                {campus.pastor && (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-slate-600 rounded-full flex items-center justify-center">
                      <span className="text-slate-400 text-xs">👤</span>
                    </div>
                    <span className="text-slate-300 text-sm">Pastor: {campus.pastor}</span>
                  </div>
                )}
                
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-slate-600 rounded-full flex items-center justify-center">
                    <span className="text-slate-400 text-xs">📊</span>
                  </div>
                  <span className="text-slate-300 text-sm">Campus ID: {campus.id}</span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <div className="w-16 h-16 bg-slate-700/50 rounded-full flex items-center justify-center mx-auto mb-4">
              <BuildingOfficeIcon className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">No Campuses Found</h3>
            <p className="text-slate-400">Create your first campus to get started</p>
          </div>
        )}
      </div>

      {/* Create Campus Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-white mb-4">Create New Campus</h3>
            <form onSubmit={handleCreateCampus} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Campus Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Address</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="pending">Pending</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Pastor</label>
                <input
                  type="text"
                  value={formData.pastor}
                  onChange={(e) => setFormData({...formData, pastor: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                />
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Create Campus
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Campus Modal */}
      {showEditModal && selectedCampus && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-white mb-4">Edit Campus</h3>
            <form onSubmit={handleEditCampus} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Campus Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Address</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="pending">Pending</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Pastor</label>
                <input
                  type="text"
                  value={formData.pastor}
                  onChange={(e) => setFormData({...formData, pastor: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                />
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Update Campus
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Campuses; 