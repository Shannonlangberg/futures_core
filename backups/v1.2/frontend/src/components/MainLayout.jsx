import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  ClipboardIcon,
  HeartIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  MapPinIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  BellIcon,
  ShieldCheckIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const MainLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [userRole, setUserRole] = useState('user');
  const [userName, setUserName] = useState('');
  const location = useLocation();

  // Fetch user session data on component mount
  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        const response = await fetch('/api/session');
        const data = await response.json();
        if (data.authenticated) {
          setUserRole(data.role || 'user');
          setUserName(data.full_name || 'User');
          console.log('User session data:', data); // Debug log
        }
      } catch (error) {
        console.error('Error fetching session data:', error);
      }
    };

    fetchSessionData();
  }, []);

  // Filter navigation items based on user role and permissions
  const getNavigationItems = () => {
    const allItems = [
      { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, roles: ['admin', 'senior_leader', 'campus_pastor'] },
      { name: 'Input', href: '/', icon: ClipboardIcon, roles: ['admin', 'senior_leader', 'campus_pastor', 'pastor', 'finance'] },
      { name: 'Pulse', href: '/query', icon: ChartBarIcon, roles: ['admin', 'senior_leader', 'campus_pastor'] },
      { name: 'Heartbeat', href: '/heartbeat', icon: HeartIcon, roles: ['admin', 'senior_leader', 'campus_pastor'] },
      { name: 'Passport', href: '/journey', icon: UserCircleIcon, roles: ['admin', 'senior_leader', 'campus_pastor'] },
    ];

    // Filter items based on user role
    return allItems.filter(item => item.roles.includes(userRole));
  };

  const navigation = getNavigationItems();

  // Settings menu items based on user role
  const getSettingsItems = () => {
    const baseItems = [
      { name: 'Notifications', href: '/settings/notifications', icon: BellIcon, show: true },
      { name: 'Profile', href: '/settings/profile', icon: UserCircleIcon, show: true },
    ];

    // Admin-only items
    if (userRole === 'admin') {
      baseItems.push(
        { name: 'Users', href: '/users', icon: UserGroupIcon, show: true },
        { name: 'Campuses', href: '/campuses', icon: BuildingOfficeIcon, show: true },
        { name: 'Security', href: '/settings/security', icon: ShieldCheckIcon, show: true }
      );
    }

    return baseItems.filter(item => item.show);
  };

  const handleLogout = async () => {
    try {
      await fetch('/logout', {
        method: 'GET',
        credentials: 'include',
      });
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
      window.location.href = '/login';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        bg-slate-900 border-r border-slate-700/50
      `}>
        <div className="flex h-full flex-col">
          {/* Logo/Brand */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-slate-700/50">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">FC</span>
              </div>
              <span className="text-white font-semibold text-lg">Futures Core</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200
                    ${isActive 
                      ? 'bg-gradient-to-r from-blue-600/20 to-purple-600/20 text-white border border-blue-500/30 shadow-lg shadow-blue-500/20' 
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className={`mr-3 h-5 w-5 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                  {item.name}
                </Link>
              );
            })}

            {/* Settings Dropdown */}
            <div className="relative">
              <button
                onClick={() => setSettingsOpen(!settingsOpen)}
                className={`
                  w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200
                  ${settingsOpen 
                    ? 'bg-gradient-to-r from-blue-600/20 to-purple-600/20 text-white border border-blue-500/30 shadow-lg shadow-blue-500/20' 
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }
                `}
              >
                <div className="flex items-center">
                  <Cog6ToothIcon className={`mr-3 h-5 w-5 ${settingsOpen ? 'text-blue-400' : 'text-slate-400'}`} />
                  Settings
                </div>
                <ChevronDownIcon className={`h-4 w-4 transition-transform duration-200 ${settingsOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Settings Dropdown Menu */}
              {settingsOpen && (
                <div className="absolute left-0 right-0 top-full mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-lg z-10">
                  {getSettingsItems().map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`
                          flex items-center px-4 py-3 text-sm font-medium transition-all duration-200
                          ${isActive 
                            ? 'bg-blue-600/20 text-blue-400' 
                            : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
                          }
                        `}
                        onClick={() => {
                          setSettingsOpen(false);
                          setSidebarOpen(false);
                        }}
                      >
                        <item.icon className={`mr-3 h-5 w-5 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                        {item.name}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          </nav>

          {/* Footer with User Info and Logout */}
          <div className="p-4 border-t border-slate-700/50 space-y-3">
            {/* User Info */}
            <div className="px-4 py-2 bg-slate-800/50 rounded-lg">
              <div className="text-sm text-slate-300 font-medium">{userName}</div>
              <div className="text-xs text-slate-500 capitalize">{userRole}</div>
            </div>
            
            <button
              onClick={handleLogout}
              className="w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 text-red-300 hover:text-red-200 hover:bg-red-900/20"
            >
              <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5" />
              Logout
            </button>
            <div className="text-xs text-slate-500 text-center">
              Futures Core
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Mobile header */}
        <div className="lg:hidden flex items-center justify-between p-4 border-b border-slate-700/50">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
          <span className="text-white font-semibold">Futures Core</span>
          <button
            onClick={handleLogout}
            className="p-2 rounded-md text-red-400 hover:text-red-300 hover:bg-red-900/20"
          >
            <ArrowRightOnRectangleIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout; 