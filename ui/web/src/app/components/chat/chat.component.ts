import {
  Component,
  Input,
  AfterViewChecked,
  ViewChild,
  ElementRef,
  Pipe,
  PipeTransform,
} from '@angular/core';
import { PromptComponent } from './../prompt/prompt.component';
import { MessageComponent } from './../message/message.component';
import { Message } from './../../models/message';
import { ChatService } from './../../services/chat.service';

@Pipe({
  name: 'truncate',
})
export class TruncatePipe implements PipeTransform {
  transform(value: string, limit = 30, ellipsis = '...'): string {
    if (!value) {
      return '';
    }

    limit = limit || 50;
    ellipsis = ellipsis || '...';

    if (value.length <= limit) {
      return value;
    }

    return value.substring(0, limit) + ellipsis;
  }
}

@Component({
  selector: 'chat',
  imports: [MessageComponent, PromptComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css',
  providers: [TruncatePipe],
})
export class ChatComponent implements AfterViewChecked {
  @Input() id = '';
  @Input() isNewChat = false;
  messages: Message[] = [];
  @ViewChild('messagesArea') private messageArea: ElementRef;

  constructor(private chatService: ChatService) {}

  ngOnChanges() {
    this.getMessages();
  }
  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  getMessages() {
    if (!this.isNewChat) {
      this.chatService
        .getChat(this.id)
        .subscribe((chat) => (this.messages = chat.messages));
    } else {
      this.messages = [];
    }
  }

  addMessage(message: Message) {
    this.messages.push(message);
  }
  setChat(chatId: string) {
    this.id = chatId;
    this.getMessages();
  }

  scrollToBottom() {
    try {
      this.messageArea.nativeElement.scrollTop =
        this.messageArea.nativeElement.scrollHeight;
    } catch (e) {}
  }
}
