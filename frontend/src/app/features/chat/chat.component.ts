import { Component, DestroyRef, OnInit, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

import { environment } from '../../../environments/environment';
import { TextSegment, toSegments } from '../../shared/chat-format';

interface ChatSource {
  course: string | null;
  page: number | null;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  segments: TextSegment[];
  sources?: ChatSource[];
}

interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  conversation_id: string;
}

interface HistoryMessage {
  question: string;
  answer: string;
  sources: ChatSource[];
}

const WELCOME_MESSAGE =
  'Bonjour ! Posez-moi une question sur les cours que vous avez importés dans « Mes cours ».';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit {
  userInput = '';
  isLoading = false;
  errorMessage = '';

  messages: ChatMessage[] = [];

  // null = nouvelle conversation (le backend en crée une au premier message)
  private conversationId: string | null = null;

  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);

  ngOnInit(): void {
    // /chat?conversation=<id> reprend une conversation de l'historique ;
    // /chat tout court démarre une nouvelle conversation.
    this.route.queryParamMap
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((params) => {
        const conversationId = params.get('conversation');
        if (conversationId) {
          this.loadConversation(conversationId);
        } else {
          this.startNewConversation();
        }
      });
  }

  sendMessage(): void {
    const content = this.userInput.trim();

    if (!content || this.isLoading) {
      return;
    }

    this.errorMessage = '';

    this.messages.push({
      role: 'user',
      segments: toSegments(content)
    });

    this.userInput = '';
    this.isLoading = true;

    this.http
      .post<ChatResponse>(`${environment.apiUrl}/chat/`, {
        message: content,
        course_id: null,
        conversation_id: this.conversationId
      })
      .subscribe({
        next: (response) => {
          this.conversationId = response.conversation_id;
          this.messages.push({
            role: 'assistant',
            segments: toSegments(response.answer),
            sources: response.sources
          });
          this.isLoading = false;
        },
        error: (error: HttpErrorResponse) => {
          this.errorMessage =
            this.getDetail(error) ??
            (error.status === 0
              ? 'Impossible de joindre le serveur. Vérifiez qu’il est lancé.'
              : 'Le chat n’a pas pu répondre. Réessayez dans un instant.');
          this.isLoading = false;
        }
      });
  }

  private startNewConversation(): void {
    this.conversationId = null;
    this.errorMessage = '';
    this.messages = [{ role: 'assistant', segments: toSegments(WELCOME_MESSAGE) }];
  }

  private loadConversation(conversationId: string): void {
    this.errorMessage = '';
    this.messages = [];
    this.isLoading = true;

    this.http
      .get<HistoryMessage[]>(`${environment.apiUrl}/history/${conversationId}`)
      .subscribe({
        next: (history) => {
          this.conversationId = conversationId;
          this.messages = history.flatMap((exchange): ChatMessage[] => [
            { role: 'user', segments: toSegments(exchange.question) },
            { role: 'assistant', segments: toSegments(exchange.answer), sources: exchange.sources }
          ]);
          this.isLoading = false;
        },
        error: (error: HttpErrorResponse) => {
          this.startNewConversation();
          this.errorMessage =
            this.getDetail(error) ?? 'Impossible de charger cette conversation.';
          this.isLoading = false;
        }
      });
  }

  private getDetail(error: HttpErrorResponse): string | null {
    const detail: unknown = error.error?.detail;
    return typeof detail === 'string' ? detail : null;
  }
}
