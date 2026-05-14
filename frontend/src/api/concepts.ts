<![CDATA[import client from './client';
import { Source } from './types';

export const uploadDocument = (file: File, title: string, sourceType: string) => {
  const form = new FormData();
  form.append('file', file);
  form.append('title', title);
  form.append('source_type', sourceType);
  return client.post<Source>('/ingest/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data);
};

export const ingestUrl = (url: string, title = '') =>
  client.post<Source>('/ingest/url', null, { params: { url, title } }).then(r => r.data);

export const ingestArxiv = (arxivId: string) =>
  client.post<Source>('/ingest/arxiv', null, { params: { arxiv_id: arxivId } }).then(r => r.data);

export const ingestText = (content: string, title = 'Text Input') =>
  client.post<Source>('/ingest/text', null, { params: { content, title } }).then(r => r.data);

export const fetchSources = (skip = 0, limit = 50) =>
  client.get<Source[]>('/ingest/sources', { params: { skip, limit } }).then(r => r.data);
]]>
