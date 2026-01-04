/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: /app/dashboard/page.tsx                                                  │
│ Dashboard Page with Metrics and Overview                                            │
└──────────────────────────────────────────────────────────────────────────────┘
*/
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Users,
  MessageSquare,
  TrendingUp,
  Activity,
  Zap,
  MoreHorizontal,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function DashboardPage() {
  const { toast } = useToast();

  const [stats, setStats] = useState({
    totalAgents: 0,
    chatSessions: 0,
    activeContacts: 0,
    activePipelines: 0,
  });

  const [activity, setActivity] = useState<any[]>([]);

  useEffect(() => {
    // Load dashboard data
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Simulate API call - replace with actual API call
      const mockStats = {
        totalAgents: 24,
        chatSessions: 1234,
        activeContacts: 5678,
        activePipelines: 12,
      };

      const mockActivity = [
        { action: "Novo agente criado", time: "Há 2 horas", user: "João Silva" },
        { action: "Pipeline 'Vendas' atualizado", time: "Há 4 horas", user: "Maria Santos" },
        { action: "Canal WhatsApp conectado", time: "Há 6 horas", user: "Pedro Costa" },
        { action: "Campanha 'Promoção' iniciada", time: "Há 1 dia", user: "Ana Rodrigues" },
      ];

      setStats(mockStats);
      setActivity(mockActivity);
    } catch (error) {
      toast({
        title: "Erro ao carregar dashboard",
        description: "Não foi possível carregar os dados do dashboard",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="container mx-auto p-6 min-h-screen bg-[#121212]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight text-white">Dashboard</h1>
        <p className="text-neutral-400 mt-2">Visão geral da plataforma Evo AI</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">
              Total de Agents
            </CardTitle>
            <LayoutDashboard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.totalAgents}</div>
            <p className="text-xs text-neutral-500">+2 em relação ao mês anterior</p>
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">
              Sessões de Chat
            </CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.chatSessions}</div>
            <p className="text-xs text-neutral-500">+18% em relação ao mês anterior</p>
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">
              Contatos Ativos
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.activeContacts}</div>
            <p className="text-xs text-neutral-500">+201 em relação ao mês anterior</p>
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">
              Pipelines Ativos
            </CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.activePipelines}</div>
            <p className="text-xs text-neutral-500">+3 novos pipelines este mês</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid gap-4 md:grid-cols-2 mb-6">
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle>Atividade de Chat</CardTitle>
            <p className="text-sm text-neutral-400">
              Número de sessões de chat nos últimos 7 dias
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center text-neutral-500">
              <div className="text-center">
                <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Gráfico de atividade será renderizado aqui</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle>Crescimento de Contatos</CardTitle>
            <p className="text-sm text-neutral-400">Novos contatos adicionados por mês</p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center text-neutral-500">
              <div className="text-center">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Gráfico de crescimento será renderizado aqui</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="bg-neutral-900 border-neutral-800 mb-6">
        <CardHeader>
          <CardTitle>Atividade Recente</CardTitle>
          <p className="text-sm text-neutral-400">Últimas ações na plataforma</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {activity.map((item, index) => (
              <div key={index} className="flex items-center">
                <div className="h-2 w-2 rounded-full bg-emerald-500 mr-4"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-white">{item.action}</p>
                  <p className="text-xs text-neutral-500">{item.user} - {item.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card className="bg-neutral-900 border-neutral-800">
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
          <p className="text-sm text-neutral-400">Crie novos recursos rapidamente</p>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Button
              variant="outline"
              className="flex flex-col items-center justify-center p-6 h-auto bg-neutral-800 hover:bg-neutral-700 border-neutral-700 text-white"
            >
              <LayoutDashboard className="h-8 w-8 mb-2 text-emerald-500" />
              <span className="font-medium">Criar Agente</span>
            </Button>
            <Button
              variant="outline"
              className="flex flex-col items-center justify-center p-6 h-auto bg-neutral-800 hover:bg-neutral-700 border-neutral-700 text-white"
            >
              <Zap className="h-8 w-8 mb-2 text-blue-500" />
              <span className="font-medium">Criar Pipeline</span>
            </Button>
            <Button
              variant="outline"
              className="flex flex-col items-center justify-center p-6 h-auto bg-neutral-800 hover:bg-neutral-700 border-neutral-700 text-white"
            >
              <MessageSquare className="h-8 w-8 mb-2 text-purple-500" />
              <span className="font-medium">Criar Campanha</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
