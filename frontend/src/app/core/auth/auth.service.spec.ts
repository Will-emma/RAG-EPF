import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { AuthService } from './auth.service';
import { environment } from '../../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let http: HttpTestingController;
  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());

  it('posts credentials and stores the returned JWT', () => {
    service.login({ email: 'a@example.com', password: 'secret' }).subscribe();
    const request = http.expectOne(`${environment.apiUrl}/auth/login`);
    expect(request.request.body).toEqual({ email: 'a@example.com', password: 'secret' });
    request.flush({ access_token: 'jwt-token', token_type: 'bearer' });
    expect(service.token).toBe('jwt-token');
    expect(service.isAuthenticated).toBeTrue();
  });

  it('registers with email and password without storing credentials', () => {
    service.register({ email: 'a@example.com', password: 'secret' }).subscribe();
    const request = http.expectOne(`${environment.apiUrl}/auth/register`);
    expect(request.request.body).toEqual({ email: 'a@example.com', password: 'secret' });
    request.flush({ id: 'user-id', email: 'a@example.com' });
    expect(service.token).toBeNull();
  });
});
