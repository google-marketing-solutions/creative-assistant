/**
 * A single interaction with Creative Assistant.
 */
export interface Message {
  /**
   * Author: Who wrote the message, either `user` or `assistant`.
   */
  author: string;
  /**
   * Content: Message text.
   */
  content: string;
}
