import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { MatInputModule } from '@angular/material/input';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { Chat } from './../../models/chat';
import { ChatService } from './../../services/chat.service';
import { ChatComponent, TruncatePipe } from '../chat/chat.component';

@Component({
  selector: 'chat-list',
  standalone: true,
  imports: [
    ChatComponent,
    MatSelectModule,
    MatFormFieldModule,
    MatIconModule,
    FormsModule,
    ReactiveFormsModule,
    MatInputModule,
    TruncatePipe,
  ],
  templateUrl: './chat-list.component.html',
  styleUrl: './chat-list.component.css',
})
export class ChatListComponent implements OnInit {
  chats: Chat[] = [];
  selectedChat: string;
  @Output() readonly chatSelected = new EventEmitter<string>();

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
    this.chatSelected.emit(this.selectedChat);
  }
}
