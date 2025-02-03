import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class AssistantService {
  constructor(private httpClient: HttpClient) {}

  interact(question: string, chatId: string) {
    return this.httpClient.post('api/interact', {
      question,
      chat_id: chatId,
    });
  }
}
