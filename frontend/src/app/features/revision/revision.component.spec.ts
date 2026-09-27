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

    const request = httpTestingController.expectOne(`${environment.apiUrl}/agent/qcm`);
    expect(request.request.method).toBe('POST');
    request.flush({ questions: quizQuestions });
    fixture.detectChanges();
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('shows the score and reviews every question with the selected and correct answers', () => {
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
