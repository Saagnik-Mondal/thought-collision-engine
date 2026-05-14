<![CDATA[import client from './client';
import { GraphData } from './types';

export const fetchGraphData = (limit = 300) =>
  client.get<GraphData>('/graph/data', { params: { limit } }).then(r => r.data);

export const fetchNeighbors = (nodeId: string, depth = 1) =>
  client.get(`/graph/neighbors/${nodeId}`, { params: { depth } }).then(r => r.data);

export const fetchShortestPath = (sourceId: string, targetId: string) =>
  client.get('/graph/path', { params: { source_id: sourceId, target_id: targetId } }).then(r => r.data);

export const fetchGraphStats = () =>
  client.get('/graph/stats').then(r => r.data);
]]>
