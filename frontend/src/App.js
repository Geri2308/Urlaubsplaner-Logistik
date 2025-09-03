import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { format, addMonths, subMonths, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, isToday, startOfYear, endOfYear, eachMonthOfInterval } from 'date-fns';
import { de } from 'date-fns/locale';
import { 
  Calendar,
  Users,
  Plus,
  Download,
  Upload,
  Printer,
  Search,
  Filter,
  Settings,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  Clock,
  X,
  UserPlus,
  Edit2,
  Trash2,
  Star,
  Minus,
  Lock,
  LogOut
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Login credentials
const VALID_CODE = "9999";

// Login Component
const LoginScreen = ({ onLogin }) => {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    // Simulate authentication delay
    setTimeout(() => {
      if (code === VALID_CODE) {
        localStorage.setItem('urlaubsplaner_auth', 'true');
        onLogin();
      } else {
        setError("Ungültiger Code. Bitte versuchen Sie es erneut.");
        setCode("");
      }
      setLoading(false);
    }, 800);
  };

  const handleCodeChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 4);
    setCode(value);
    if (error) setError("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="mx-auto h-20 w-20 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <Calendar className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Urlaubsplaner</h1>
          <p className="text-gray-600">Bitte geben Sie Ihren 4-stelligen Code ein</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Lock className="w-4 h-4 inline mr-2" />
                Zugangscode
              </label>
              <input
                type="password"
                value={code}
                onChange={handleCodeChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-center text-2xl font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="●●●●"
                maxLength="4"
                autoFocus
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                <AlertTriangle className="w-4 h-4 inline mr-2" />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={code.length !== 4 || loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Überprüfung...
                </div>
              ) : (
                "Anmelden"
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              Sicheres Urlaubsplanungssystem
            </p>
          </div>
        </div>

        {/* Info */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>🔒 Ihre Daten sind geschützt</p>
        </div>
      </div>
    </div>
  );
};

// Star Rating Component
const StarRating = ({ rating, onRatingChange, readonly = false }) => {
  const stars = [1, 2, 3, 4, 5];
  
  return (
    <div className="flex space-x-1">
      {stars.map((star) => (
        <button
          key={star}
          type="button"
          disabled={readonly}
          onClick={() => !readonly && onRatingChange(star)}
          className={`w-5 h-5 ${readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110'} transition-transform`}
        >
          <Star
            className={`w-full h-full ${
              star <= rating
                ? 'text-yellow-400 fill-yellow-400'
                : 'text-gray-300'
            }`}
          />
        </button>
      ))}
    </div>
  );
};

// Skill Management Component
const SkillManager = ({ skills, onSkillsChange }) => {
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillRating, setNewSkillRating] = useState(3);

  const addSkill = () => {
    if (newSkillName.trim()) {
      const newSkill = {
        name: newSkillName.trim(),
        rating: newSkillRating
      };
      onSkillsChange([...skills, newSkill]);
      setNewSkillName('');
      setNewSkillRating(3);
    }
  };

  const removeSkill = (index) => {
    const updatedSkills = skills.filter((_, i) => i !== index);
    onSkillsChange(updatedSkills);
  };

  const updateSkillRating = (index, rating) => {
    const updatedSkills = [...skills];
    updatedSkills[index].rating = rating;
    onSkillsChange(updatedSkills);
  };

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Fähigkeiten & Skills
      </label>
      
      {/* Existing Skills */}
      {skills.map((skill, index) => (
        <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium">{skill.name}</span>
            <StarRating 
              rating={skill.rating} 
              onRatingChange={(rating) => updateSkillRating(index, rating)}
            />
          </div>
          <button
            type="button"
            onClick={() => removeSkill(index)}
            className="text-red-500 hover:text-red-700"
          >
            <Minus className="w-4 h-4" />
          </button>
        </div>
      ))}

      {/* Add New Skill */}
      <div className="flex items-center space-x-2 p-2 border border-gray-200 rounded">
        <input
          type="text"
          value={newSkillName}
          onChange={(e) => setNewSkillName(e.target.value)}
          placeholder="Neue Fähigkeit..."
          className="flex-1 border-none outline-none text-sm"
          onKeyPress={(e) => e.key === 'Enter' && addSkill()}
        />
        <StarRating 
          rating={newSkillRating} 
          onRatingChange={setNewSkillRating}
        />
        <button
          type="button"
          onClick={addSkill}
          className="text-green-600 hover:text-green-800"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

// Vacation Types
const VACATION_TYPES = {
  URLAUB: { label: 'Urlaub', color: 'bg-blue-500', textColor: 'text-blue-700' },
  KRANKHEIT: { label: 'Krankheit', color: 'bg-red-600', textColor: 'text-red-800' },
  SONDERURLAUB: { label: 'Sonderurlaub', color: 'bg-green-500', textColor: 'text-green-700' }
};

// Toolbar Component (Word-style)
const Toolbar = ({ 
  onNewVacation, 
  onNewEmployee,
  onExport, 
  onImport, 
  onPrint, 
  currentView, 
  onViewChange,
  searchTerm,
  onSearchChange,
  showFilters,
  onToggleFilters,
  employees,
  settings,
  onLogout
}) => {
  return (
    <div className="bg-white border-b border-gray-200 p-3">
      {/* Main Toolbar */}
      <div className="flex items-center space-x-1 mb-2">
        {/* File Group */}
        <div className="flex items-center space-x-1 border-r border-gray-300 pr-3 mr-3">
          <button
            onClick={onNewVacation}
            className="flex items-center px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-1" />
            Neuer Urlaub
          </button>
          <button
            onClick={onNewEmployee}
            className="flex items-center px-3 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
          >
            <UserPlus className="w-4 h-4 mr-1" />
            Mitarbeiter
          </button>
          <button
            onClick={onExport}
            className="flex items-center px-2 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded transition-colors"
            title="Exportieren"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={onImport}
            className="flex items-center px-2 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded transition-colors"
            title="Importieren"
          >
            <Upload className="w-4 h-4" />
          </button>
          <button
            onClick={onPrint}
            className="flex items-center px-2 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded transition-colors"
            title="Drucken"
          >
            <Printer className="w-4 h-4" />
          </button>
        </div>

        {/* View Group */}
        <div className="flex items-center space-x-1 border-r border-gray-300 pr-3 mr-3">
          <button
            onClick={() => onViewChange('month')}
            className={`flex items-center px-3 py-2 text-sm rounded transition-colors ${
              currentView === 'month' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Calendar className="w-4 h-4 mr-1" />
            Monat
          </button>
          <button
            onClick={() => onViewChange('year')}
            className={`flex items-center px-3 py-2 text-sm rounded transition-colors ${
              currentView === 'year' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Calendar className="w-4 h-4 mr-1" />
            Jahr
          </button>
          <button
            onClick={() => onViewChange('team')}
            className={`flex items-center px-3 py-2 text-sm rounded transition-colors ${
              currentView === 'team' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Users className="w-4 h-4 mr-1" />
            Team
          </button>
        </div>

        {/* Search & Filter Group */}
        <div className="flex items-center space-x-2 flex-1">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Mitarbeiter suchen..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-8 pr-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={onToggleFilters}
            className={`flex items-center px-3 py-2 text-sm rounded transition-colors ${
              showFilters ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Filter className="w-4 h-4 mr-1" />
            Filter
          </button>
        </div>

        {/* Settings & Logout */}
        <div className="flex items-center space-x-1">
          <button className="flex items-center px-2 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded transition-colors">
            <Settings className="w-4 h-4" />
          </button>
          <button
            onClick={onLogout}
            className="flex items-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded transition-colors"
            title="Abmelden"
          >
            <LogOut className="w-4 h-4 mr-1" />
            Abmelden
          </button>
        </div>
      </div>

      {/* Breadcrumb/Status Bar */}
      <div className="text-xs text-gray-500 flex items-center justify-between">
        <span>Urlaubsplaner • {format(new Date(), 'MMMM yyyy', { locale: de })}</span>
        <span>{employees.length} Mitarbeiter • Max. {settings.max_concurrent_calculated} gleichzeitig ({settings.max_concurrent_percentage}%)</span>
      </div>
    </div>
  );
};

// Calendar Navigation
const CalendarNavigation = ({ currentDate, onPrevious, onNext, view }) => {
  const getTitle = () => {
    switch (view) {
      case 'month':
        return format(currentDate, 'MMMM yyyy', { locale: de });
      case 'year':
        return format(currentDate, 'yyyy', { locale: de });
      default:
        return format(currentDate, 'MMMM yyyy', { locale: de });
    }
  };

  return (
    <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
      <button
        onClick={onPrevious}
        className="flex items-center px-3 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
      >
        <ChevronLeft className="w-5 h-5" />
      </button>
      <h2 className="text-xl font-semibold text-gray-900 capitalize">
        {getTitle()}
      </h2>
      <button
        onClick={onNext}
        className="flex items-center px-3 py-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
      >
        <ChevronRight className="w-5 h-5" />
      </button>
    </div>
  );
};

// Employee Dialog Component
const EmployeeDialog = ({ isOpen, onClose, onSave, editingEmployee = null }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'employee',
    skills: []
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editingEmployee) {
      setFormData({
        name: editingEmployee.name,
        email: editingEmployee.email,
        role: editingEmployee.role,
        skills: editingEmployee.skills || []
      });
    } else {
      setFormData({
        name: '',
        email: '',
        role: 'employee',
        skills: []
      });
    }
    setError('');
  }, [editingEmployee, isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (editingEmployee) {
        await axios.put(`${API}/employees/${editingEmployee.id}`, formData);
      } else {
        await axios.post(`${API}/employees`, formData);
      }
      onSave();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ein Fehler ist aufgetreten');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">
            {editingEmployee ? 'Mitarbeiter bearbeiten' : 'Neuer Mitarbeiter'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Max Mustermann"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              E-Mail
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="max.mustermann@firma.de"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Rolle
            </label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="employee">Mitarbeiter</option>
              <option value="admin">Administrator</option>
              <option value="leiharbeiter">Leiharbeiter</option>
            </select>
          </div>

          <SkillManager
            skills={formData.skills}
            onSkillsChange={(skills) => setFormData({ ...formData, skills })}
          />

          <div className="flex justify-end space-x-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Speichern...' : (editingEmployee ? 'Aktualisieren' : 'Erstellen')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Vacation Entry Dialog
const VacationDialog = ({ isOpen, onClose, onSave, employees, editingEntry = null }) => {
  const [formData, setFormData] = useState({
    employee_id: '',
    start_date: '',
    end_date: '',
    vacation_type: 'URLAUB',
    notes: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editingEntry) {
      setFormData({
        employee_id: editingEntry.employee_id,
        start_date: editingEntry.start_date,
        end_date: editingEntry.end_date,
        vacation_type: editingEntry.vacation_type,
        notes: editingEntry.notes || ''
      });
    } else {
      setFormData({
        employee_id: '',
        start_date: '',
        end_date: '',
        vacation_type: 'URLAUB',
        notes: ''
      });
    }
    setError('');
  }, [editingEntry, isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (editingEntry) {
        await axios.put(`${API}/vacation-entries/${editingEntry.id}`, formData);
      } else {
        await axios.post(`${API}/vacation-entries`, formData);
      }
      onSave();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ein Fehler ist aufgetreten');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold">
            {editingEntry ? 'Urlaub bearbeiten' : 'Neuer Urlaub'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mitarbeiter
            </label>
            <select
              value={formData.employee_id}
              onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Mitarbeiter auswählen</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.name}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Von
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bis
              </label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Art
            </label>
            <select
              value={formData.vacation_type}
              onChange={(e) => setFormData({ ...formData, vacation_type: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {Object.entries(VACATION_TYPES).map(([key, type]) => (
                <option key={key} value={key}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notizen
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Optionale Notizen..."
            />
          </div>

          <div className="flex justify-between pt-4">
            {editingEntry && (
              <button
                type="button"
                onClick={async () => {
                  if (window.confirm('Urlaubseintrag wirklich löschen?')) {
                    try {
                      await axios.delete(`${API}/vacation-entries/${editingEntry.id}`);
                      onSave(); // Reload data
                      onClose();
                    } catch (err) {
                      alert('Fehler beim Löschen des Urlaubseintrags');
                    }
                  }
                }}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                <Trash2 className="w-4 h-4 mr-1 inline" />
                Löschen
              </button>
            )}
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
              >
                Abbrechen
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Speichern...' : (editingEntry ? 'Aktualisieren' : 'Erstellen')}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

// Month Calendar View
const MonthCalendarView = ({ currentDate, vacationEntries, employees, onDateClick, onEntryClick }) => {
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarDays = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const getVacationsForDay = (day) => {
    return vacationEntries.filter(entry => {
      const entryStart = new Date(entry.start_date);
      const entryEnd = new Date(entry.end_date);
      return day >= entryStart && day <= entryEnd;
    });
  };

  const getDayClasses = (day) => {
    const isCurrentMonth = isSameMonth(day, currentDate);
    const isCurrentDay = isToday(day);
    const isWeekend = day.getDay() === 0 || day.getDay() === 6;
    
    let classes = "min-h-24 p-1 border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors ";
    
    if (!isCurrentMonth) classes += "bg-gray-50 text-gray-400 ";
    if (isCurrentDay) classes += "bg-blue-50 border-blue-300 ";
    if (isWeekend && isCurrentMonth) classes += "bg-gray-100 ";
    
    return classes;
  };

  return (
    <div className="bg-white">
      {/* Calendar Header */}
      <div className="grid grid-cols-7 border-b border-gray-200">
        {['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'].map((day) => (
          <div key={day} className="p-3 text-center text-sm font-medium text-gray-500 bg-gray-50">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Body */}
      <div className="grid grid-cols-7">
        {calendarDays.map((day) => {
          const dayVacations = getVacationsForDay(day);
          
          return (
            <div
              key={day.toISOString()}
              className={getDayClasses(day)}
              onClick={() => onDateClick(day)}
            >
              <div className="flex justify-between items-start">
                <span className="text-sm font-medium">
                  {format(day, 'd')}
                </span>
                {dayVacations.length > 0 && (
                  <span className="text-xs bg-blue-500 text-white rounded-full px-1 min-w-4 text-center">
                    {dayVacations.length}
                  </span>
                )}
              </div>
              
              <div className="mt-1 space-y-1">
                {dayVacations.slice(0, 3).map((vacation) => {
                  const vacationType = VACATION_TYPES[vacation.vacation_type];
                  return (
                    <div
                      key={vacation.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        onEntryClick(vacation);
                      }}
                      className={`text-xs p-1 rounded truncate cursor-pointer hover:opacity-80 ${vacationType.color} text-white`}
                      title={`${vacation.employee_name} - ${vacationType.label}`}
                    >
                      {vacation.employee_name}
                    </div>
                  );
                })}
                {dayVacations.length > 3 && (
                  <div className="text-xs text-gray-500">
                    +{dayVacations.length - 3} weitere
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Year Calendar View
const YearCalendarView = ({ currentDate, vacationEntries, onMonthClick }) => {
  const yearStart = startOfYear(currentDate);
  const yearEnd = endOfYear(currentDate);
  const yearMonths = eachMonthOfInterval({ start: yearStart, end: yearEnd });

  const getVacationsForMonth = (month) => {
    const monthStart = startOfMonth(month);
    const monthEnd = endOfMonth(month);
    
    return vacationEntries.filter(entry => {
      const entryStart = new Date(entry.start_date);
      const entryEnd = new Date(entry.end_date);
      return (entryStart <= monthEnd && entryEnd >= monthStart);
    });
  };

  const getMonthVacationStats = (month) => {
    const monthVacations = getVacationsForMonth(month);
    const uniqueEmployees = [...new Set(monthVacations.map(v => v.employee_id))];
    
    const typeStats = {
      URLAUB: monthVacations.filter(v => v.vacation_type === 'URLAUB').length,
      KRANKHEIT: monthVacations.filter(v => v.vacation_type === 'KRANKHEIT').length,
      SONDERURLAUB: monthVacations.filter(v => v.vacation_type === 'SONDERURLAUB').length
    };

    return {
      totalEntries: monthVacations.length,
      uniqueEmployees: uniqueEmployees.length,
      typeStats
    };
  };

  return (
    <div className="bg-white p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {yearMonths.map((month) => {
          const stats = getMonthVacationStats(month);
          
          return (
            <div
              key={month.toISOString()}
              onClick={() => onMonthClick(month)}
              className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
            >
              <div className="text-center mb-3">
                <h3 className="text-lg font-semibold text-gray-900 capitalize">
                  {format(month, 'MMMM', { locale: de })}
                </h3>
                <p className="text-sm text-gray-500">
                  {format(month, 'yyyy')}
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Urlaubseinträge:</span>
                  <span className="font-medium">{stats.totalEntries}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Betroffene Mitarbeiter:</span>
                  <span className="font-medium">{stats.uniqueEmployees}</span>
                </div>

                {stats.totalEntries > 0 && (
                  <div className="pt-2 border-t border-gray-100">
                    <div className="text-xs text-gray-500 mb-1">Aufschlüsselung:</div>
                    <div className="space-y-1">
                      {stats.typeStats.URLAUB > 0 && (
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
                            <span className="text-xs">Urlaub</span>
                          </div>
                          <span className="text-xs font-medium">{stats.typeStats.URLAUB}</span>
                        </div>
                      )}
                      {stats.typeStats.KRANKHEIT > 0 && (
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-3 h-3 bg-red-500 rounded mr-2"></div>
                            <span className="text-xs">Krankheit</span>
                          </div>
                          <span className="text-xs font-medium">{stats.typeStats.KRANKHEIT}</span>
                        </div>
                      )}
                      {stats.typeStats.SONDERURLAUB > 0 && (
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
                            <span className="text-xs">Sonderurlaub</span>
                          </div>
                          <span className="text-xs font-medium">{stats.typeStats.SONDERURLAUB}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {stats.totalEntries === 0 && (
                  <div className="text-center py-2">
                    <span className="text-xs text-gray-400">Keine Einträge</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [currentView, setCurrentView] = useState('month');
  const [employees, setEmployees] = useState([]);
  const [vacationEntries, setVacationEntries] = useState([]);
  const [showVacationDialog, setShowVacationDialog] = useState(false);
  const [showEmployeeDialog, setShowEmployeeDialog] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [settings, setSettings] = useState({
    max_concurrent_percentage: 30,
    total_employees: 0,
    max_concurrent_calculated: 1
  });

  // Check authentication on app load
  useEffect(() => {
    const authStatus = localStorage.getItem('urlaubsplaner_auth');
    if (authStatus === 'true') {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  // Load data when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated]);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('urlaubsplaner_auth');
    setIsAuthenticated(false);
    // Clear all data
    setEmployees([]);
    setVacationEntries([]);
    setCurrentView('month');
    setSearchTerm('');
    setShowFilters(false);
    setError('');
  };

  const loadData = async () => {
    try {
      setLoading(true);
      // Add cache buster to ensure we get fresh data  
      const cacheBuster = `?t=${Date.now()}`;
      const [employeesRes, vacationRes, settingsRes] = await Promise.all([
        axios.get(`${API}/employees${cacheBuster}`),
        axios.get(`${API}/vacation-entries${cacheBuster}`),
        axios.get(`${API}/settings${cacheBuster}`)
      ]);
      setEmployees(employeesRes.data);
      setVacationEntries(vacationRes.data);
      setSettings(settingsRes.data);
      setError('');
    } catch (err) {
      setError('Fehler beim Laden der Daten');
      console.error('Loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Navigation handlers
  const handlePrevious = () => {
    if (currentView === 'month') {
      setCurrentDate(subMonths(currentDate, 1));
    } else if (currentView === 'year') {
      setCurrentDate(new Date(currentDate.getFullYear() - 1, currentDate.getMonth()));
    }
  };

  const handleNext = () => {
    if (currentView === 'month') {
      setCurrentDate(addMonths(currentDate, 1));
    } else if (currentView === 'year') {
      setCurrentDate(new Date(currentDate.getFullYear() + 1, currentDate.getMonth()));
    }
  };

  // Dialog handlers
  const handleNewVacation = () => {
    setEditingEntry(null);
    setShowVacationDialog(true);
  };

  const handleNewEmployee = () => {
    setEditingEmployee(null);
    setShowEmployeeDialog(true);
  };

  const handleEditVacation = (entry) => {
    setEditingEntry(entry);
    setShowVacationDialog(true);
  };

  const handleEditEmployee = (employee) => {
    setEditingEmployee(employee);
    setShowEmployeeDialog(true);
  };

  const handleDeleteEmployee = async (employee) => {
    if (window.confirm(`Mitarbeiter "${employee.name}" wirklich löschen? Alle Urlaubseinträge werden ebenfalls gelöscht.`)) {
      try {
        await axios.delete(`${API}/employees/${employee.id}`);
        loadData();
      } catch (err) {
        alert('Fehler beim Löschen des Mitarbeiters');
      }
    }
  };

  const handleSaveVacation = () => {
    loadData(); // Reload data after save
  };

  const handleSaveEmployee = () => {
    loadData(); // Reload data after save
  };

  // View handlers
  const handleMonthClick = (month) => {
    setCurrentDate(month);
    setCurrentView('month');
  };

  // Placeholder handlers
  const handleExport = () => {
    alert('Export-Funktion wird implementiert...');
  };

  const handleImport = () => {
    alert('Import-Funktion wird implementiert...');
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDateClick = (date) => {
    console.log('Date clicked:', date);
    // Could open a day view or quick add dialog
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initialisierung...</p>
        </div>
      </div>
    );
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <BrowserRouter>
        <div className="flex flex-col h-screen">
          {/* Toolbar */}
          <Toolbar
            onNewVacation={handleNewVacation}
            onNewEmployee={handleNewEmployee}
            onExport={handleExport}
            onImport={handleImport}
            onPrint={handlePrint}
            currentView={currentView}
            onViewChange={setCurrentView}
            searchTerm={searchTerm}
            onSearchChange={setSearchTerm}
            showFilters={showFilters}
            onToggleFilters={() => setShowFilters(!showFilters)}
            employees={employees}
            settings={settings}
            onLogout={handleLogout}
          />

          {/* Calendar Navigation */}
          <CalendarNavigation
            currentDate={currentDate}
            onPrevious={handlePrevious}
            onNext={handleNext}
            view={currentView}
          />

          {/* Main Content */}
          <div className="flex-1 overflow-hidden">
            {error && (
              <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4 mx-4">
                <div className="flex">
                  <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
                  <p className="text-red-700">{error}</p>
                </div>
              </div>
            )}

            {currentView === 'month' && (
              <MonthCalendarView
                currentDate={currentDate}
                vacationEntries={vacationEntries}
                employees={employees}
                onDateClick={handleDateClick}
                onEntryClick={handleEditVacation}
              />
            )}

            {currentView === 'year' && (
              <YearCalendarView
                currentDate={currentDate}
                vacationEntries={vacationEntries}
                onMonthClick={handleMonthClick}
              />
            )}

            {currentView === 'team' && (
              <div className="bg-white p-6">
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Team-Verwaltung</h2>
                  <p className="text-gray-600">
                    Verwalten Sie Ihre Mitarbeiter und deren Informationen.
                  </p>
                  <div className="mt-2 text-sm text-gray-500">
                    Aktuell: {employees.length} Mitarbeiter • Max. gleichzeitig im Urlaub: {Math.max(1, Math.floor(employees.length * 0.3))} (30%)
                  </div>
                </div>

                {employees.length === 0 ? (
                  <div className="text-center py-12">
                    <Users className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Keine Mitarbeiter vorhanden</h3>
                    <p className="text-gray-500 mb-6">Fügen Sie Ihren ersten Mitarbeiter hinzu, um zu beginnen.</p>
                  </div>
                ) : (
                  <div className="shadow ring-1 ring-black ring-opacity-5 md:rounded-lg overflow-hidden">
                    <div className="team-table-scroll">
                      <table className="min-w-full divide-y divide-gray-300">
                        <thead className="bg-gray-50 sticky top-0 z-10">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide bg-gray-50">
                              Name
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide bg-gray-50">
                              E-Mail
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide bg-gray-50">
                              Rolle
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide bg-gray-50">
                              Urlaubstage
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide bg-gray-50">
                              Skills
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide bg-gray-50">
                              Aktionen
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {employees
                            .sort((a, b) => {
                              // Admins first
                              if (a.role === 'admin' && b.role !== 'admin') return -1;
                              if (b.role === 'admin' && a.role !== 'admin') return 1;
                              return a.name.localeCompare(b.name);
                            })
                            .map((employee) => (
                              <tr key={`employee-${employee.id}-${employee.name}`}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="text-sm font-medium text-gray-900">
                                    {employee.role === 'admin' && '👑 '}
                                    {employee.name}
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="text-sm text-gray-900">{employee.email}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                    employee.role === 'admin' 
                                      ? 'bg-purple-100 text-purple-800' 
                                      : employee.role === 'leiharbeiter'
                                      ? 'bg-orange-100 text-orange-800'
                                      : 'bg-gray-100 text-gray-800'
                                  }`}>
                                    {employee.role === 'admin' ? 'Administrator' : employee.role === 'leiharbeiter' ? 'Leiharbeiter' : 'Mitarbeiter'}
                                  </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {employee.vacation_days_total} Tage
                                </td>
                                <td className="px-6 py-4">
                                  <div className="space-y-1">
                                    {(employee.skills && employee.skills.length > 0) ? (
                                      <>
                                        {employee.skills.slice(0, 3).map((skill, index) => (
                                          <div key={`skill-${index}-${skill.name}`} className="flex items-center space-x-2">
                                            <span className="text-xs text-gray-600">{skill.name}</span>
                                            <StarRating rating={skill.rating} readonly={true} />
                                          </div>
                                        ))}
                                        {employee.skills.length > 3 && (
                                          <div className="text-xs text-gray-400">
                                            +{employee.skills.length - 3} weitere
                                          </div>
                                        )}
                                      </>
                                    ) : (
                                      <span className="text-xs text-gray-400">Keine Skills</span>
                                    )}
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                  <button
                                    onClick={() => handleEditEmployee(employee)}
                                    className="text-blue-600 hover:text-blue-900 mr-3"
                                  >
                                    <Edit2 className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => handleDeleteEmployee(employee)}
                                    className="text-red-600 hover:text-red-900"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                    
                    {/* Scroll Indicator */}
                    {employees.length > 8 && (
                      <div className="bg-gray-50 px-6 py-2 border-t border-gray-200 text-center">
                        <div className="flex justify-between items-center text-xs text-gray-500">
                          <span>
                            Zeige alle {employees.length} Mitarbeiter
                          </span>
                          <div className="flex items-center space-x-2">
                            <span>↕ Scrollbar verfügbar</span>
                            <div className="flex space-x-1">
                              <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse"></div>
                              <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                              <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Vacation Dialog */}
          <VacationDialog
            isOpen={showVacationDialog}
            onClose={() => setShowVacationDialog(false)}
            onSave={handleSaveVacation}
            employees={employees}
            editingEntry={editingEntry}
          />

          {/* Employee Dialog */}
          <EmployeeDialog
            isOpen={showEmployeeDialog}
            onClose={() => setShowEmployeeDialog(false)}
            onSave={handleSaveEmployee}
            editingEmployee={editingEmployee}
          />
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;