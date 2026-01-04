/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: /app/pipelines/page.tsx                                                  │
│ Pipelines Page - Workflow Management                                                │
└──────────────────────────────────────────────────────────────────────────────┘
*/
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { GitMerge, Plus, Play, MoreHorizontal, Clock, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function PipelinesPage() {
  const { toast } = useToast();

  const [pipelines, setPipelines] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadPipelines();
  }, []);

  const loadPipelines = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      const mockPipelines = [
        {
          id: 1,
          name: "Pipeline de Vendas",
          description: "Fluxo de atendimento automatizado para vendas",
          status: "active",
          lastRun: "Há 2 horas",
          executions: 156,
        },
        {
          id: 2,
          name: "Suporte Técnico",
          description: "Triagem automática de tickets de suporte",
          status: "active",
          lastRun: "Há 30 minutos",
          executions: 423,
        },
        {
          id: 3,
          name: "Onboarding de Novos Clients",
          description: "Sequência de boas-vindas automatizada",
          status: "paused",
          lastRun: "Há 1 dia",
          executions: 89,
        },
      ];

      setPipelines(mockPipelines);
    } catch (error) {
      toast({
        title: "Erro ao carregar pipelines",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
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
          <h1 className="text-3xl font-bold tracking-tight text-white">Pipelines</h1>
          <p className="text-neutral-400 mt-2">
            Gerencie seus workflows de automação
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Novo Pipeline
        </Button>
      </div>

      {/* Pipelines Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {pipelines.map((pipeline) => (
          <Card key={pipeline.id} className="bg-neutral-900 border-neutral-800 hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="flex items-center gap-2 text-white">
                    <GitMerge className="h-5 w-5 text-blue-500" />
                    {pipeline.name}
                  </CardTitle>
                  <p className="text-sm text-neutral-400">{pipeline.description}</p>
                </div>
                <Button variant="ghost" size="icon" className="text-white hover:bg-neutral-800">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Status Badge */}
                <div className="flex items-center gap-2">
                  <div
                    className={`h-2 w-2 rounded-full ${
                      pipeline.status === "active"
                        ? "bg-emerald-500"
                        : "bg-yellow-500"
                    }`}
                  ></div>
                  <span className="text-sm text-neutral-400">
                    {pipeline.status === "active" ? "Ativo" : "Pausado"}
                  </span>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-neutral-400 flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      Última execução
                    </div>
                    <div className="font-medium text-white">{pipeline.lastRun}</div>
                  </div>
                  <div>
                    <div className="text-neutral-400 flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" />
                      Execuções
                    </div>
                    <div className="font-medium text-white">{pipeline.executions}</div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1 bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700">
                    Editar
                  </Button>
                  <Button size="sm" className="flex-1 gap-2">
                    <Play className="h-3 w-3" />
                    Executar
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Add New Pipeline Card */}
        <Card className="border-dashed border-neutral-700 hover:border-emerald-500/50 transition-colors cursor-pointer bg-neutral-900/50">
          <CardContent className="flex flex-col items-center justify-center h-full min-h-[280px]">
            <div className="p-4 rounded-full bg-neutral-800 mb-4">
              <Plus className="h-8 w-8 text-neutral-400" />
            </div>
            <p className="font-medium text-white">Criar novo pipeline</p>
            <p className="text-sm text-neutral-500 text-center mt-1">
              Crie workflows de automação personalizados
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
