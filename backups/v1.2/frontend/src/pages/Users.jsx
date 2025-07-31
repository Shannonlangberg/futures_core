import React, { useState, useEffect } from 'react';
import { UserIcon, PlusIcon, PencilIcon, TrashIcon, EyeIcon } from '@heroicons/react/24/outline';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    full_name: '',
    role: 'campus_pastor',
    campus: 'all_campuses',
    permissions: []
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/users', {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/users/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        credentials: 'include',
      });
      
      if (response.ok) {
        setShowCreateModal(false);
        setFormData({ username: '', password: '', email: '', full_name: '', role: 'campus_pastor', campus: 'all_campuses', permissions: [] });
        fetchUsers();
      }
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  const handleEditUser = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`/api/users/${selectedUser.id}/edit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        credentials: 'include',
      });
      
      if (response.ok) {
        setShowEditModal(false);
        setSelectedUser(null);
        setFormData({ username: '', password: '', email: '', full_name: '', role: 'campus_pastor', campus: 'all_campuses', permissions: [] });
        fetchUsers();
      }
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        const response = await fetch(`/api/users/${userId}/delete`, {
          method: 'POST',
          credentials: 'include',
        });
        
        if (response.ok) {
          fetchUsers();
        }
      } catch (error) {
        console.error('Error deleting user:', error);
      }
    }
  };

  const openEditModal = (user) => {
    setSelectedUser(user);
    setFormData({
      username: user.username,
      password: '',
      email: user.email || '',
      full_name: user.full_name || user.username,
      role: user.role,
      campus: user.campus || 'all_campuses',
      permissions: user.permissions || []
    });
    setShowEditModal(true);
  };

  const roles = [
    { id: 'admin', name: 'Admin', description: 'Full system access' },
    { id: 'senior_pastor', name: 'Senior Pastor', description: 'Network leadership access' },
    { id: 'lead_pastor', name: 'Lead Pastor', description: 'Campus leadership access' },
    { id: 'campus_pastor', name: 'Campus Pastor', description: 'Campus-specific access' },
    { id: 'finance', name: 'Finance', description: 'Finance team access' }
  ];

  const getRoleColor = (role) => {
    const colors = {
      admin: 'bg-red-500/10 text-red-400 border-red-500/20',
      senior_pastor: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      lead_pastor: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      campus_pastor: 'bg-green-500/10 text-green-400 border-green-500/20',
      finance: 'bg-orange-500/10 text-orange-400 border-orange-500/20'
    };
    return colors[role] || colors.campus_pastor;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Users</h1>
          <p className="text-slate-400 mt-1">Manage user accounts and permissions</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <PlusIcon className="w-4 h-4" />
          <span>Add User</span>
        </button>
      </div>

      {/* Users List */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-flex items-center space-x-2 text-blue-400">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>
              <span>Loading users...</span>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {users.map((user) => (
              <div key={user.id} className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-slate-600 rounded-full flex items-center justify-center">
                    <UserIcon className="w-5 h-5 text-slate-400" />
                  </div>
                  <div>
                    <div className="text-white font-medium">{user.username}</div>
                    <div className="text-slate-400 text-sm">{user.email || 'No email'}</div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getRoleColor(user.role)}`}>
                    {roles.find(r => r.id === user.role)?.name || user.role}
                  </span>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => openEditModal(user)}
                      className="p-2 text-slate-400 hover:text-blue-400 hover:bg-slate-700/50 rounded-lg transition-colors"
                    >
                      <PencilIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-700/50 rounded-lg transition-colors"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
            
            {users.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-slate-700/50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <UserIcon className="w-8 h-8 text-slate-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">No Users Found</h3>
                <p className="text-slate-400">Create your first user to get started</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-white mb-4">Create New User</h3>
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Username</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  placeholder="user@futures.church"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Full Name</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  placeholder="Full Name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Role</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                >
                  {roles.map(role => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Campus</label>
                <select
                  value={formData.campus}
                  onChange={(e) => setFormData({...formData, campus: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                >
                  <option value="">Select Campus</option>
                  <option value="all_campuses">All Campuses</option>
                  <option value="paradise">Paradise</option>
                  <option value="adelaide_city">Adelaide City</option>
                  <option value="salisbury">Salisbury</option>
                  <option value="south">South</option>
                  <option value="mount_barker">Mount Barker</option>
                  <option value="clare_valley">Clare Valley</option>
                  <option value="victor_harbour">Victor Harbour</option>
                  <option value="copper_coast">Copper Coast</option>
                  <option value="online">Online</option>
                </select>
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
                  Create User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {showEditModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-white mb-4">Edit User</h3>
            <form onSubmit={handleEditUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Username</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Password (leave blank to keep current)</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  placeholder="user@futures.church"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Full Name</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                  placeholder="Full Name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Role</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                >
                  {roles.map(role => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Campus</label>
                <select
                  value={formData.campus}
                  onChange={(e) => setFormData({...formData, campus: e.target.value})}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-white"
                >
                  <option value="">Select Campus</option>
                  <option value="all_campuses">All Campuses</option>
                  <option value="paradise">Paradise</option>
                  <option value="adelaide_city">Adelaide City</option>
                  <option value="salisbury">Salisbury</option>
                  <option value="south">South</option>
                  <option value="mount_barker">Mount Barker</option>
                  <option value="clare_valley">Clare Valley</option>
                  <option value="victor_harbour">Victor Harbour</option>
                  <option value="copper_coast">Copper Coast</option>
                  <option value="online">Online</option>
                </select>
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
                  Update User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users; 