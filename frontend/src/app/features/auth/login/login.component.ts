import { Component, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';

@Component({ selector: 'app-login', standalone: true, imports: [ReactiveFormsModule, RouterLink], templateUrl: './login.component.html', styleUrl: './login.component.scss' })
export class LoginComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  readonly form = this.fb.nonNullable.group({ email: ['', [Validators.required, Validators.email]], password: ['', Validators.required] });
  errorMessage = '';
  submitting = false;
  readonly justRegistered = this.route.snapshot.queryParamMap.get('registered') === 'true';

  submit(): void {
    this.errorMessage = '';
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.submitting = true;
    this.auth.login(this.form.getRawValue()).subscribe({
      next: () => {
        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
        const destination = returnUrl?.startsWith('/') && !returnUrl.startsWith('//') ? returnUrl : '/';
        void this.router.navigateByUrl(destination);
      },
      error: (error: HttpErrorResponse) => {
        this.errorMessage = error.status === 401 ? 'Email ou mot de passe incorrect.' :
          error.status === 0 ? 'Impossible de joindre le serveur. Vérifiez votre connexion.' :
          this.getDetail(error) ?? 'La connexion a échoué. Réessayez.';
        this.submitting = false;
      }
    });
  }

  private getDetail(error: HttpErrorResponse): string | null {
    const detail: unknown = error.error?.detail;
    return typeof detail === 'string' ? detail : null;
  }
}
