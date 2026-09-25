import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { LoginComponent } from './login.component';
import { environment } from '../../../../environments/environment';

describe('LoginComponent', () => {
  let fixture: ComponentFixture<LoginComponent>;
  let http: HttpTestingController;
  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({ imports: [LoginComponent], providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()] }).compileComponents();
    fixture = TestBed.createComponent(LoginComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });
  afterEach(() => { http.verify(); localStorage.clear(); });

  it('shows the email and password fields', () => {
    expect(fixture.nativeElement.querySelector('#email')).toBeTruthy();
    expect(fixture.nativeElement.querySelector('#password')).toBeTruthy();
    expect(fixture.nativeElement.textContent).toContain('Se connecter');
  });

  it('sends login credentials and stores the successful token', () => {
    fixture.componentInstance.form.setValue({ email: 'a@example.com', password: 'secret' });
    fixture.componentInstance.submit();
    const request = http.expectOne(`${environment.apiUrl}/auth/login`);
    request.flush({ access_token: 'jwt-token', token_type: 'bearer' });
    expect(localStorage.getItem('access_token')).toBe('jwt-token');
  });

  it('shows a clear message for invalid credentials', () => {
    fixture.componentInstance.form.setValue({ email: 'a@example.com', password: 'wrong' });
    fixture.componentInstance.submit();
    http.expectOne(`${environment.apiUrl}/auth/login`).flush({ detail: 'Email ou mot de passe incorrect.' }, { status: 401, statusText: 'Unauthorized' });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('incorrect');
  });
});
