import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import HomePage from './components/HomePage';
import Dashboard from './components/Dashboard';
import { collectTelemetry } from './components/TelemetryCollector';

interface RiskResponse {
  risk_score: number;
  classification: string;
  decision: string;
  confidence: number;
}

interface DashboardData {
  total_requests: number;
  human_count: number;
  bot_count: number;
  suspicious_count: number;
  allowed: number;
  challenged: number;
  blocked: number;
  percentages: any;
}

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [riskResult, setRiskResult] = useState<RiskResponse | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);

  const API_URL = 'https://passiveguard-backend.onrender.com';

  // Fetch dashboard data
  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  };

  // Handle security check
  const handleSecurityCheck = async () => {
    setLoading(true);
    try {
      // Collect telemetry
      const telemetry = collectTelemetry();
      
      // Send to backend
      const response = await axios.post(`${API_URL}/api/risk/evaluate`, telemetry);
      setRiskResult(response.data);
      
      // Refresh dashboard
      await fetchDashboard();
    } catch (error) {
      console.error('Error:', error);
      alert('Error connecting to backend. Make sure it\'s running on port 8000');
    } finally {
      setLoading(false);
    }
  };

  // Simulate different user types
  const simulateUser = async (type: 'human' | 'bot' | 'suspicious') => {
    setLoading(true);
    try {
      let telemetry;
      
      if (type === 'human') {
        telemetry = {
          interaction_duration: 15.5,
          mouse_count: 125,
          mouse_speed_mean: 1.8,
          mouse_speed_variance: 0.9,
          click_count: 7,
          click_interval_variance: 1.2,
          scroll_count: 5,
          keyboard_count: 3,
          request_frequency: 1.2,
          webdriver_flag: 0,
          touch_support: 0,
          viewport_width: 1024,
          viewport_height: 768,
          timezone_offset: -330,
          hardware_concurrency: 8,
        };
      } else if (type === 'bot') {
        telemetry = {
          interaction_duration: 0.5,
          mouse_count: 15,
          mouse_speed_mean: 12.0,
          mouse_speed_variance: 0.05,
          click_count: 2,
          click_interval_variance: 0.02,
          scroll_count: 0,
          keyboard_count: 0,
          request_frequency: 100.0,
          webdriver_flag: 1,
          touch_support: 0,
          viewport_width: 1024,
          viewport_height: 768,
          timezone_offset: -330,
          hardware_concurrency: 8,
        };
      } else {
        telemetry = {
          interaction_duration: 3.5,
          mouse_count: 50,
          mouse_speed_mean: 4.5,
          mouse_speed_variance: 0.4,
          click_count: 4,
          click_interval_variance: 0.5,
          scroll_count: 2,
          keyboard_count: 1,
          request_frequency: 8.0,
          webdriver_flag: 0,
          touch_support: 1,
          viewport_width: 1024,
          viewport_height: 768,
          timezone_offset: -330,
          hardware_concurrency: 8,
        };
      }

      const response = await axios.post(`${API_URL}/api/risk/evaluate`, telemetry);
      setRiskResult(response.data);
      await fetchDashboard();
    } catch (error) {
      console.error('Error:', error);
      alert('Error connecting to backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <nav className="navbar">
        <div className="navbar-content">
          <h1>🛡️ PassiveGuard</h1>
          <div className="nav-buttons">
            <button 
              className={currentPage === 'home' ? 'active' : ''} 
              onClick={() => setCurrentPage('home')}
            >
              Home
            </button>
            <button 
              className={currentPage === 'dashboard' ? 'active' : ''} 
              onClick={() => setCurrentPage('dashboard')}
            >
              Dashboard
            </button>
            <button 
              className={currentPage === 'privacy' ? 'active' : ''} 
              onClick={() => setCurrentPage('privacy')}
            >
              Privacy
            </button>
          </div>
        </div>
      </nav>

      <div className="content">
        {currentPage === 'home' && (
          <HomePage 
            riskResult={riskResult} 
            onSecurityCheck={handleSecurityCheck}
            onSimulate={simulateUser}
            loading={loading}
          />
        )}
        {currentPage === 'dashboard' && (
          <Dashboard data={dashboardData} />
        )}
        {currentPage === 'privacy' && (
          <div className="privacy-page">
            <h2>Privacy & Security</h2>
            <div className="privacy-content">
              <h3>What We Collect:</h3>
              <ul>
                <li>✅ Mouse movement statistics (speed, variance)</li>
                <li>✅ Click patterns and timing</li>
                <li>✅ Scroll behavior</li>
                <li>✅ Keyboard event count</li>
                <li>✅ Browser info (timezone, language, device)</li>
              </ul>
              
              <h3>What We DO NOT Collect:</h3>
              <ul>
                <li>❌ Aadhaar number or personal documents</li>
                <li>❌ Passwords or sensitive data</li>
                <li>❌ Raw keystroke logs</li>
                <li>❌ Camera or microphone access</li>
                <li>❌ Location data</li>
                <li>❌ Fingerprinting data</li>
              </ul>

              <h3>Privacy by Design:</h3>
              <p>
                PassiveGuard collects ONLY derived statistical features, never raw personal data.
                Your privacy is protected by design, not by policy.
              </p>

              <h3>Synthetic Data:</h3>
              <p>
                This prototype uses synthetic (fake but realistic) training data. 
                No real user data is collected or analyzed.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;