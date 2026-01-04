/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: /app/campaigns/page.tsx                                                 │
│ Campaigns Page - Mass Messaging                                                  │
└──────────────────────────────────────────────────────────────────────────────┘
*/
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Megaphone, Plus, MoreHorizontal, Play, Pause, Send, Clock, CheckCircle, Users } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function CampaignsPage() {
  const { toast } = useToast();
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      const mockCampaigns = [
        {
          id: 1,
          name: "Promoção de Natal",
          description: "Campanha de promoções de fim de ano",
          status: "running",
          type: "whatsapp",
          recipients: 1250,
          sent: 875,
          delivered: 820,
          opened: 645,
          scheduled: "2025-01-15 10:00",
        },
        {
          id: 2,
          name: "Lançamento de Produto",
          description: "Anúncio do novo produto premium",
          status: "scheduled",
          type: "email",
          recipients: 3400,
          sent: 0,
          delivered: 0,
          opened: 0,
          scheduled: "2025-01-20 09:00",
        },
      ];

      setCampaigns(mockCampaigns);
    } catch (error) {
      toast({
        title: "Erro ao carregar campanhas",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "running":
        return (
          <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-emerald-100 text-emerald-700">
            <Play className="h-3 w-3" />
            Em andamento
          </span>
        );
      case "scheduled":
        return (
          <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-700">
            <Clock className="h-3 w-3" />
            Agendada
          </span>
        );
      case "completed":
        return (
          <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-neutral-100 text-neutral-700">
            <CheckCircle className="h-3 w-3" />
            Concluída
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-700">
            <Pause className="h-3 w-3" />
            Pausada
          </span>
        );
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
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Campanhas
          </h1>
          <p className="text-neutral-400 mt-2">
            Crie e gerencie campanhas de envio em massa
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Nova Campanha
        </Button>
      </div>

      {/* Campaigns Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {campaigns.map((campaign) => (
          <Card
            key={campaign.id}
            className="bg-neutral-900 border-neutral-800 hover:shadow-lg transition-shadow"
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="flex items-center gap-2 text-white">
                    <Megaphone className="h-5 w-5 text-purple-500" />
                    {campaign.name}
                  </CardTitle>
                  <p className="text-sm text-neutral-400">{campaign.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(campaign.status)}
                  <Button variant="ghost" size="icon" className="text-white hover:bg-neutral-800">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Channel Type */}
                <div className="flex items-center gap-2 text-sm">
                  <Send className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium text-white capitalize">
                    {campaign.type === "whatsapp" ? "WhatsApp" : "Email"}
                  </span>
                </div>

                {/* Recipients */}
                <div className="flex items-center gap-2 text-sm text-neutral-400">
                  <Users className="h-4 w-4" />
                  <span className="text-white">{campaign.recipients} destinatários</span>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="text-center p-2 rounded bg-neutral-800">
                    <div className="text-neutral-400 text-xs">Enviados</div>
                    <div className="font-bold text-white">{campaign.sent}</div>
                  </div>
                  <div className="text-center p-2 rounded bg-neutral-800">
                    <div className="text-neutral-400 text-xs">Entregues</div>
                    <div className="font-bold text-white">{campaign.delivered}</div>
                  </div>
                  <div className="text-center p-2 rounded bg-neutral-800">
                    <div className="text-neutral-400 text-xs">Abertos</div>
                    <div className="font-bold text-white">{campaign.opened}</div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {campaign.status === "running" ? (
                    <Button
                      variant="destructive"
                      size="sm"
                      className="flex-1 gap-2"
                    >
                      <Pause className="h-3 w-3" />
                      Pausar
                    </Button>
                  ) : campaign.status === "scheduled" ? (
                    <Button size="sm" className="flex-1 gap-2">
                      <Play className="h-3 w-3" />
                      Iniciar Agora
                    </Button>
                  ) : (
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1 gap-2"
                    >
                      <Megaphone className="h-3 w-3" />
                      Duplicar
                    </Button>
                  )}
                  <Button variant="outline" size="sm">
                    Ver Detalhes
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Add New Campaign Card */}
        <Card className="border-dashed border-neutral-700 hover:border-emerald-500/50 transition-colors cursor-pointer bg-neutral-900/50">
          <CardContent className="flex flex-col items-center justify-center h-full min-h-[350px]">
            <div className="p-4 rounded-full bg-neutral-800 mb-4">
              <Plus className="h-8 w-8 text-neutral-400" />
            </div>
            <p className="font-medium text-white">Criar nova campanha</p>
            <p className="text-sm text-neutral-500 text-center mt-1">
              Envie mensagens em massa para múltiplos contatos
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
