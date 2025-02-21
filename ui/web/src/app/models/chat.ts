import { Message } from './message';
/**
 * A series of interaction with Creative Assistant under the same id.
 */
export interface Chat {
  /**
   * Chat Id: Unique identifier of a chat.
   */
  id: string;
  /**
   * Chat name:  Optional chat name.
   */
  name: string;
  /**
   * Created at: When chat was created.
   */
  createdAt: string;
  /**
   * Pinned: Whether the chat is pinned.
   */
  pinned: boolean;
  /**
   * Messages: All messages in the chat.
   */
  messages: Message[];
}
