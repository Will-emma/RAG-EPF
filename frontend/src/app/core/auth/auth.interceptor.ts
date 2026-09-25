import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const auth = inject(AuthService);
  const token = auth.token;
  if (!token || !request.url.startsWith(environment.apiUrl) || request.headers.has('Authorization')) return next(request);
  return next(request.clone({ setHeaders: { Authorization: `Bearer ${token}` } })).pipe(
    catchError((error: unknown) => {
      // Token expiré ou invalide : on vide la session et on renvoie vers /login.
      if (error instanceof HttpErrorResponse && error.status === 401 && !request.url.startsWith(`${environment.apiUrl}/auth/`)) auth.logout();
      return throwError(() => error);
    })
  );
};
