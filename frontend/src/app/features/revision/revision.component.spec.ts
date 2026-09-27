import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { environment } from '../../../environments/environment';
import { RevisionComponent } from './revision.component';

const quizQuestions = [
  {
    question: 'Quelle réponse est correcte ?',
    options: ['Bonne réponse', 'Autre réponse', 'Troisième réponse', 'Quatrième réponse'],
    correctAnswer: 0
  },
  {
    question: 'Quelle réponse as-tu ratée ?',
    options: ['Réponse choisie', 'Autre réponse', 'Bonne réponse', 'Dernière réponse'],
    correctAnswer: 2
  },
  {
    question: 'Quelle question est restée vide ?',
    options: ['Réponse A', 'Bonne réponse', 'Réponse C', 'Réponse D'],
    correctAnswer: 1
  }
];

describe('RevisionComponent', () => {
  let component: RevisionComponent;
  let fixture: ComponentFixture<RevisionComponent>;
  let httpTestingController: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RevisionComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()]
    })
    .compileComponents();

    httpTestingController = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(RevisionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('shows configuration and sends no request before generation is requested', () => {
    expect(fixture.nativeElement.querySelector('.quiz-setup')).not.toBeNull();
    expect(component.questionCount).toBe(5);
    expect(component.difficulty).toBe('medium');
    httpTestingController.expectNone(`${environment.apiUrl}/agent/qcm`);
  });

  it('offers all supported question counts and difficulties', () => {
    const questionCounts: HTMLOptionElement[] = Array.from(
      fixture.nativeElement.querySelectorAll('#question-count option')
    );
    const difficulties: HTMLOptionElement[] = Array.from(
      fixture.nativeElement.querySelectorAll('#quiz-difficulty option')
    );

    expect(questionCounts.map((option) => option.value)).toEqual(['5', '10', '15', '20']);
    expect(difficulties.map((option) => option.value)).toEqual(['easy', 'medium', 'hard']);
  });

  it('sends the selected question count and difficulty', () => {
    const questionCount = fixture.nativeElement.querySelector('#question-count') as HTMLSelectElement;
    const difficulty = fixture.nativeElement.querySelector('#quiz-difficulty') as HTMLSelectElement;
    questionCount.value = '10';
    questionCount.dispatchEvent(new Event('change'));
    difficulty.value = 'hard';
    difficulty.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    const generateButton = fixture.nativeElement.querySelector('.quiz-setup .primary-button') as HTMLButtonElement;
    generateButton.click();
    fixture.detectChanges();

    const request = httpTestingController.expectOne(`${environment.apiUrl}/agent/qcm`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      course_name: null,
      num_questions: 10,
      difficulty: 'hard'
    });
    expect(component.loading).toBeTrue();
    request.flush({ questions: quizQuestions });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.quiz-setup')).toBeNull();
    expect(fixture.nativeElement.querySelector('.quiz-card')).not.toBeNull();
  });

  it('retry reuses the selected configuration', () => {
    const questionCount = fixture.nativeElement.querySelector('#question-count') as HTMLSelectElement;
    const difficulty = fixture.nativeElement.querySelector('#quiz-difficulty') as HTMLSelectElement;
    questionCount.value = '15';
    questionCount.dispatchEvent(new Event('change'));
    difficulty.value = 'easy';
    difficulty.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    (fixture.nativeElement.querySelector('.quiz-setup .primary-button') as HTMLButtonElement).click();
    fixture.detectChanges();
    const firstRequest = httpTestingController.expectOne(`${environment.apiUrl}/agent/qcm`);
    firstRequest.flush({ detail: 'Erreur temporaire' }, { status: 502, statusText: 'Bad Gateway' });
    fixture.detectChanges();

    (fixture.nativeElement.querySelector('.result-card .primary-button') as HTMLButtonElement).click();
    fixture.detectChanges();
    const retryRequest = httpTestingController.expectOne(`${environment.apiUrl}/agent/qcm`);
    expect(retryRequest.request.body).toEqual({
      course_name: null,
      num_questions: 15,
      difficulty: 'easy'
    });
    retryRequest.flush({ questions: quizQuestions });
  });

  it('restart reuses the selected configuration', () => {
    component.questionCount = 20;
    component.difficulty = 'medium';
    component.loadQuiz();
    const firstRequest = httpTestingController.expectOne(`${environment.apiUrl}/agent/qcm`);
    expect(firstRequest.request.body).toEqual({
      course_name: null,
      num_questions: 20,
      difficulty: 'medium'
    });
    firstRequest.flush({ questions: quizQuestions });

    component.showResult = true;
    fixture.detectChanges();
    (fixture.nativeElement.querySelector('.restart-button') as HTMLButtonElement).click();
    fixture.detectChanges();

    const restartRequest = httpTestingController.expectOne(`${environment.apiUrl}/agent/qcm`);
    expect(restartRequest.request.body).toEqual({
      course_name: null,
      num_questions: 20,
      difficulty: 'medium'
    });
    restartRequest.flush({ questions: quizQuestions });
  });

  it('returns to configuration without generating and keeps previous values editable', () => {
    component.questionCount = 15;
    component.difficulty = 'hard';
    component.loadQuiz();
    const firstRequest = httpTestingController.expectOne(`${environment.apiUrl}/agent/qcm`);
    firstRequest.flush({ questions: quizQuestions });

    component.showResult = true;
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.restart-button').textContent).toContain('Recommencer');

    (fixture.nativeElement.querySelector('.config-button') as HTMLButtonElement).click();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.quiz-setup')).not.toBeNull();
    expect((fixture.nativeElement.querySelector('#question-count') as HTMLSelectElement).value).toBe('15');
    expect((fixture.nativeElement.querySelector('#quiz-difficulty') as HTMLSelectElement).value).toBe('hard');
    httpTestingController.expectNone(`${environment.apiUrl}/agent/qcm`);

    const questionCount = fixture.nativeElement.querySelector('#question-count') as HTMLSelectElement;
    const difficulty = fixture.nativeElement.querySelector('#quiz-difficulty') as HTMLSelectElement;
    questionCount.value = '10';
    questionCount.dispatchEvent(new Event('change'));
    difficulty.value = 'medium';
    difficulty.dispatchEvent(new Event('change'));
    fixture.detectChanges();
    (fixture.nativeElement.querySelector('.quiz-setup .primary-button') as HTMLButtonElement).click();
    fixture.detectChanges();

    const updatedRequest = httpTestingController.expectOne(`${environment.apiUrl}/agent/qcm`);
    expect(updatedRequest.request.body).toEqual({
      course_name: null,
      num_questions: 10,
      difficulty: 'medium'
    });
    updatedRequest.flush({ questions: quizQuestions });
  });

  it('shows the score and reviews every question with the selected and correct answers', () => {
    component.loadQuiz();
    const request = httpTestingController.expectOne(`${environment.apiUrl}/agent/qcm`);
    request.flush({ questions: quizQuestions });

    component.answers = [0, 0, null];
    component.showResult = true;
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.score').textContent.trim())
      .toBe('Score : 1/3');

    const reviewedQuestions: NodeListOf<HTMLElement> =
      fixture.nativeElement.querySelectorAll('.review-question');
    expect(reviewedQuestions.length).toBe(3);
    expect(reviewedQuestions[0].querySelector('h3')!.textContent).toContain('Question 1');
    expect(reviewedQuestions[0].textContent).toContain('Quelle réponse est correcte ?');
    expect(reviewedQuestions[1].querySelector('h3')!.textContent).toContain('Question 2');
    expect(reviewedQuestions[1].textContent).toContain('Quelle réponse as-tu ratée ?');
    expect(reviewedQuestions[2].querySelector('h3')!.textContent).toContain('Question 3');
    expect(reviewedQuestions[2].textContent).toContain('Quelle question est restée vide ?');
    reviewedQuestions.forEach((question) => {
      expect(question.querySelectorAll('.review-option').length).toBe(4);
    });

    const correctChoice = reviewedQuestions[0].querySelector('.chosen-correct');
    expect(correctChoice!.textContent).toContain('Bonne réponse');
    expect(correctChoice!.textContent).toContain('correcte');
    expect(reviewedQuestions[0].querySelector('.correct-answer-text')).toBeNull();

    expect(reviewedQuestions[1].querySelector('.chosen-incorrect')!.textContent)
      .toContain('Réponse choisie');
    expect(reviewedQuestions[1].querySelector('.correct-answer')!.textContent)
      .toContain('Bonne réponse');
    expect(reviewedQuestions[1].querySelector('.correct-answer-text')!.textContent)
      .toContain('Bonne réponse : C. Bonne réponse');

    expect(reviewedQuestions[2].textContent).toContain('Question non répondue.');
    expect(reviewedQuestions[2].querySelector('.correct-answer-text')!.textContent)
      .toContain('Bonne réponse : B. Bonne réponse');
  });
});
