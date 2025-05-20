import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class AssistantService {
  private httpClient = inject(HttpClient);

  interact(question: string, chatId: string) {
    return this.httpClient.post('api/interact', {
      question,
      chat_id: chatId,
    });
  }
}
