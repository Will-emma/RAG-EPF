import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { provideRouter, Router } from '@angular/router';
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
    expect(service.userEmail).toBe('a@example.com');
    expect(service.isAuthenticated).toBeTrue();
  });

  it('registers with email and password without storing credentials', () => {
    service.register({ email: 'a@example.com', password: 'secret' }).subscribe();
    const request = http.expectOne(`${environment.apiUrl}/auth/register`);
    expect(request.request.body).toEqual({ email: 'a@example.com', password: 'secret' });
    request.flush({ id: 'user-id', email: 'a@example.com' });
    expect(service.token).toBeNull();
  });

  it('clears the token and stored email on logout', () => {
    const router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true));
    localStorage.setItem('access_token', 'jwt-token');
    localStorage.setItem('user_email', 'a@example.com');
    service.logout();
    expect(service.token).toBeNull();
    expect(service.userEmail).toBeNull();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });
});
