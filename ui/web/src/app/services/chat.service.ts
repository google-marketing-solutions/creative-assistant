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
  deleteChat(chatId: string) {
    return this.httpClient.delete(`api/chats/${chatId}`);
  }
  pinChat(chatId: string) {
    return this.httpClient.patch(`api/chats/${chatId}`, { pinned: true });
  }
  unpinChat(chatId: string) {
    return this.httpClient.patch(`api/chats/${chatId}`, { pinned: false });
  }
  renameChat(chatId: string, name: string) {
    return this.httpClient.patch(`api/chats/${chatId}`, { name });
  }
}
