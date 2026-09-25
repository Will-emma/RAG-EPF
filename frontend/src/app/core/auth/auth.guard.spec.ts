import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { authGuard } from './auth.guard';

describe('authGuard', () => {
  beforeEach(() => { localStorage.clear(); TestBed.configureTestingModule({ providers: [provideRouter([]), provideHttpClient()] }); });
  it('allows an authenticated user', () => {
    localStorage.setItem('access_token', 'jwt-token');
    expect(TestBed.runInInjectionContext(() => authGuard({} as never, { url: '/chat' } as never))).toBeTrue();
  });
  it('redirects an unauthenticated user to login with the requested URL', () => {
    const result = TestBed.runInInjectionContext(() => authGuard({} as never, { url: '/chat' } as never));
    expect(result).toEqual(TestBed.inject(Router).createUrlTree(['/login'], { queryParams: { returnUrl: '/chat' } }));
  });
});
