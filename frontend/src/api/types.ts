<![CDATA[/* API response types for the Thought Collision Engine */

export interface Source {
  id: string;
  source_type: string;
  title: string;
  url?: string;
  content_preview: string;
  concept_count: number;
  status: string;
  created_at: string;
}

export interface Concept {
  id: string;
  name: string;
  node_type: string;
  domain: string;
  description: string;
  pagerank: number;
  centrality: number;
  community_id?: number;
}

export interface GraphNode {
  id: string;
  name: string;
  node_type: string;
  domain: string;
  val: number;
  color?: string;
  community_id?: number;
  pagerank: number;
}

export interface GraphLink {
  source: string;
  target: string;
  edge_type: string;
  weight: number;
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
  stats: Record<string, number>;
}

export interface Collision {
  id: string;
  concept_a: Concept;
  concept_b: Concept;
  domain_a: string;
  domain_b: string;
  reasoning: string;
  novelty_score: number;
  confidence_score: number;
  semantic_distance: number;
  graph_distance: number;
  bridge_score: number;
  hypotheses: Hypothesis[];
  created_at: string;
}

export interface Hypothesis {
  id: string;
  collision_id: string;
  title: string;
  hypothesis_type: string;
  description: string;
  reasoning_chain: string[];
  potential_applications: string[];
  novelty_score: number;
  confidence_score: number;
  created_at: string;
}

export interface ExperimentConfig {
  name: string;
  description: string;
  algorithms: string[];
  embedding_model: string;
  scoring_weights: Record<string, number>;
  max_collisions: number;
}

export interface ExperimentResult {
  id: string;
  config: ExperimentConfig;
  collisions: Collision[];
  metrics: Record<string, number>;
  duration_seconds: number;
  created_at: string;
}

export interface LeaderboardEntry {
  algorithm: string;
  avg_novelty: number;
  avg_confidence: number;
  total_collisions: number;
  top_collision_score: number;
  experiment_count: number;
}

export interface StatsResponse {
  total_concepts: number;
  total_relationships: number;
  total_sources: number;
  total_collisions: number;
  total_hypotheses: number;
  domains: string[];
}
]]>
