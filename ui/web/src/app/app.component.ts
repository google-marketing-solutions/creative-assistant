import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { v4 as uuidv4 } from 'uuid';
import { MatGridListModule } from '@angular/material/grid-list';
import { ChatComponent } from './components/chat/chat.component';
import { ChatListComponent } from './components/chat-list/chat-list.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ChatComponent, ChatListComponent, MatGridListModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  title = 'Creative Assistant';
  newChat = true;
  @Input() chatId = '';
  @Output() readonly newChatStarted = new EventEmitter<boolean>();

  ngOnInit() {
    this.startChat();
  }
  setChat(chatId: string) {
    this.chatId = chatId;
    this.newChat = false;
  }
  startChat() {
    this.chatId = uuidv4().toString();
    this.newChat = true;
    this.newChatStarted.emit(true);
  }
}
