import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { HistoryComponent } from './history.component';
import { environment } from '../../../environments/environment';

describe('HistoryComponent', () => {
  let component: HistoryComponent;
  let fixture: ComponentFixture<HistoryComponent>;
  let http: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HistoryComponent],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HistoryComponent);
    component = fixture.componentInstance;
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => http.verify());

  it('loads the conversations from the API', () => {
    http.expectOne(`${environment.apiUrl}/history/`).flush([
      { conversation_id: 'c1', title: 'Qu’est-ce que le RAG ?', last_question: 'Et les embeddings ?', message_count: 2, updated_at: '2026-09-25T20:00:00' }
    ]);
    fixture.detectChanges();

    expect(component.conversations.length).toBe(1);
    expect(component.conversations[0].date.toISOString()).toBe('2026-09-25T20:00:00.000Z');
    expect(fixture.nativeElement.textContent).toContain('Qu’est-ce que le RAG ?');
  });

  it('shows the full exchanges of the selected conversation', () => {
    http.expectOne(`${environment.apiUrl}/history/`).flush([
      { conversation_id: 'c1', title: 'Question', last_question: 'Question', message_count: 1, updated_at: '2026-09-25T20:00:00' }
    ]);
    component.selectConversation(component.conversations[0]);
    http.expectOne(`${environment.apiUrl}/history/c1`).flush([
      { id: 'm1', question: 'Question', answer: 'Une **réponse** en gras', sources: [{ course: 'Cours IA', page: 3 }], created_at: '2026-09-25T20:00:00' }
    ]);
    fixture.detectChanges();

    const detail: HTMLElement = fixture.nativeElement.querySelector('.history-detail');
    expect(detail.querySelector('strong')?.textContent).toBe('réponse');
    expect(detail.textContent).toContain('Cours IA');
  });

  it('removes a conversation after a successful delete', () => {
    http.expectOne(`${environment.apiUrl}/history/`).flush([
      { conversation_id: 'c1', title: 'Question', last_question: 'Question', message_count: 1, updated_at: '2026-09-25T20:00:00' }
    ]);
    component.deleteConversation('c1');
    http.expectOne({ method: 'DELETE', url: `${environment.apiUrl}/history/c1` }).flush(null, { status: 204, statusText: 'No Content' });

    expect(component.conversations).toEqual([]);
  });
});
