import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

import { DocumentsComponent } from './documents.component';
import { environment } from '../../../environments/environment';

const COURSE = {
  id: 'd1',
  filename: 'cours.pdf',
  course_name: null,
  status: 'ready',
  created_at: '2026-09-25T20:00:00'
};

describe('DocumentsComponent', () => {
  let component: DocumentsComponent;
  let fixture: ComponentFixture<DocumentsComponent>;
  let http: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DocumentsComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()]
    }).compileComponents();

    fixture = TestBed.createComponent(DocumentsComponent);
    component = fixture.componentInstance;
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => http.verify());

  it('loads the documents list from the API', () => {
    http.expectOne(`${environment.apiUrl}/documents/`).flush([COURSE]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('cours.pdf');
    expect(fixture.nativeElement.textContent).toContain('Prêt');
  });

  it('uploads the selected file then refreshes the list', () => {
    http.expectOne(`${environment.apiUrl}/documents/`).flush([]);
    component.selectedFile = new File(['pdf'], 'cours.pdf', { type: 'application/pdf' });

    component.uploadDocument();
    const upload = http.expectOne(`${environment.apiUrl}/documents/upload`);
    expect((upload.request.body as FormData).get('file')).toBe(component.selectedFile);
    upload.flush(COURSE, { status: 201, statusText: 'Created' });

    expect(component.uploadSuccess).toBeTrue();
    http.expectOne(`${environment.apiUrl}/documents/`).flush([COURSE]);
    expect(component.documents.length).toBe(1);
  });

  it('shows the backend message when the upload fails', () => {
    http.expectOne(`${environment.apiUrl}/documents/`).flush([]);
    component.selectedFile = new File(['pdf'], 'cours.pdf', { type: 'application/pdf' });

    component.uploadDocument();
    http.expectOne(`${environment.apiUrl}/documents/upload`)
      .flush({ detail: 'Fichier trop volumineux.' }, { status: 400, statusText: 'Bad Request' });

    expect(component.errorMessage).toBe('Fichier trop volumineux.');
  });

  it('deletes a document after confirmation', () => {
    http.expectOne(`${environment.apiUrl}/documents/`).flush([COURSE]);
    spyOn(window, 'confirm').and.returnValue(true);

    component.deleteDocument(component.documents[0]);
    http.expectOne({ method: 'DELETE', url: `${environment.apiUrl}/documents/d1` })
      .flush(null, { status: 204, statusText: 'No Content' });

    expect(component.documents).toEqual([]);
  });

  it('does not delete when the confirmation is cancelled', () => {
    http.expectOne(`${environment.apiUrl}/documents/`).flush([COURSE]);
    spyOn(window, 'confirm').and.returnValue(false);

    component.deleteDocument(component.documents[0]);

    http.expectNone({ method: 'DELETE' });
    expect(component.documents.length).toBe(1);
  });
});
