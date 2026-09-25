import { TestBed } from '@angular/core/testing';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { provideRouter, Router } from '@angular/router';
import { authInterceptor } from './auth.interceptor';
import { environment } from '../../../environments/environment';

describe('authInterceptor', () => {
  let http: HttpTestingController;
  beforeEach(() => {
    localStorage.setItem('access_token', 'jwt-token');
    TestBed.configureTestingModule({ providers: [provideRouter([]), provideHttpClient(withInterceptors([authInterceptor])), provideHttpClientTesting()] });
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => { http.verify(); localStorage.clear(); });

  it('adds a bearer header to API requests', () => {
    TestBed.inject(HttpClient).get(`${environment.apiUrl}/documents/`).subscribe();
    const request = http.expectOne(`${environment.apiUrl}/documents/`);
    expect(request.request.headers.get('Authorization')).toBe('Bearer jwt-token');
    request.flush([]);
  });

  it('logs out and redirects to login when an API call returns 401', () => {
    const router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.returnValue(Promise.resolve(true));
    TestBed.inject(HttpClient).get(`${environment.apiUrl}/documents/`).subscribe({ error: () => undefined });
    http.expectOne(`${environment.apiUrl}/documents/`).flush({ detail: 'expired' }, { status: 401, statusText: 'Unauthorized' });
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('does not log out on a 401 from the auth endpoints', () => {
    TestBed.inject(HttpClient).post(`${environment.apiUrl}/auth/login`, {}).subscribe({ error: () => undefined });
    http.expectOne(`${environment.apiUrl}/auth/login`).flush({ detail: 'bad' }, { status: 401, statusText: 'Unauthorized' });
    expect(localStorage.getItem('access_token')).toBe('jwt-token');
  });
});
