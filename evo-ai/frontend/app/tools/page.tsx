/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: /app/tools/page.tsx                                                     │
│ Tools Page - Custom Tools Management                                             │
└──────────────────────────────────────────────────────────────────────────────┘
*/
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Wrench, Plus, Search, Code, Play, MoreHorizontal, Zap, Layers, Clock } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function ToolsPage() {
  const { toast } = useToast();
  const [tools, setTools] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      const mockTools = [
        {
          id: 1,
          name: "Calculadora de Preços",
          description: "Calcula preços baseado em parâmetros personalizados",
          type: "custom",
          lastUsed: "Há 2 horas",
          executions: 156,
          status: "active",
        },
        {
          id: 2,
          name: "Validador de CPF",
          description: "Valida números de CPF brasileiros",
          type: "custom",
          lastUsed: "Há 4 horas",
          executions: 423,
          status: "active",
        },
        {
          id: 3,
          name: "Buscador de CEP",
          description: "Busca informações de endereço por CEP",
          type: "integration",
          lastUsed: "Há 1 dia",
          executions: 89,
          status: "active",
        },
      ];

      setTools(mockTools);
    } catch (error) {
      toast({
        title: "Erro ao carregar ferramentas",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const filteredTools = tools.filter((tool) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      tool.name.toLowerCase().includes(searchLower) ||
      tool.description.toLowerCase().includes(searchLower)
    );
  });

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
            Ferramentas
          </h1>
          <p className="text-neutral-400 mt-2">
            Gerencie suas ferramentas customizadas para agentes
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Nova Ferramenta
        </Button>
      </div>

      {/* Search Bar */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
        <Input
          placeholder="Buscar ferramentas..."
          className="pl-10 bg-neutral-900 border-neutral-800 text-white"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Tools Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredTools.map((tool) => (
          <Card key={tool.id} className="bg-neutral-900 border-neutral-800 hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="flex items-center gap-2 text-white">
                    {tool.type === "custom" ? (
                      <Wrench className="h-5 w-5 text-emerald-500" />
                    ) : (
                      <Layers className="h-5 w-5 text-blue-500" />
                    )}
                    {tool.name}
                  </CardTitle>
                  <p className="text-sm text-neutral-400">{tool.description}</p>
                </div>
                <Button variant="ghost" size="icon" className="text-white hover:bg-neutral-800">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Type Badge */}
                <div className="flex items-center gap-2">
                  {tool.type === "custom" ? (
                    <>
                      <Code className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-neutral-400">Customizada</span>
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-neutral-400">Integração</span>
                    </>
                  )}
                </div>

                {/* Status */}
                <div className="flex items-center gap-2">
                  <div
                    className={`h-2 w-2 rounded-full ${
                      tool.status === "active"
                        ? "bg-emerald-500"
                        : "bg-neutral-400"
                    }`}
                  ></div>
                  <span className="text-sm text-neutral-400">
                    {tool.status === "active" ? "Ativa" : "Inativa"}
                  </span>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-neutral-400 flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      Último uso
                    </div>
                    <div className="font-medium text-white">{tool.lastUsed}</div>
                  </div>
                  <div>
                    <div className="text-neutral-400 flex items-center gap-1">
                      <Play className="h-3 w-3" />
                      Execuções
                    </div>
                    <div className="font-medium text-white">{tool.executions}</div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700"
                  >
                    Editar
                  </Button>
                  <Button size="sm" className="flex-1 gap-2">
                    <Play className="h-3 w-3" />
                    Testar
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Add New Tool Card */}
        <Card className="border-dashed border-neutral-700 hover:border-emerald-500/50 transition-colors cursor-pointer bg-neutral-900/50">
          <CardContent className="flex flex-col items-center justify-center h-full min-h-[280px]">
            <div className="p-4 rounded-full bg-neutral-800 mb-4">
              <Plus className="h-8 w-8 text-neutral-400" />
            </div>
            <p className="font-medium text-white">Criar nova ferramenta</p>
            <p className="text-sm text-neutral-500 text-center mt-1">
              Crie ferramentas customizadas para seus agentes
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
