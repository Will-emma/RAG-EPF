import { Component, OnInit, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { environment } from '../../../environments/environment';

interface QuizQuestion {
  question: string;
  options: string[];
  correctAnswer: number;
}

interface QcmResponse {
  questions: QuizQuestion[];
}

@Component({
  selector: 'app-revision',
  standalone: true,
  imports: [],
  templateUrl: './revision.component.html',
  styleUrl: './revision.component.scss'
})
export class RevisionComponent implements OnInit {
  currentQuestionIndex = 0;
  selectedAnswer: number | null = null;
  showResult = false;
  answers: (number | null)[] = [];

  questions: QuizQuestion[] = [];
  loading = false;
  errorMessage: string | null = null;

  private readonly http = inject(HttpClient);

  ngOnInit(): void {
    this.loadQuiz();
  }

  loadQuiz(): void {
    this.loading = true;
    this.errorMessage = null;
    this.questions = [];

    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders(
      token ? { Authorization: `Bearer ${token}` } : {}
    );

    this.http
      .post<QcmResponse>(
        `${environment.apiUrl}/agent/qcm`,
        { course_name: null, num_questions: 5 },
        { headers }
      )
      .subscribe({
        next: (response) => {
          this.questions = response.questions;
          this.loading = false;

          if (this.questions.length === 0) {
            this.errorMessage = 'Aucune question n’a pu être générée.';
          }
        },
        error: (err: HttpErrorResponse) => {
          this.errorMessage =
            err.error?.detail ??
            'Impossible de générer le quiz. Vérifiez que le serveur est lancé.';
          this.loading = false;
        }
      });
  }

  get currentQuestion(): QuizQuestion {
    return this.questions[this.currentQuestionIndex];
  }

  get progress(): number {
    return ((this.currentQuestionIndex + 1) / this.questions.length) * 100;
  }

  selectAnswer(index: number): void {
    if (this.showResult) {
      return;
    }

    this.selectedAnswer = index;
    this.answers[this.currentQuestionIndex] = index;
  }

  nextQuestion(): void {
  if (this.selectedAnswer === null) {
    return;
  }

  if (this.currentQuestionIndex < this.questions.length - 1) {
    this.currentQuestionIndex++;
    this.selectedAnswer = this.answers[this.currentQuestionIndex] ?? null;
  } else {
    this.showResult = true;
  }
}

  previousQuestion(): void {
  if (this.currentQuestionIndex > 0) {
    this.currentQuestionIndex--;
    this.selectedAnswer = this.answers[this.currentQuestionIndex] ?? null;
  }
}

  restartQuiz(): void {
  this.currentQuestionIndex = 0;
  this.selectedAnswer = null;
  this.showResult = false;
  this.answers = [];
  this.loadQuiz();
}

  get score(): number {
  return this.questions.reduce((total, question, index) => {
    return total + (
      this.answers[index] === question.correctAnswer ? 1 : 0
    );
  }, 0);
}

  private getAnswerForQuestion(index: number): number | null {
    return index === this.currentQuestionIndex ? this.selectedAnswer : null;
  }
}