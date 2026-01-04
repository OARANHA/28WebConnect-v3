"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Radio,
  Plus,
  MoreHorizontal,
  CheckCircle,
  AlertCircle,
  MessageCircle,
  Mail,
  Send,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function ChannelsPage() {
  const { toast } = useToast();

  // data
  const [channels, setChannels] = useState<any[]>([]);
  const [avatarMap, setAvatarMap] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  // filters & pagination
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [page, setPage] = useState<number>(1);
  const [limit, setLimit] = useState<number>(20);
  const [total, setTotal] = useState<number>(0);
  const [hasMore, setHasMore] = useState<boolean>(false);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  // create dialog
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [instanceName, setInstanceName] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  // delete confirm dialog
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const [pendingDeleteStatus, setPendingDeleteStatus] = useState<string | null>(null);

  // qr modal
  const [isQROpen, setIsQROpen] = useState(false);
  const [qrImage, setQrImage] = useState<string | null>(null);
  const [qrText, setQrText] = useState<string | null>(null);
  const [pairingCode, setPairingCode] = useState<string | null>(null);
  const [refText, setRefText] = useState<string | null>(null);
  const [currentInstance, setCurrentInstance] = useState<string | null>(null);
  const [statusText, setStatusText] = useState<string>("Aguardando leitura do QR...");
  const [isLinkingBot, setIsLinkingBot] = useState(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    loadChannels();
    return () => stopPolling();
  }, []);

  // re-fetch on filters/pagination change (debounced for search)
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      loadChannels();
    }, 500);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, statusFilter, typeFilter, page, limit]);

  const loadChannels = async () => {
    setIsLoading(true);
    try {
      const { getChannelsMeta } = await import("@/services/channelService");
      const meta = await getChannelsMeta({
        page,
        limit,
        status: statusFilter || undefined,
        type: typeFilter || undefined,
        search: search || undefined,
      });
      const arr = Array.isArray(meta?.data) ? meta.data : [];
      setChannels(arr);
      setTotal(meta?.total || 0);
      setHasMore(Boolean(meta?.hasMore));
      const map: Record<string, string> = {};
      for (const c of arr) {
        if (c?.id && c?.avatarUrl) map[c.id] = c.avatarUrl;
      }
      setAvatarMap(map);
    } catch (error: any) {
      if (error?.response?.status && error.response.status >= 500) {
        toast({ title: "Falha no servidor ao carregar canais", variant: "destructive" });
      } else {
        setChannels([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getChannelIcon = (type: string) => {
    switch (type) {
      case "whatsapp":
        return <MessageCircle className="h-5 w-5 text-emerald-500" />;
      case "instagram":
        return <MessageCircle className="h-5 w-5 text-pink-500" />;
      case "email":
        return <Mail className="h-5 w-5 text-blue-500" />;
      case "sms":
        return <Send className="h-5 w-5 text-purple-500" />;
      default:
        return <Radio className="h-5 w-5 text-neutral-500" />;
    }
  };

  const startPolling = (instance: string) => {
    stopPolling();
    pollingRef.current = setInterval(async () => {
      try {
        const { getChannelState, linkEvoAiBot } = await import("@/services/channelService");
        const state = await getChannelState(instance);
        const s = (state?.status || state?.state || state?.message || "").toString().toLowerCase();
        if (s) setStatusText(s);
        const qrCandidate = state?.qrcode || state?.qr || state?.base64 || state?.image || null;
        const pairingCandidate = state?.pairingCode || state?.pairing_code || null;
        const refCandidate = state?.ref || state?.reference || null;
        if (pairingCandidate && typeof pairingCandidate === "string") setPairingCode(pairingCandidate);
        if (refCandidate && typeof refCandidate === "string") setRefText(refCandidate);
        if (qrCandidate && typeof qrCandidate === "string") {
          const isDataUrl = qrCandidate.startsWith("data:image");
          const img = isDataUrl ? qrCandidate : `data:image/png;base64,${qrCandidate}`;
          setQrImage(img);
        }
        if (s.includes("connected")) {
          try {
            await linkEvoAiBot(instance);
            toast({ title: `Instância ${instance} conectada e bot EvoAI vinculado!` });
          } catch {
            toast({ title: `Instância ${instance} conectada (falha ao vincular bot)`, variant: "destructive" });
          }
          await loadChannels();
          setIsQROpen(false);
          stopPolling();
        }
      } catch {
        // ignore
      }
    }, 2000);
  };

  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  const handleConnect = async (id: string) => {
    try {
      const { connectChannel, getChannelState } = await import("@/services/channelService");
      const resp = await connectChannel(String(id));
      setCurrentInstance(String(id));

      const qrCandidate = resp?.qrcode || resp?.qr || resp?.base64 || resp?.image || null;
      const pairingCandidate = resp?.pairingCode || resp?.pairing_code || null;
      const textCandidate = resp?.ref || resp?.reference || resp?.message || null;
      setQrText(textCandidate);
      if (pairingCandidate && typeof pairingCandidate === "string") setPairingCode(pairingCandidate);
      if (qrCandidate && typeof qrCandidate === "string") {
        const isDataUrl = qrCandidate.startsWith("data:image");
        const img = isDataUrl ? qrCandidate : `data:image/png;base64,${qrCandidate}`;
        setQrImage(img);
      } else {
        try {
          const st = await getChannelState(String(id));
          const q2 = st?.qrcode || st?.qr || st?.base64 || st?.image || null;
          if (q2 && typeof q2 === "string") {
            const isDataUrl2 = q2.startsWith("data:image");
            const img2 = isDataUrl2 ? q2 : `data:image/png;base64,${q2}`;
            setQrImage(img2);
          }
        } catch {}
      }

      setIsQROpen(true);
      startPolling(String(id));
      toast({ title: `Conexão iniciada para ${id}` });
    } catch {
      toast({ title: "Falha ao conectar canal", variant: "destructive" });
    }
  };

  const handleLogout = async (id: string) => {
    try {
      const { logoutChannel } = await import("@/services/channelService");
      await logoutChannel(String(id));
      toast({ title: `Logout solicitado em ${id}` });
      await loadChannels();
    } catch {
      toast({ title: "Falha ao desconectar canal", variant: "destructive" });
    }
  };

  const handleDelete = async (id: string) => {
    // Optimistic UI update
    setChannels((prev) => prev.filter((c) => String(c.id) !== String(id)));
    setAvatarMap((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
    setTotal((t) => Math.max(0, t - 1));
    try {
      const { deleteChannel } = await import("@/services/channelService");
      await deleteChannel(id);
      toast({ title: `Canal ${id} excluído` });
      // Sync with backend to reflect server truth (e.g., counts)
      await loadChannels();
    } catch {
      toast({ title: `Falha ao excluir ${id}`, variant: "destructive" });
      // Fallback: reload from server to restore original state
      await loadChannels();
    }
  };

  const handleCreate = async () => {
    if (!instanceName?.trim()) {
      toast({ title: "Informe o nome da instância", variant: "destructive" });
      return;
    }
    setIsCreating(true);
    try {
      const { createChannel } = await import("@/services/channelService");
      await createChannel({ instanceName });
      toast({ title: "Instância criada com sucesso" });
      setIsCreateOpen(false);
      setInstanceName("");
      await loadChannels();
    } catch {
      toast({ title: "Falha ao criar instância", variant: "destructive" });
    } finally {
      setIsCreating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 min-h-screen bg-[#121212]">
        <div className="text-white">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 min-h-screen bg-[#121212]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight text-white">Canais</h1>
          <p className="text-neutral-400 mt-2">Gerencie seus canais de comunicação</p>
        </div>
        {/* Filters */}
        <div className="flex items-end gap-2 flex-wrap justify-end">
          <div className="w-56">
            <Label className="text-neutral-300">Buscar</Label>
            <Input
              placeholder="Buscar por nome, número, descrição"
              value={search}
              onChange={(e) => { setPage(1); setSearch(e.target.value); }}
              className="bg-neutral-900 border-neutral-700 text-white"
            />
          </div>
          <div>
            <Label className="text-neutral-300">Status</Label>
            <select
              className="h-10 px-3 rounded-md bg-neutral-900 border border-neutral-700 text-white"
              value={statusFilter}
              onChange={(e) => { setPage(1); setStatusFilter(e.target.value); }}
            >
              <option value="">Todos</option>
              <option value="connected">Conectado</option>
              <option value="disconnected">Desconectado</option>
              <option value="connecting">Conectando</option>
              <option value="awaiting_qr">Aguardando QR</option>
            </select>
          </div>
          <div>
            <Label className="text-neutral-300">Tipo</Label>
            <select
              className="h-10 px-3 rounded-md bg-neutral-900 border border-neutral-700 text-white"
              value={typeFilter}
              onChange={(e) => { setPage(1); setTypeFilter(e.target.value); }}
            >
              <option value="">Todos</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="instagram">Instagram</option>
              <option value="email">Email</option>
              <option value="sms">SMS</option>
            </select>
          </div>
          <div>
            <Label className="text-neutral-300">Por página</Label>
            <select
              className="h-10 px-3 rounded-md bg-neutral-900 border border-neutral-700 text-white"
              value={limit}
              onChange={(e) => { setPage(1); setLimit(Number(e.target.value)); }}
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Adicionar Canal
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-neutral-950 text-white border-neutral-800">
              <DialogHeader>
                <DialogTitle>Novo Canal (Instância WhatsApp)</DialogTitle>
                <DialogDescription>
                  Crie uma nova instância na Evolution-API. Use um nome único.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-3">
                <div className="grid gap-2">
                  <Label htmlFor="instanceName">Nome da Instância</Label>
                  <Input
                    id="instanceName"
                    placeholder="ex.: tenant-xyz-wa-01"
                    value={instanceName}
                    onChange={(e) => setInstanceName(e.target.value)}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setIsCreateOpen(false)} className="bg-neutral-900 border-neutral-700">Cancelar</Button>
                <Button onClick={handleCreate} disabled={isCreating}>
                  {isCreating ? "Criando..." : "Criar"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Toolbar bottom: pagination */}
      <div className="flex items-center justify-between mb-4">
        <div className="text-sm text-neutral-400">
          Página {page} de {Math.max(1, Math.ceil(total / Math.max(1, limit)))} • Total: {total}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="bg-neutral-900 border-neutral-700" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Anterior</Button>
          <Button variant="outline" className="bg-neutral-900 border-neutral-700" disabled={!hasMore} onClick={() => setPage((p) => p + 1)}>Próximo</Button>
        </div>
      </div>

      {/* Channels Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {channels.map((channel) => (
          <Card key={channel.id} className="bg-neutral-900 border-neutral-800 hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="flex items-center gap-2 text-white">
                    {avatarMap[channel.id] ? (
                      <img src={avatarMap[channel.id]} alt="avatar" className="h-6 w-6 rounded-full" />
                    ) : (
                      getChannelIcon(channel.type)
                    )}
                    {channel.name}
                  </CardTitle>
                  <p className="text-sm text-neutral-400">{channel.description}</p>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="text-white hover:bg-neutral-800">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-neutral-900 text-white border-neutral-800">
                    <DropdownMenuItem
                      className="cursor-pointer focus:bg-neutral-800"
                      onClick={() => {
                        setPendingDeleteId(String(channel.id));
                        setPendingDeleteStatus(String(channel.status || ""));
                        setIsDeleteOpen(true);
                      }}
                    >
                      Excluir canal
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Status Badge */}
                <div className="flex items-center gap-2">
                  {String(channel.status).toLowerCase() === "connected" ? (
                    <>
                      <CheckCircle className="h-4 w-4 text-emerald-500" />
                      <span className="text-sm text-emerald-600 font-medium">Conectado</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="h-4 w-4 text-yellow-500" />
                      <span className="text-sm text-yellow-600 font-medium">Desconectado</span>
                    </>
                  )}
                </div>

                {/* Channel Info */}
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-neutral-400">Identificador:</span>
                    <span className="font-medium text-white">{channel.phoneNumber || "-"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-neutral-400">Mensagens hoje:</span>
                    <span className="font-medium text-white">{channel.messagesToday ?? 0}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {String(channel.status).toLowerCase() === "connected" ? (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700"
                        onClick={async () => {
                          try {
                            setIsLinkingBot(true);
                            const { linkEvoAiBot } = await import("@/services/channelService");
                            await linkEvoAiBot(String(channel.id));
                            toast({ title: `Bot vinculado a ${channel.id}` });
                          } catch {
                            toast({ title: `Falha ao vincular bot em ${channel.id}`, variant: "destructive" });
                          } finally {
                            setIsLinkingBot(false);
                          }
                        }}
                      >
                        {isLinkingBot ? "Vinculando..." : "Vincular Bot"}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        className="flex-1"
                        onClick={() => handleLogout(String(channel.id))}
                      >
                        Desconectar
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        className="flex-1"
                        onClick={async () => {
                          try {
                            const { deleteChannel } = await import("@/services/channelService");
                            await deleteChannel(String(channel.id));
                            toast({ title: `Canal ${channel.id} excluído` });
                            await loadChannels();
                          } catch {
                            toast({ title: `Falha ao excluir ${channel.id}`, variant: "destructive" });
                          }
                        }}
                      >
                        Excluir
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button size="sm" className="flex-1 gap-2" onClick={() => handleConnect(String(channel.id))}>
                        <Plus className="h-3 w-3" />
                        Conectar
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        className="flex-1"
                        onClick={async () => {
                          try {
                            const { deleteChannel } = await import("@/services/channelService");
                            await deleteChannel(String(channel.id));
                            toast({ title: `Canal ${channel.id} excluído` });
                            await loadChannels();
                          } catch {
                            toast({ title: `Falha ao excluir ${channel.id}`, variant: "destructive" });
                          }
                        }}
                      >
                        Excluir
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Add New Channel Card (secondary entry) */}
        <Card className="border-dashed border-neutral-700 hover:border-emerald-500/50 transition-colors cursor-pointer bg-neutral-900/50" onClick={() => setIsCreateOpen(true)}>
          <CardContent className="flex flex-col items-center justify-center h-full min-h-[280px]">
            <div className="p-4 rounded-full bg-neutral-800 mb-4">
              <Plus className="h-8 w-8 text-neutral-400" />
            </div>
            <p className="font-medium text-white">Adicionar novo canal</p>
            <p className="text-sm text-neutral-500 text-center mt-1">Conecte novos canais de comunicação</p>
          </CardContent>
        </Card>
      </div>

      {/* Delete Confirm Modal */}
      <Dialog open={isDeleteOpen} onOpenChange={setIsDeleteOpen}>
        <DialogContent className="bg-neutral-950 text-white border-neutral-800">
          <DialogHeader>
            <DialogTitle>Confirmar exclusão</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja excluir o canal {pendingDeleteId}? Esta ação não pode ser desfeita.
              {String(pendingDeleteStatus).toLowerCase() === "connected" && (
                <>
                  <br />
                  <span className="text-red-400">Atenção:</span> este canal está <span className="font-semibold">conectado</span>. A exclusão irá desconectá-lo imediatamente e remover a instância no Evolution-API.
                </>
              )}
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2">
            <Button variant="outline" className="bg-neutral-900 border-neutral-700" onClick={() => setIsDeleteOpen(false)}>
              Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={async () => {
                if (!pendingDeleteId) return;
                try {
                  const { deleteChannel } = await import("@/services/channelService");
                  await deleteChannel(pendingDeleteId);
                  toast({ title: `Canal ${pendingDeleteId} excluído` });
                  setIsDeleteOpen(false);
                  setPendingDeleteId(null);
                  await handleDelete(pendingDeleteId);
                } catch {
                  toast({ title: `Falha ao excluir ${pendingDeleteId}`, variant: "destructive" });
                }
              }}
            >
              Excluir
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* QR Modal */}
      <Dialog
        open={isQROpen}
        onOpenChange={(open) => {
          setIsQROpen(open);
          if (!open) {
            stopPolling();
          }
        }}
      >
        <DialogContent className="bg-neutral-950 text-white border-neutral-800">
          <DialogHeader>
            <DialogTitle>Escanear o QR Code</DialogTitle>
            <DialogDescription>
              Abra o WhatsApp no seu celular e escaneie o QR para conectar a instância {currentInstance}.
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col items-center gap-4">
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="bg-neutral-900 border-neutral-700" onClick={() => currentInstance && handleConnect(currentInstance)}>
                Regerar QR
              </Button>
              {currentInstance && (
                <Button
                  variant="outline"
                  size="sm"
                  className="bg-neutral-900 border-neutral-700"
                  onClick={async () => {
                    try {
                      setIsLinkingBot(true);
                      const { linkEvoAiBot } = await import("@/services/channelService");
                      await linkEvoAiBot(currentInstance);
                      toast({ title: `Bot vinculado a ${currentInstance}` });
                    } catch {
                      toast({ title: `Falha ao vincular bot em ${currentInstance}` , variant: "destructive" });
                    } finally {
                      setIsLinkingBot(false);
                    }
                  }}
                >
                  {isLinkingBot ? "Vinculando..." : "Vincular Bot"}
                </Button>
              )}
            </div>
            {qrImage ? (
              <img src={qrImage} alt="QR Code" className="rounded bg-white p-2" />
            ) : (
              <div className="text-neutral-400 text-sm">Aguardando QR Code...</div>
            )}
            {qrText && (
              <div className="text-xs text-neutral-400 break-all">{qrText}</div>
            )}
            <div className="w-full space-y-2">
              {pairingCode && (
                <div className="text-xs text-neutral-300">
                  Pairing code: <span className="font-mono">{pairingCode}</span>
                </div>
              )}
              {refText && (
                <div className="text-xs text-neutral-500 break-all">
                  Ref: <span className="font-mono">{refText}</span>
                </div>
              )}
              <div className="text-xs text-neutral-500">
                {statusText || "A janela se fechará automaticamente quando a conexão for estabelecida."}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
