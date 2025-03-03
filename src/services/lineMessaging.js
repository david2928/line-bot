const line = require('@line/bot-sdk');

/**
 * LINE Messaging Service
 * This replaces the previous LINE Notify implementation with Messaging API
 */
class LineMessagingService {
  constructor(config) {
    this.client = new line.Client(config);
  }

  /**
   * Send a push message to a specific group
   * @param {string} groupId - ID of the LINE group to send to
   * @param {string} message - Text message to send
   */
  async sendGroupMessage(groupId, message) {
    try {
      if (!groupId) {
        throw new Error('Group ID is required');
      }

      // Use the Messaging API to send the message
      const result = await this.client.pushMessage(groupId, {
        type: 'text',
        text: message
      });

      console.log('Message sent successfully');
      return result;
    } catch (error) {
      console.error('Error sending message:', 
        error.originalError?.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Send a message to multiple groups
   * @param {string[]} groupIds - Array of LINE group IDs
   * @param {string} message - Text message to send
   */
  async broadcastToGroups(groupIds, message) {
    try {
      const results = await Promise.all(
        groupIds.map(groupId => this.sendGroupMessage(groupId, message))
      );
      
      return results;
    } catch (error) {
      console.error('Error broadcasting message:', error);
      throw error;
    }
  }
}

module.exports = LineMessagingService; 