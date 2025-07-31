import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  BellIcon,
  UserCircleIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  ShieldCheckIcon,
  Cog6ToothIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';

const Settings = () => {
  const [userRole, setUserRole] = useState('user');
  const [userName, setUserName] = useState('');
  const location = useLocation();

  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        const response = await fetch('/api/session');
        const data = await response.json();
        if (data.authenticated) {
          setUserRole(data.role || 'user');
          setUserName(data.full_name || 'User');
        }
      } catch (error) {
        console.error('Error fetching session data:', error);
      }
    };

    fetchSessionData();
  }, []);

  const settingsSections = [
    {
      title: 'General',
      items: [
        { name: 'Notifications', href: '/settings/notifications', icon: BellIcon, description: 'Manage your notification preferences' },
        { name: 'Profile', href: '/settings/profile', icon: UserCircleIcon, description: 'Update your personal information' },
      ]
    }
  ];

  // Add admin-only sections
  if (userRole === 'admin') {
    settingsSections.push(
      {
        title: 'Administration',
        items: [
          { name: 'Users', href: '/users', icon: UserGroupIcon, description: 'Manage user accounts and permissions' },
          { name: 'Campuses', href: '/campuses', icon: BuildingOfficeIcon, description: 'Manage campus locations and settings' },
          { name: 'Security', href: '/settings/security', icon: ShieldCheckIcon, description: 'Configure security settings' },
        ]
      }
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <Link
            to="/dashboard"
            className="mr-4 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5 text-slate-400" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-white">Settings</h1>
            <p className="text-slate-400">Manage your account and preferences</p>
          </div>
        </div>
        
        {/* User Info Card */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">
                {userName.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">{userName}</h2>
              <p className="text-slate-400 capitalize">{userRole}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="space-y-8">
        {settingsSections.map((section) => (
          <div key={section.title}>
            <h3 className="text-lg font-semibold text-white mb-4">{section.title}</h3>
            <div className="grid gap-4">
              {section.items.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="flex items-center p-6 bg-slate-800/50 border border-slate-700 rounded-xl hover:border-slate-600 hover:bg-slate-800 transition-all duration-200 group"
                >
                  <div className="flex items-center justify-center w-12 h-12 bg-slate-700 rounded-lg mr-4 group-hover:bg-slate-600 transition-colors">
                    <item.icon className="h-6 w-6 text-slate-400 group-hover:text-white transition-colors" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-medium text-white group-hover:text-blue-400 transition-colors">
                      {item.name}
                    </h4>
                    <p className="text-slate-400 text-sm">{item.description}</p>
                  </div>
                  <div className="text-slate-400 group-hover:text-white transition-colors">
                    <Cog6ToothIcon className="h-5 w-5" />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Settings; 