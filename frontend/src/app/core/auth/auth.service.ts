import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface AuthToken { access_token: string; token_type: string; }
export interface AuthUser { id: string; email: string; }
export interface Credentials { email: string; password: string; }

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly storageKey = 'access_token';

  get token(): string | null { return localStorage.getItem(this.storageKey); }
  get isAuthenticated(): boolean { return this.token !== null; }

  login(credentials: Credentials): Observable<AuthToken> {
    return this.http.post<AuthToken>(`${environment.apiUrl}/auth/login`, credentials).pipe(
      tap((response) => localStorage.setItem(this.storageKey, response.access_token))
    );
  }

  register(credentials: Credentials): Observable<AuthUser> {
    return this.http.post<AuthUser>(`${environment.apiUrl}/auth/register`, credentials);
  }

  logout(): void {
    localStorage.removeItem(this.storageKey);
    void this.router.navigate(['/login']);
  }
}
