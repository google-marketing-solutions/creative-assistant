import { Component, EventEmitter, OnInit, Output, inject } from '@angular/core';
import { MatInputModule } from '@angular/material/input';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MatButtonModule } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatButton } from '@angular/material/button';
import { Router } from '@angular/router';
import { Chat } from './../../models/chat';
import { ChatService } from './../../services/chat.service';
import {
  ChatComponent,
  ChatOptionsComponent,
  TruncatePipe,
} from '../chat/chat.component';

@Component({
  selector: 'chat-list',
  standalone: true,
  imports: [
    ChatComponent,
    ChatOptionsComponent,
    MatSelectModule,
    MatFormFieldModule,
    MatIconModule,
    FormsModule,
    ReactiveFormsModule,
    MatInputModule,
    TruncatePipe,
    MatTooltipModule,
    MatMenuModule,
    MatButtonModule,
    MatIcon,
    MatButton,
  ],
  templateUrl: './chat-list.component.html',
  styleUrl: './chat-list.component.css',
})
export class ChatListComponent implements OnInit {
  chats: Chat[] = [];
  selectedChat: string;
  @Output() readonly chatSelected = new EventEmitter<string>();
  private readonly router = inject(Router);

  constructor(private chatService: ChatService) {}
  ngOnInit() {
    this.getChats();
  }
  getChats() {
    this.chatService.getChats().subscribe((chats) => (this.chats = chats));
  }

  onChatSelected() {
    this.chatSelected.emit(this.selectedChat);
  }

  selectChat(chatId: string) {
    this.selectedChat = chatId;
    this.router.navigate(['/chats', chatId]);
    this.chatSelected.emit(this.selectedChat);
  }
}
