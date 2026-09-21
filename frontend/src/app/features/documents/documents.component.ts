import { Component } from '@angular/core';

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [],
  templateUrl: './documents.component.html',
  styleUrl: './documents.component.scss'
})
export class DocumentsComponent {
  selectedFile: File | null = null;
  isDragging = false;
  isUploading = false;
  uploadSuccess = false;
  errorMessage = '';

  private readonly allowedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];

  private readonly maxFileSize = 25 * 1024 * 1024;

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

    setTimeout(() => {
      this.isUploading = false;
      this.uploadSuccess = true;
    }, 1500);
  }

  removeFile(): void {
    this.selectedFile = null;
    this.errorMessage = '';
    this.uploadSuccess = false;
  }
}