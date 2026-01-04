/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: /app/settings/page.tsx                                                 │
│ Settings Page - Global System Configuration                                     │
└──────────────────────────────────────────────────────────────────────────────┘
*/
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Settings2,
  Webhook,
  Database,
  Bell,
  Shield,
  Key,
  Globe,
  ChevronRight,
  MessageSquare,
  CheckCircle,
  Zap,
  Bot,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function SettingsPage() {
  const { toast } = useToast();

  const [settings, setSettings] = useState({
    general: {
      darkMode: true,
      realTimeNotifications: true,
      notificationSounds: true,
    },
    notifications: {
      emailNotifications: false,
      pushNotifications: true,
      dailySummary: false,
    },
  });

  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      // Simulate API call
      setSettings({
        general: {
          darkMode: true,
          realTimeNotifications: true,
          notificationSounds: true,
        },
        notifications: {
          emailNotifications: false,
          pushNotifications: true,
          dailySummary: false,
        },
      });
    } catch (error) {
      toast({
        title: "Erro ao carregar configurações",
        variant: "destructive",
      });
    }
  };

  const updateSettings = async (key: string, value: any) => {
    setIsLoading(true);
    try {
      setSettings((prev) => ({
        ...prev,
        [key]: { ...prev[key as keyof typeof prev], ...value },
      }));

      toast({
        title: "Configurações atualizadas",
        description: "Suas configurações foram salvas com sucesso",
      });
    } catch (error) {
      toast({
        title: "Erro ao salvar configurações",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 min-h-screen bg-[#121212]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Configurações
        </h1>
        <p className="text-neutral-400 mt-2">
          Configure as opções globais da plataforma
        </p>
      </div>

      {/* Settings Sections */}
      <div className="grid gap-6">
        {/* General Settings */}
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Settings2 className="h-5 w-5" />
              Configurações Gerais
            </CardTitle>
            <CardDescription className="text-neutral-400">
              Configurações básicas da plataforma
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between py-2 border-b border-neutral-800">
              <div>
                <div className="font-medium text-white">Modo Escuro</div>
                <div className="text-sm text-neutral-400">
                  Ativar tema escuro na interface
                </div>
              </div>
              <Switch
                checked={settings.general.darkMode}
                onCheckedChange={(checked) =>
                  updateSettings("general", { darkMode: checked })
                }
              />
            </div>
            <div className="flex items-center justify-between py-2 border-b border-neutral-800">
              <div>
                <div className="font-medium text-white">
                  Notificações em Tempo Real
                </div>
                <div className="text-sm text-neutral-400">
                  Receber notificações instantaneas
                </div>
              </div>
              <Switch
                checked={settings.general.realTimeNotifications}
                onCheckedChange={(checked) =>
                  updateSettings("general", { realTimeNotifications: checked })
                }
              />
            </div>
            <div className="flex items-center justify-between py-2">
              <div>
                <div className="font-medium text-white">Sons de Notificação</div>
                <div className="text-sm text-neutral-400">
                  Reproduzir sons para eventos importantes
                </div>
              </div>
              <Switch
                checked={settings.general.notificationSounds}
                onCheckedChange={(checked) =>
                  updateSettings("general", { notificationSounds: checked })
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Bell className="h-5 w-5" />
              Notificações
            </CardTitle>
            <CardDescription className="text-neutral-400">
              Configure preferencias de notificação
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between py-2 border-b border-neutral-800">
              <div>
                <div className="font-medium text-white">
                  Notificações por Email
                </div>
                <div className="text-sm text-neutral-400">
                  Receber alertas importantes por email
                </div>
              </div>
              <Switch
                checked={settings.notifications.emailNotifications}
                onCheckedChange={(checked) =>
                  updateSettings("notifications", { emailNotifications: checked })
                }
              />
            </div>
            <div className="flex items-center justify-between py-2 border-b border-neutral-800">
              <div>
                <div className="font-medium text-white">Notificações Push</div>
                <div className="text-sm text-neutral-400">
                  Notificações no navegador
                </div>
              </div>
              <Switch
                checked={settings.notifications.pushNotifications}
                onCheckedChange={(checked) =>
                  updateSettings("notifications", { pushNotifications: checked })
                }
              />
            </div>
            <div className="flex items-center justify-between py-2">
              <div>
                <div className="font-medium text-white">Resumo Diário</div>
                <div className="text-sm text-neutral-400">
                  Receber resumo das atividades diárias
                </div>
              </div>
              <Switch
                checked={settings.notifications.dailySummary}
                onCheckedChange={(checked) =>
                  updateSettings("notifications", { dailySummary: checked })
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Security */}
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Shield className="h-5 w-5" />
              Segurança
            </CardTitle>
            <CardDescription className="text-neutral-400">
              Configurações de segurança e autenticação
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              variant="outline"
              className="w-full justify-between gap-2 bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700"
            >
              <span className="flex items-center gap-2">
                <Key className="h-4 w-4" />
                Gerenciar API Keys
              </span>
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              className="w-full justify-between gap-2 bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700"
            >
              <span className="flex items-center gap-2">
                <Globe className="h-4 w-4" />
                Configurar Domínios Permitidos
              </span>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
