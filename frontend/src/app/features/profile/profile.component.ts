import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss'
})
export class ProfileComponent {

  user = {
    initials: 'WE',
    name: 'Will Emma',
    email: 'example@email.com',
    school: 'EPF',
    program: 'Ingénieur',
    year: '4e année'
  };

  stats = {
    conversations: 12,
    quizzes: 5,
    successRate: 87
  };

  isEditing = false;

  editUser = { ...this.user };

  startEditing(): void {
    this.editUser = { ...this.user };
    this.isEditing = true;
  }

  cancelEditing(): void {
    this.editUser = { ...this.user };
    this.isEditing = false;
  }

  saveProfile(): void {
    this.user = { ...this.editUser };

    this.user.initials = this.user.name
      .split(' ')
      .filter(name => name.length > 0)
      .map(name => name[0])
      .join('')
      .toUpperCase();

    this.isEditing = false;
  }
}