import {
  Component,
  Input,
  AfterViewChecked,
  ViewChild,
  ElementRef,
  Pipe,
  PipeTransform,
  inject,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatMenuModule } from '@angular/material/menu';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatIcon } from '@angular/material/icon';
import { MatButton } from '@angular/material/button';
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
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  constructor(private chatService: ChatService) {}
  ngOnInit() {
    this.router.navigate(['/chats', { id: this.id }]);
  }

  ngOnChanges() {
    this.getMessages();
  }
  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  getMessages() {
    if (!this.isNewChat && this.id !== undefined) {
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

@Component({
  selector: 'chat-options',
  standalone: true,
  imports: [MatMenuModule, MatButtonModule, MatIconModule, MatIcon, MatButton],
  template: `
    <button mat-icon-button [matMenuTriggerFor]="menu">
      @if (pinned) {
        <mat-icon>push_pin</mat-icon>
      } @else {
        <mat-icon>more_vert</mat-icon>
      }
    </button>
    <mat-menu #menu="matMenu">
      @if (pinned) {
        <button mat-menu-item (click)="unpinChat()">Unpin</button>
      } @else {
        <button mat-menu-item (click)="pinChat()">Pin</button>
      }
      <button mat-menu-item (click)="renameChat('new-name')">Rename</button>
      <button mat-menu-item (click)="deleteChat()">Delete</button>
    </mat-menu>
  `,
})
export class ChatOptionsComponent {
  @Input() id = '';
  @Input() pinned: boolean = false;
  private chatService = inject(ChatService);

  pinChat() {
    this.chatService.pinChat(this.id).subscribe();
  }
  unpinChat() {
    this.chatService.unpinChat(this.id).subscribe();
  }

  renameChat(name: string) {
    this.chatService.renameChat(this.id, name).subscribe();
  }

  deleteChat() {
    this.chatService.deleteChat(this.id).subscribe();
  }
}
