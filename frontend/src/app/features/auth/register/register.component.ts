import { Component, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';

@Component({ selector: 'app-register', standalone: true, imports: [ReactiveFormsModule, RouterLink], templateUrl: './register.component.html', styleUrl: './register.component.scss' })
export class RegisterComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  readonly form = this.fb.nonNullable.group({ email: ['', [Validators.required, Validators.email]], password: ['', [Validators.required, Validators.minLength(8)]], confirmPassword: ['', Validators.required] });
  errorMessage = '';
  submitting = false;
  get passwordsMatch(): boolean { return this.form.controls.password.value === this.form.controls.confirmPassword.value; }

  submit(): void {
    this.errorMessage = '';
    if (this.form.invalid || !this.passwordsMatch) { this.form.markAllAsTouched(); return; }
    this.submitting = true;
    const { email, password } = this.form.getRawValue();
    this.auth.register({ email, password }).subscribe({
      next: () => void this.router.navigate(['/login'], { queryParams: { registered: 'true' } }),
      error: (error: HttpErrorResponse) => {
        const detail: unknown = error.error?.detail;
        this.errorMessage = typeof detail === 'string' ? detail : error.status === 0 ?
          'Impossible de joindre le serveur. Vérifiez votre connexion.' : 'La création du compte a échoué. Réessayez.';
        this.submitting = false;
      }
    });
  }
}
