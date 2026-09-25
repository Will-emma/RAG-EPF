import { Component, OnInit, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

import { environment } from '../../../environments/environment';
import { parseApiDate } from '../../shared/chat-format';

interface CourseDocument {
  id: string;
  filename: string;
  course_name: string | null;
  status: string;
  created_at: string;
}

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './documents.component.html',
  styleUrl: './documents.component.scss'
})
export class DocumentsComponent implements OnInit {
  selectedFile: File | null = null;
  isDragging = false;
  isUploading = false;
  uploadSuccess = false;
  errorMessage = '';

  documents: CourseDocument[] = [];
  isLoadingDocuments = false;
  documentsError = '';
  deletingId: string | null = null;

  readonly statusLabels: Record<string, string | undefined> = {
    uploaded: 'Importé',
    processing: 'En traitement',
    ready: 'Prêt',
    error: 'Erreur'
  };

  readonly parseApiDate = parseApiDate;

  private readonly http = inject(HttpClient);

  private readonly allowedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];

  private readonly maxFileSize = 25 * 1024 * 1024;

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.isLoadingDocuments = true;
    this.documentsError = '';

    this.http.get<CourseDocument[]>(`${environment.apiUrl}/documents/`).subscribe({
      next: (documents) => {
        this.documents = documents;
        this.isLoadingDocuments = false;
      },
      error: (error: HttpErrorResponse) => {
        this.documentsError =
          this.getDetail(error) ?? 'Impossible de charger vos documents.';
        this.isLoadingDocuments = false;
      }
    });
  }

  deleteDocument(document: CourseDocument): void {
    if (this.deletingId) {
      return;
    }

    const confirmed = window.confirm(
      `Supprimer « ${document.filename} » ? Le chat et les quiz ne l'utiliseront plus.`
    );
    if (!confirmed) {
      return;
    }

    this.deletingId = document.id;
    this.documentsError = '';

    this.http.delete(`${environment.apiUrl}/documents/${document.id}`).subscribe({
      next: () => {
        this.documents = this.documents.filter((item) => item.id !== document.id);
        this.deletingId = null;
      },
      error: (error: HttpErrorResponse) => {
        this.documentsError =
          this.getDetail(error) ?? 'La suppression du document a échoué. Réessayez.';
        this.deletingId = null;
      }
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      this.handleFile(input.files[0]);
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragging = false;

    if (event.dataTransfer?.files.length) {
      this.handleFile(event.dataTransfer.files[0]);
    }
  }

  private handleFile(file: File): void {
    this.errorMessage = '';
    this.uploadSuccess = false;

    if (!this.allowedTypes.includes(file.type)) {
      this.errorMessage =
        'Format non accepté. Veuillez sélectionner un fichier PDF, PPTX ou DOCX.';
      return;
    }

    if (file.size > this.maxFileSize) {
      this.errorMessage =
        'Le fichier est trop volumineux. La taille maximale est de 25 MB.';
      return;
    }

    this.selectedFile = file;
  }

  uploadDocument(): void {
    if (!this.selectedFile || this.isUploading) {
      return;
    }

    this.errorMessage = '';
    this.uploadSuccess = false;
    this.isUploading = true;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.http
      .post<CourseDocument>(`${environment.apiUrl}/documents/upload`, formData)
      .subscribe({
        next: () => {
          this.isUploading = false;
          this.uploadSuccess = true;
          this.loadDocuments();
        },
        error: (error: HttpErrorResponse) => {
          this.errorMessage =
            this.getDetail(error) ??
            (error.status === 0
              ? 'Impossible de joindre le serveur. Vérifiez qu’il est lancé.'
              : 'L’import du document a échoué. Réessayez.');
          this.isUploading = false;
        }
      });
  }

  removeFile(): void {
    this.selectedFile = null;
    this.errorMessage = '';
    this.uploadSuccess = false;
  }

  private getDetail(error: HttpErrorResponse): string | null {
    const detail: unknown = error.error?.detail;
    return typeof detail === 'string' ? detail : null;
  }
}
