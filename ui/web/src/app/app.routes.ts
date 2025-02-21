import { Routes } from '@angular/router';
import { ChatComponent } from './components/chat/chat.component';

export const routes: Routes = [
  { path: 'chats/:id', component: ChatComponent },
  { path: '', component: ChatComponent },
];
