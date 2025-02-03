import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Chat } from '../models/chat';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  constructor(private httpClient: HttpClient) {}

  getChat(chatId: string) {
    return this.httpClient.get<Chat>(`api/chats/${chatId}`);
  }

  getChats() {
    return this.httpClient.get<Chat[]>(`api/chats`);
  }
}
