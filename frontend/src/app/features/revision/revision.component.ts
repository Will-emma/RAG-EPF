import { Component } from '@angular/core';

interface QuizQuestion {
  question: string;
  options: string[];
  correctAnswer: number;
}

@Component({
  selector: 'app-revision',
  standalone: true,
  imports: [],
  templateUrl: './revision.component.html',
  styleUrl: './revision.component.scss'
})
export class RevisionComponent {
  currentQuestionIndex = 0;
  selectedAnswer: number | null = null;
  showResult = false;
  answers: (number | null)[] = [];

  questions: QuizQuestion[] = [
    {
      question: 'Qu’est-ce qu’un modèle de langage (LLM) ?',
      options: [
        'Un système capable de traiter et générer du texte',
        'Un type de base de données relationnelle',
        'Un protocole réseau',
        'Un système de fichiers'
      ],
      correctAnswer: 0
    },
    {
      question: 'Que signifie RAG ?',
      options: [
        'Random Answer Generation',
        'Retrieval-Augmented Generation',
        'Real-time AI Generator',
        'Remote Application Gateway'
      ],
      correctAnswer: 1
    },
    {
      question: 'Quel est le rôle d’un embedding ?',
      options: [
        'Convertir un texte en représentation vectorielle',
        'Créer une interface graphique',
        'Compresser un fichier PDF',
        'Générer une image'
      ],
      correctAnswer: 0
    },
    {
      question: 'Pourquoi utiliser une base vectorielle dans un système RAG ?',
      options: [
        'Pour stocker uniquement des images',
        'Pour rechercher des contenus similaires',
        'Pour remplacer le frontend',
        'Pour gérer les utilisateurs'
      ],
      correctAnswer: 1
    },
    {
      question: 'Quel est l’objectif principal du contexte dans un système RAG ?',
      options: [
        'Fournir au LLM des informations pertinentes pour répondre',
        'Accélérer uniquement le frontend',
        'Créer un compte utilisateur',
        'Modifier automatiquement le modèle'
      ],
      correctAnswer: 0
    }
  ];

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