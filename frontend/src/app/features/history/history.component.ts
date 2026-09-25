import { Component, OnInit, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { RouterLink } from '@angular/router';

import { environment } from '../../../environments/environment';
import { TextSegment, parseApiDate, toSegments } from '../../shared/chat-format';

interface ConversationSummary {
  conversation_id: string;
  title: string;
  last_question: string;
  message_count: number;
  updated_at: string;
}

interface HistorySource {
  course: string | null;
  page: number | null;
}

interface HistoryMessage {
  id: string;
  question: string;
  answer: string;
  sources: HistorySource[];
  created_at: string;
}

interface Conversation {
  id: string;
  title: string;
  preview: string;
  date: Date;
  messageCount: number;
}

interface Exchange {
  id: string;
  question: string;
  answer: TextSegment[];
  sources: HistorySource[];
}

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [DatePipe, RouterLink],
  templateUrl: './history.component.html',
  styleUrl: './history.component.scss'
})
export class HistoryComponent implements OnInit {
  conversations: Conversation[] = [];
  isLoading = false;
  errorMessage = '';

  selectedConversation: Conversation | null = null;
  exchanges: Exchange[] = [];
  isLoadingDetail = false;
  detailError = '';

  private readonly http = inject(HttpClient);

  ngOnInit(): void {
    this.loadConversations();
  }

  loadConversations(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.http.get<ConversationSummary[]>(`${environment.apiUrl}/history/`).subscribe({
      next: (summaries) => {
        this.conversations = summaries.map((summary) => ({
          id: summary.conversation_id,
          title: summary.title,
          preview: summary.last_question,
          date: parseApiDate(summary.updated_at),
          messageCount: summary.message_count
        }));
        this.isLoading = false;
      },
      error: (error: HttpErrorResponse) => {
        this.errorMessage = this.getDetail(error) ?? 'Impossible de charger votre historique.';
        this.isLoading = false;
      }
    });
  }

  selectConversation(conversation: Conversation): void {
    this.selectedConversation = conversation;
    this.exchanges = [];
    this.detailError = '';
    this.isLoadingDetail = true;

    this.http
      .get<HistoryMessage[]>(`${environment.apiUrl}/history/${conversation.id}`)
      .subscribe({
        next: (messages) => {
          // Ignore une réponse arrivée après un clic sur une autre conversation
          if (this.selectedConversation?.id !== conversation.id) return;
          this.exchanges = messages.map((message) => ({
            id: message.id,
            question: message.question,
            answer: toSegments(message.answer),
            sources: message.sources
          }));
          this.isLoadingDetail = false;
        },
        error: (error: HttpErrorResponse) => {
          if (this.selectedConversation?.id !== conversation.id) return;
          this.detailError = this.getDetail(error) ?? 'Impossible de charger cette conversation.';
          this.isLoadingDetail = false;
        }
      });
  }

  deleteConversation(id: string): void {
    this.http.delete(`${environment.apiUrl}/history/${id}`).subscribe({
      next: () => {
        this.conversations = this.conversations.filter(
          conversation => conversation.id !== id
        );

        if (this.selectedConversation?.id === id) {
          this.selectedConversation = null;
          this.exchanges = [];
        }
      },
      error: (error: HttpErrorResponse) => {
        this.errorMessage = this.getDetail(error) ?? 'La suppression a échoué. Réessayez.';
      }
    });
  }

  private getDetail(error: HttpErrorResponse): string | null {
    const detail: unknown = error.error?.detail;
    return typeof detail === 'string' ? detail : null;
  }
}
