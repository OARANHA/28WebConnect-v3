/*
┌──────────────────────────────────────────────────────────────────────────────┐
│ @file: /app/contacts/page.tsx                                                  │
│ Contacts Page - CRM Integration                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
*/
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Users, Plus, Search, Phone, Mail, MessageCircle, MoreHorizontal } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function ContactsPage() {
  const { toast } = useToast();
  const [contacts, setContacts] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      const mockContacts = [
        {
          id: 1,
          name: "João Silva",
          phone: "+55 11 98765-4321",
          email: "joao.silva@email.com",
          tags: ["cliente-vip", "recorrente"],
          lastContact: "Há 2 horas",
          messages: 45,
        },
        {
          id: 2,
          name: "Maria Santos",
          phone: "+55 11 12345-6789",
          email: "maria.santos@email.com",
          tags: ["lead", "prospecção"],
          lastContact: "Há 1 dia",
          messages: 23,
        },
        {
          id: 3,
          name: "Pedro Costa",
          phone: "+55 21 98765-4321",
          email: "pedro.costa@email.com",
          tags: ["cliente-novo"],
          lastContact: "Há 3 dias",
          messages: 12,
        },
      ];

      setContacts(mockContacts);
    } catch (error) {
      toast({
        title: "Erro ao carregar contatos",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const filteredContacts = contacts.filter((contact) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      contact.name.toLowerCase().includes(searchLower) ||
      contact.email.toLowerCase().includes(searchLower) ||
      contact.phone.includes(searchLower)
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
            Contatos
          </h1>
          <p className="text-neutral-400 mt-2">
            Gerencie seus contatos e leads
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Novo Contato
        </Button>
      </div>

      {/* Search Bar */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
        <Input
          placeholder="Buscar contatos por nome, email ou telefone..."
          className="pl-10 bg-neutral-900 border-neutral-800 text-white"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Contacts List */}
      <Card className="bg-neutral-900 border-neutral-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Users className="h-5 w-5" />
            Todos os Contatos
            <span className="text-sm font-normal text-neutral-500 ml-2">
              ({filteredContacts.length} contatos)
            </span>
          </CardTitle>
          <p className="text-sm text-neutral-400">
            Lista completa de contatos e leads
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {filteredContacts.map((contact) => (
              <div
                key={contact.id}
                className="flex items-center justify-between p-4 rounded-lg border border-neutral-800 hover:bg-neutral-800 transition-colors"
              >
                {/* Contact Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-white">
                      {contact.name}
                    </h3>
                    <div className="flex gap-1">
                      {contact.tags.map((tag: string) => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 text-xs rounded-full bg-emerald-500/10 text-emerald-400"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-sm text-neutral-400">
                    <div className="flex items-center gap-1">
                      <Phone className="h-3 w-3" />
                      {contact.phone}
                    </div>
                    <div className="flex items-center gap-1">
                      <Mail className="h-3 w-3" />
                      {contact.email}
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageCircle className="h-3 w-3" />
                      {contact.messages} mensagens
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                  <div className="text-right text-sm">
                    <div className="text-neutral-500">Último contato</div>
                    <div className="font-medium text-white">
                      {contact.lastContact}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-white hover:bg-neutral-800"
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
