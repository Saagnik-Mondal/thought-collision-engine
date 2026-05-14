<![CDATA[import client from './client';
import { ExperimentResult, LeaderboardEntry } from './types';

export const runExperiment = (config: Record<string, unknown>) =>
  client.post<ExperimentResult>('/experiments/run', config).then(r => r.data);

export const fetchExperiments = (skip = 0, limit = 20) =>
  client.get<ExperimentResult[]>('/experiments/', { params: { skip, limit } }).then(r => r.data);

export const fetchLeaderboard = () =>
  client.get<LeaderboardEntry[]>('/experiments/leaderboard').then(r => r.data);
]]>
