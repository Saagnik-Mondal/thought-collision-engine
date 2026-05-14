<![CDATA[import client from './client';
import { Hypothesis } from './types';

export const generateHypotheses = (collisionId: string, count = 3) =>
  client.post<Hypothesis[]>(`/hypotheses/generate/${collisionId}`, null, {
    params: { count },
  }).then(r => r.data);

export const fetchHypotheses = (skip = 0, limit = 20) =>
  client.get<Hypothesis[]>('/hypotheses/', { params: { skip, limit } }).then(r => r.data);
]]>
