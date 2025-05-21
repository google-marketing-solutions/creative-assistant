import {
  Component,
  EventEmitter,
  ViewChild,
  ElementRef,
  AfterViewInit,
  Input,
  Output,
  inject,
} from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';

import { AssistantService } from '../../services/assistant.service';
import { Message } from './../../models/message';

@Component({
  selector: 'prompt',
  standalone: true,
  imports: [
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './prompt.component.html',
  styleUrl: './prompt.component.css',
})
export class PromptComponent implements AfterViewInit {
  @ViewChild('prompt') prompt!: ElementRef<HTMLTextAreaElement>;
  private textarea: HTMLTextAreaElement;
  @Input() chatId!: string;
  @Output() readonly messageSent = new EventEmitter<Message>();
  @Output() readonly responseReceived = new EventEmitter<Message>();
  @Output() readonly newChatIdReceived = new EventEmitter<string>();
  private assistantService = inject(AssistantService);

  ngAfterViewInit() {
    this.textarea = this.prompt.nativeElement;
  }

  onEnter(value: string, chatId: string) {
    this.assistantService.interact(value, chatId).subscribe((response: any) => {
      this.responseReceived.emit({
        author: 'assistant',
        content: response.output.toString(),
      });
      if (chatId === undefined) {
        this.chatId = response.chat_id;
        this.newChatIdReceived.emit(this.chatId);
      }
    });
    this.messageSent.emit({ author: 'user', content: value });
    this.prompt.nativeElement.value = '';
  }
}
