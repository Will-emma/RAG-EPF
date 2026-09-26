import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { BehaviorSubject } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ChatComponent } from './chat.component';

describe('ChatComponent', () => {
  let fixture: ComponentFixture<ChatComponent>;
  let component: ChatComponent;
  let httpTestingController: HttpTestingController;
  let queryParams: BehaviorSubject<ReturnType<typeof convertToParamMap>>;

  const chatUrl = `${environment.apiUrl}/chat/`;

  beforeEach(() => {
    queryParams = new BehaviorSubject(convertToParamMap({}));

    TestBed.configureTestingModule({
      imports: [ChatComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: { queryParamMap: queryParams.asObservable() }
        }
      ]
    });

    httpTestingController = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(ChatComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(() => {
    httpTestingController.verify();
  });

  function setInput(value: string): HTMLInputElement {
    const input: HTMLInputElement = fixture.nativeElement.querySelector('input[name="message"]');
    input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    component.userInput = value;
    fixture.detectChanges();
    return input;
  }

  it('creates the component', () => {
    expect(component).toBeTruthy();
  });

  it('starts a new conversation and displays the welcome message when there is no conversation parameter', () => {
    const assistantMessage: HTMLElement = fixture.nativeElement.querySelector('.assistant-message');

    expect(component.messages.length).toBe(1);
    expect(assistantMessage.textContent).toContain('Bonjour !');
    httpTestingController.expectNone(`${environment.apiUrl}/history/`);
  });

  it('sends a message, displays the assistant response and renders returned sources', () => {
    setInput('  Explique la thermodynamique  ');
    component.sendMessage();
    fixture.detectChanges();

    const request = httpTestingController.expectOne(chatUrl);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      message: 'Explique la thermodynamique',
      course_id: null,
      conversation_id: null
    });
    expect(fixture.nativeElement.querySelector('.user-message').textContent)
      .toContain('Explique la thermodynamique');

    request.flush({
      answer: 'La thermodynamique étudie les échanges d’énergie.',
      sources: [{ course: 'Physique générale', page: 12 }],
      conversation_id: 'conversation-1'
    });
    fixture.detectChanges();

    const assistantMessages: NodeListOf<HTMLElement> =
      fixture.nativeElement.querySelectorAll('.assistant-message');
    expect(assistantMessages[assistantMessages.length - 1].textContent)
      .toContain('La thermodynamique étudie les échanges d’énergie.');
    expect(fixture.nativeElement.querySelector('.source-course').textContent)
      .toContain('Physique générale');
    expect(fixture.nativeElement.querySelector('.source-page').textContent)
      .toContain('Page 12');
  });

  it('loads a conversation and maps history exchanges to user and assistant messages', () => {
    queryParams.next(convertToParamMap({ conversation: 'conversation-42' }));

    const request = httpTestingController.expectOne(
      `${environment.apiUrl}/history/conversation-42`
    );
    expect(request.request.method).toBe('GET');
    request.flush([
      {
        question: 'Question précédente',
        answer: 'Réponse précédente',
        sources: [{ course: 'Mathématiques', page: 7 }]
      },
      { question: 'Deuxième question', answer: 'Deuxième réponse', sources: [] }
    ]);
    fixture.detectChanges();

    const userMessages: NodeListOf<HTMLElement> =
      fixture.nativeElement.querySelectorAll('.user-message');
    const assistantMessages: NodeListOf<HTMLElement> =
      fixture.nativeElement.querySelectorAll('.assistant-message');
    expect(userMessages.length).toBe(2);
    expect(userMessages[0].textContent).toContain('Question précédente');
    expect(userMessages[1].textContent).toContain('Deuxième question');
    expect(assistantMessages.length).toBe(2);
    expect(assistantMessages[0].textContent).toContain('Réponse précédente');
    expect(assistantMessages[1].textContent).toContain('Deuxième réponse');
    expect(fixture.nativeElement.querySelector('.source-course').textContent)
      .toContain('Mathématiques');
    expect(fixture.nativeElement.querySelector('.source-page').textContent)
      .toContain('Page 7');
  });

  it('shows an error when sending a message fails', () => {
    setInput('Question en échec');
    component.sendMessage();
    const request = httpTestingController.expectOne(chatUrl);
    request.flush({ detail: 'Service indisponible' }, { status: 503, statusText: 'Unavailable' });
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent)
      .toContain('Service indisponible');
    expect(component.isLoading).toBeFalse();
  });

  it('shows an error when loading a conversation fails', () => {
    queryParams.next(convertToParamMap({ conversation: 'missing-conversation' }));
    const request = httpTestingController.expectOne(
      `${environment.apiUrl}/history/missing-conversation`
    );
    request.flush({ detail: 'Conversation introuvable' }, { status: 404, statusText: 'Not Found' });
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent)
      .toContain('Conversation introuvable');
    expect(fixture.nativeElement.querySelector('.assistant-message').textContent)
      .toContain('Bonjour !');
    expect(component.isLoading).toBeFalse();
  });

  it('does not send an empty or whitespace-only message', () => {
    setInput('   \t  ');
    component.sendMessage();
    fixture.detectChanges();

    expect(component.messages.length).toBe(1);
    httpTestingController.expectNone(chatUrl);
  });

  it('blocks another send while a request is loading', () => {
    setInput('Premier message');
    component.sendMessage();
    setInput('Deuxième message');
    component.sendMessage();

    const requests = httpTestingController.match(chatUrl);
    expect(requests.length).toBe(1);
    expect(component.messages.filter((message) => message.role === 'user').length).toBe(1);
    requests[0].flush({ answer: 'Réponse', sources: [], conversation_id: 'conversation-1' });
  });
});
