import {
  Component,
  EventEmitter,
  ViewChild,
  ElementRef,
  AfterViewInit,
  Input,
  Output,
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

  ngAfterViewInit() {
    this.textarea = this.prompt.nativeElement;
  }

  constructor(private assistantService: AssistantService) {}

  onEnter(value: string, chatId: string) {
    this.assistantService.interact(value, chatId).subscribe((response) => {
      this.responseReceived.emit({
        author: 'assistant',
        content: response.toString(),
      });
    });
    this.messageSent.emit({ author: 'user', content: value });
    this.prompt.nativeElement.value = '';
  }
}
