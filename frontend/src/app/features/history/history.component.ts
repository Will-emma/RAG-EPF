import { Component } from '@angular/core';

interface ChatHistory {
  id: number;
  title: string;
  preview: string;
  date: string;
  messageCount: number;
}

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [],
  templateUrl: './history.component.html',
  styleUrl: './history.component.scss'
})
export class HistoryComponent {
  selectedConversation: ChatHistory | null = null;

  conversations: ChatHistory[] = [
    {
      id: 1,
      title: 'Comprendre le RAG',
      preview: 'Peux-tu m’expliquer le fonctionnement du RAG ?',
      date: 'Aujourd’hui, 10:32',
      messageCount: 8
    },
    {
      id: 2,
      title: 'Les embeddings',
      preview: 'Quelle est la différence entre un embedding et un token ?',
      date: 'Hier, 16:45',
      messageCount: 6
    },
    {
      id: 3,
      title: 'Préparation examen IA',
      preview: 'Quels sont les concepts importants à retenir ?',
      date: '20 sept. 2026, 14:20',
      messageCount: 12
    },
    {
      id: 4,
      title: 'Architecture chatbot',
      preview: 'Comment fonctionne l’architecture d’un chatbot RAG ?',
      date: '19 sept. 2026, 11:08',
      messageCount: 10
    }
  ];

  selectConversation(conversation: ChatHistory): void {
    this.selectedConversation = conversation;
  }

  deleteConversation(id: number): void {
    this.conversations = this.conversations.filter(
      conversation => conversation.id !== id
    );

    if (this.selectedConversation?.id === id) {
      this.selectedConversation = null;
    }
  }
}