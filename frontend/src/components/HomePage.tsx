import type { RiskResponse } from '../types';

interface HomePageProps {
  riskResult: RiskResponse | null;
  onSecurityCheck: () => void;
  onSimulate: (type: 'human' | 'bot' | 'suspicious') => void;
  loading: boolean;
}

export default function HomePage({ riskResult, onSecurityCheck, onSimulate, loading }: HomePageProps) {
  const getRiskColor = (score: number) => {
  if (score < 0.3) return '#29e0b0'; // signal teal
  if (score < 0.7) return '#ffb84d'; // warning amber
  return '#ff5d5d'; // danger red
};

  const getRiskEmoji = (classification: string) => {
    switch (classification) {
      case 'human': return '✅';
      case 'suspicious': return '⚠️';
      case 'bot': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="home-page">
      <div className="hero">
        <h2>Privacy-Preserving Bot Detection</h2>
        <p>No CAPTCHA. No friction. Just intelligent security.</p>
      </div>

      <div className="check-section">
        <button 
          className="check-button" 
          onClick={onSecurityCheck}
          disabled={loading}
        >
          {loading ? '⏳ Analyzing...' : '🔍 Check My Security'}
        </button>
      </div>

      {riskResult && (
        <div className="result-card">
          <div className="result-header">
            <h3>{getRiskEmoji(riskResult.classification)} {riskResult.classification.toUpperCase()}</h3>
            <p className="risk-label">{riskResult.decision.toUpperCase()}</p>
          </div>
          
          <div className="risk-score">
            <div className="score-visual">
              <div 
                className="score-bar"
                style={{
                  width: `${riskResult.risk_score * 100}%`,
                  backgroundColor: getRiskColor(riskResult.risk_score)
                }}
              ></div>
            </div>
            <p className="score-text">
              Risk Score: {(riskResult.risk_score * 100).toFixed(1)}%
            </p>
            <p className="confidence-text">
              Confidence: {(riskResult.confidence * 100).toFixed(1)}%
            </p>
          </div>

          <div className="decision-text">
            {riskResult.decision === 'allow' && (
              <p className="success">✅ Access Granted - You are authorized</p>
            )}
            {riskResult.decision === 'challenge' && (
              <p className="warning">⚠️ Please verify your identity</p>
            )}
            {riskResult.decision === 'block' && (
              <p className="error">❌ Access Denied - Suspected bot activity</p>
            )}
          </div>

          {riskResult.top_reasons && riskResult.top_reasons.length > 0 && (
            <div className="reasons-box">
              <h4>🔎 Why this decision?</h4>
              <ul>
                {riskResult.top_reasons.map((reason, idx) => (
                  <li key={idx}>
                    <strong>{reason.description}</strong>
                    <span className="reason-meta">
                      {' '}(value: {reason.value}, influence: {(reason.importance * 100).toFixed(1)}%)
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="demo-section">
        <h3>🎬 Demo Simulations</h3>
        <div className="demo-buttons">
          <button 
            className="demo-btn human"
            onClick={() => onSimulate('human')}
            disabled={loading}
          >
            👤 Simulate Normal User
          </button>
          <button 
            className="demo-btn suspicious"
            onClick={() => onSimulate('suspicious')}
            disabled={loading}
          >
            🤔 Simulate Suspicious
          </button>
          <button 
            className="demo-btn bot"
            onClick={() => onSimulate('bot')}
            disabled={loading}
          >
            🤖 Simulate Bot Attack
          </button>
        </div>
      </div>
    </div>
  );
}