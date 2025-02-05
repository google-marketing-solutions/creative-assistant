import { Component, Input, OnInit, inject } from '@angular/core';
import { NgClass, CommonModule } from '@angular/common';
import { MarkdownModule, MarkdownService } from 'ngx-markdown';
import { Message } from './../../models/message';

@Component({
  selector: 'message',
  standalone: true,
  imports: [NgClass, CommonModule, MarkdownModule],
  templateUrl: './message.component.html',
  styleUrl: './message.component.css',
})
export class MessageComponent implements OnInit {
  @Input() m: Message;
  private markdownService = inject(MarkdownService);
  isUserMessage = false;
  formattedHtml = '';

  ngOnInit() {
    this.isUserMessage = this.m.author === 'user';
    this.formattedHtml = this.formatMessageToHtml(this.m.content);
  }

  private formatMessageToHtml(content: string): string {
    content = content.trim();

    const lines = content.split('\n');

    const formattedLines = lines.map((line) => {
      if (line.startsWith('* ')) {
        return `- ${line.substring(2)}`;
      }
      return line;
    });

    const markdownText = formattedLines.join('\n');

    const html = this.markdownService.parse(markdownText);
    return html.toString();
  }
}
