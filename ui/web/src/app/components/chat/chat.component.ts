import {
  Component,
  Input,
  AfterViewChecked,
  ViewChild,
  ElementRef,
} from '@angular/core';
import { PromptComponent } from './../prompt/prompt.component';
import { MessageComponent } from './../message/message.component';
import { Message } from './../../models/message';
import { ChatService } from './../../services/chat.service';

@Component({
  selector: 'chat',
  imports: [MessageComponent, PromptComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css',
})
export class ChatComponent implements AfterViewChecked {
  @Input() id = '';
  messages: Message[] = [];
  isActiveChat = this.id !== '';
  @ViewChild('messagesArea') private messageArea: ElementRef;

  constructor(private chatService: ChatService) {}

  ngOnChanges() {
    this.isActiveChat = this.id !== '';
    this.getMessages();
  }
  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  getMessages() {
    this.chatService
      .getChat(this.id)
      .subscribe((chat) => (this.messages = chat.messages));
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
