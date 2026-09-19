import { Routes } from '@angular/router';

import { HomeComponent } from './features/home/home.component';
import { ChatComponent } from './features/chat/chat.component';
import { DocumentsComponent } from './features/documents/documents.component';
import { RevisionComponent } from './features/revision/revision.component';
import { HistoryComponent } from './features/history/history.component';
import { ProfileComponent } from './features/profile/profile.component';

export const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
  },
  {
    path: 'chat',
    component: ChatComponent,
  },
  {
    path: 'documents',
    component: DocumentsComponent,
  },
  {
    path: 'revision',
    component: RevisionComponent,
  },
  {
    path: 'history',
    component: HistoryComponent,
  },
  {
    path: 'profile',
    component: ProfileComponent,
  },
  {
    path: '**',
    redirectTo: '',
  },
];