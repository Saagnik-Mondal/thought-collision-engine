<![CDATA[import client from './client';
import { Collision } from './types';

export const discoverCollisions = (params = {}) =>
  client.post<Collision[]>('/collisions/discover', {
    min_novelty: 50, max_results: 20, algorithm: 'composite', ...params,
  }).then(r => r.data);

export const fetchCollisions = (skip = 0, limit = 20) =>
  client.get<Collision[]>('/collisions/', { params: { skip, limit } }).then(r => r.data);

export const fetchCollisionStats = () =>
  client.get('/collisions/stats').then(r => r.data);
]]>
