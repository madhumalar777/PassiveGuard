export interface Reason {
  feature: string;
  value: number;
  importance: number;
  description: string;
}

export interface RiskResponse {
  risk_score: number;
  classification: string;
  decision: string;
  confidence: number;
  top_reasons: Reason[];
}