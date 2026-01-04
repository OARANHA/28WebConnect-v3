import api from "./api";

export interface Channel {
  id: string;
  name: string;
  type: string;
  description?: string;
  status?: string;
  phoneNumber?: string;
  messagesToday?: number;
  avatarUrl?: string;
}

export interface ChannelQuery {
  page?: number;
  limit?: number;
  status?: string; // connected | disconnected | connecting | awaiting_qr
  type?: string;   // whatsapp | instagram | email | sms
  search?: string;
}

export interface ChannelListResponse {
  data: Channel[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export async function getChannels(params: ChannelQuery = {}): Promise<Channel[]> {
  const { data } = await api.get<ChannelListResponse>("/api/v1/channels", { params });
  return data.data;
}

export async function getChannelsMeta(params: ChannelQuery = {}): Promise<ChannelListResponse> {
  const { data } = await api.get<ChannelListResponse>("/api/v1/channels", { params });
  return data;
}

export async function createChannel(payload: any) {
  const { data } = await api.post("/api/v1/channels", payload);
  return data;
}

export async function connectChannel(instance: string) {
  const { data } = await api.post(`/api/v1/channels/${instance}/connect`);
  return data;
}

export async function getChannelState(instance: string) {
  const { data } = await api.get(`/api/v1/channels/${instance}/state`);
  return data;
}

export async function logoutChannel(instance: string) {
  const { data } = await api.delete(`/api/v1/channels/${instance}/logout`);
  return data;
}

export async function deleteChannel(instance: string) {
  const { data } = await api.delete(`/api/v1/channels/${instance}`);
  return data;
}

export async function linkEvoAiBot(instance: string) {
  const { data } = await api.post(`/api/v1/channels/${instance}/bot`);
  return data;
}
