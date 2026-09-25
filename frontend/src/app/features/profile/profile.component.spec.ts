import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, Router } from '@angular/router';
import { routes } from '../../app.routes';
import { ProfileComponent } from './profile.component';

describe('ProfileComponent', () => {
  let component: ProfileComponent;
  let fixture: ComponentFixture<ProfileComponent>;

  beforeEach(async () => {
    localStorage.clear();
    localStorage.setItem('access_token', 'jwt-token');
    localStorage.setItem('user_email', 'etudiant@epf.fr');
    await TestBed.configureTestingModule({
      imports: [ProfileComponent],
      providers: [provideHttpClient(), provideRouter(routes)]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProfileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('displays the signed-in user email', () => {
    expect(fixture.nativeElement.textContent).toContain('Mon profil');
    expect(fixture.nativeElement.textContent).toContain('etudiant@epf.fr');
  });

  it('navigates to the protected profile route when signed in', async () => {
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/profile');
    expect(router.url).toBe('/profile');
  });

  it('redirects an anonymous profile visit to login', async () => {
    localStorage.removeItem('access_token');
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/profile');
    expect(router.url).toContain('/login?returnUrl=');
    expect(decodeURIComponent(router.url)).toContain('/profile');
  });

  it('logs out and redirects to login when the button is clicked', async () => {
    fixture.nativeElement.querySelector('.logout-button').click();
    await fixture.whenStable();
    expect(TestBed.inject(Router).url).toBe('/login');
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('user_email')).toBeNull();
  });
});
