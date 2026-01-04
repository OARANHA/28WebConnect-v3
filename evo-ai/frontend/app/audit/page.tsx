/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: /app/audit/page.tsx                                                     │
│ Audit Page - Admin Audit Logs                                               │
└──────────────────────────────────────────────────────────────────────────────┘
*/
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollText, Search, Filter, Download, User, Shield, AlertTriangle, Clock, ChevronRight } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function AuditPage() {
  const { toast } = useToast();
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      const mockLogs = [
        {
          id: 1,
          action: "Criou novo agente",
          entity: "Agent: Assistente de Vendas",
          user: "João Silva",
          timestamp: "2025-01-15 14:32:15",
          type: "create",
          ip: "192.168.1.100",
        },
        {
          id: 2,
          action: "Atualizou configuração",
          entity: "Settings: Webhook URL",
          user: "Maria Santos",
          timestamp: "2025-01-15 14:28:42",
          type: "update",
          ip: "192.168.1.101",
        },
        {
          id: 3,
          action: "Deletou contato",
          entity: "Contact: Test User",
          user: "Pedro Costa",
          timestamp: "2025-01-15 14:15:30",
          type: "delete",
          ip: "192.168.1.102",
        },
        {
          id: 4,
          action: "Falha de autenticação",
          entity: "Auth: Login",
          user: "unknown",
          timestamp: "2025-01-15 13:45:11",
          type: "security",
          ip: "203.0.113.42",
        },
      ];

      setAuditLogs(mockLogs);
    } catch (error) {
      toast({
        title: "Erro ao carregar logs",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getActionIcon = (type: string) => {
    switch (type) {
      case "create":
        return <User className="h-4 w-4 text-emerald-500" />;
      case "update":
        return <Shield className="h-4 w-4 text-blue-500" />;
      case "delete":
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case "execute":
        return <Clock className="h-4 w-4 text-purple-500" />;
      case "security":
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      default:
        return <ScrollText className="h-4 w-4 text-neutral-500" />;
    }
  };

  const getActionColor = (type: string) => {
    switch (type) {
      case "create":
        return "text-emerald-600 bg-emerald-50";
      case "update":
        return "text-blue-600 bg-blue-50";
      case "delete":
        return "text-red-600 bg-red-50";
      case "execute":
        return "text-purple-600 bg-purple-50";
      case "security":
        return "text-orange-600 bg-orange-50";
      default:
        return "text-neutral-600 bg-neutral-50";
    }
  };

  const filteredLogs = auditLogs.filter((log) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      log.action.toLowerCase().includes(searchLower) ||
      log.user.toLowerCase().includes(searchLower) ||
      log.entity.toLowerCase().includes(searchLower)
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
            Auditoria
          </h1>
          <p className="text-neutral-400 mt-2">
            Logs de auditoria e atividades do sistema
          </p>
        </div>
        <Button variant="outline" className="gap-2 bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700">
          <Download className="h-4 w-4" />
          Exportar Logs
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
          <Input
            placeholder="Buscar logs por usuário, ação ou entidade..."
            className="pl-10 bg-neutral-900 border-neutral-800 text-white"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <Button variant="outline" className="gap-2 bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700">
          <Filter className="h-4 w-4" />
          Filtros
        </Button>
      </div>

      {/* Audit Logs */}
      <Card className="bg-neutral-900 border-neutral-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <ScrollText className="h-5 w-5" />
            Logs de Atividade
            <span className="text-sm font-normal text-neutral-500 ml-2">
              ({filteredLogs.length} registros)
            </span>
          </CardTitle>
          <CardDescription className="text-neutral-400">
            Histórico completo de ações realizadas na plataforma
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {filteredLogs.map((log) => (
              <div
                key={log.id}
                className="flex items-start gap-4 p-4 rounded-lg border border-neutral-800 hover:bg-neutral-800 transition-colors"
              >
                {/* Icon */}
                <div className="p-2 rounded bg-neutral-800 flex-shrink-0">
                  {getActionIcon(log.type)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`px-2 py-0.5 text-xs font-medium rounded-full ${getActionColor(
                        log.type
                      )}`}
                    >
                      {log.type}
                    </span>
                    <span className="font-semibold text-white">{log.action}</span>
                  </div>
                  <div className="text-sm text-neutral-400 mb-1">{log.entity}</div>
                  <div className="flex flex-wrap gap-4 text-xs text-neutral-500">
                    <span className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {log.user}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {log.timestamp}
                    </span>
                    <span className="flex items-center gap-1">
                      IP: {log.ip}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <Button variant="ghost" size="icon" className="flex-shrink-0 text-white hover:bg-neutral-800">
                  <ScrollText className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-neutral-800">
            <div className="text-sm text-neutral-400">
              Mostrando 1-{filteredLogs.length} de {auditLogs.length} registros
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled className="bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700">
                Anterior
              </Button>
              <Button variant="outline" size="sm" className="bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700">
                Próxima
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
