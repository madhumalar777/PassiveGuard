interface DashboardProps {
  data: any;
}

export default function Dashboard({ data }: DashboardProps) {
  if (!data) {
    return <div className="dashboard"><p>Loading...</p></div>;
  }

  return (
    <div className="dashboard">
      <h2>📊 Security Dashboard</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{data.total_requests}</div>
          <div className="stat-label">Total Requests</div>
        </div>
        
        <div className="stat-card human">
          <div className="stat-number">{data.human_count}</div>
          <div className="stat-label">✅ Humans ({data.percentages?.human || 0}%)</div>
        </div>
        
        <div className="stat-card suspicious">
          <div className="stat-number">{data.suspicious_count}</div>
          <div className="stat-label">⚠️ Suspicious ({data.percentages?.suspicious || 0}%)</div>
        </div>
        
        <div className="stat-card bot">
          <div className="stat-number">{data.bot_count}</div>
          <div className="stat-label">❌ Bots ({data.percentages?.bot || 0}%)</div>
        </div>
      </div>

      <div className="actions-grid">
        <div className="action-card">
          <div className="action-number">{data.allowed}</div>
          <div className="action-label">Allowed</div>
          <div className="action-percent">{data.percentages?.allowed || 0}%</div>
        </div>
        
        <div className="action-card">
          <div className="action-number">{data.challenged}</div>
          <div className="action-label">Challenged</div>
          <div className="action-percent">{data.percentages?.challenged || 0}%</div>
        </div>
        
        <div className="action-card">
          <div className="action-number">{data.blocked}</div>
          <div className="action-label">Blocked</div>
          <div className="action-percent">{data.percentages?.blocked || 0}%</div>
        </div>
      </div>

      <div className="info-box">
        <h3>📈 Real-Time Monitoring</h3>
        <p>Dashboard updates every 5 seconds to show live threat detection metrics.</p>
      </div>
    </div>
  );
}