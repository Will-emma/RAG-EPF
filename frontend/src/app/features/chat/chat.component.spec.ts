import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
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
      role: 'user',
      content: 'Bonjour, peux-tu m\'expliquer ce cours ?'
    },
    {
      role: 'assistant',
      content:
        'Bien sûr. Je peux vous aider à comprendre les notions importantes du cours.'
    }
  ];

  sendMessage(): void {
    const content = this.userInput.trim();

    if (!content || this.isLoading) {
      return;
    }

    this.errorMessage = '';

    this.messages.push({
      role: 'user',
      content
    });

    this.userInput = '';
    this.isLoading = true;

    setTimeout(() => {
      this.messages.push({
        role: 'assistant',
        content:
          'Je suis en train d’analyser votre question à partir des cours de l’EPF.'
      });

      this.isLoading = false;
    }, 1000);
  }
}