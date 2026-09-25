import { Component, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { environment } from '../../../environments/environment';

interface ChatSource {
  course: string | null;
  page: number | null;
}

interface TextSegment {
  text: string;
  bold: boolean;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  segments: TextSegment[];
  sources?: ChatSource[];
}

interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent {
  userInput = '';
  isLoading = false;
  errorMessage = '';

  messages: ChatMessage[] = [
    {
      role: 'assistant',
      segments: toSegments(
        'Bonjour ! Posez-moi une question sur les cours que vous avez importés dans « Mes cours ».'
      )
    }
  ];

  private readonly http = inject(HttpClient);

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
        course_id: null
      })
      .subscribe({
        next: (response) => {
          this.messages.push({
            role: 'assistant',
            segments: toSegments(response.answer),
            sources: response.sources
          });
          this.isLoading = false;
        },
        error: (error: HttpErrorResponse) => {
          const detail: unknown = error.error?.detail;
          this.errorMessage =
            typeof detail === 'string'
              ? detail
              : error.status === 0
                ? 'Impossible de joindre le serveur. Vérifiez qu’il est lancé.'
                : 'Le chat n’a pas pu répondre. Réessayez dans un instant.';
          this.isLoading = false;
        }
      });
  }
}

// Le LLM répond en Markdown : on retire les lignes vides autour de la réponse,
// on remplace les puces "* " / "- " par "• ", on retire les marqueurs d'*italique*
// et on découpe le **gras** en segments
// (affichés via interpolation, donc échappés : pas d'innerHTML).
function toSegments(text: string): TextSegment[] {
  const cleaned = text
    .trim()
    .replace(/^[ \t]*[*-][ \t]+/gm, '• ')
    .replace(/(^|[^*])\*(?![\s*])([^*\n]+?)(?<!\s)\*(?!\*)/g, '$1$2');
  return cleaned
    .split(/\*\*(.+?)\*\*/s)
    .map((part, index) => ({ text: part, bold: index % 2 === 1 }))
    .filter((segment) => segment.text !== '');
}
