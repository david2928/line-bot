require('dotenv').config();
const express = require('express');
const line = require('@line/bot-sdk');

const config = {
  channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN,
  channelSecret: process.env.CHANNEL_SECRET
};

const app = express();

// Add middleware to log all incoming requests
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.url}`);
  next();
});

// Add JSON parsing middleware for all routes except /inventory/update
app.use((req, res, next) => {
  if (req.path === '/inventory/update') {
    return next();
  }
  express.json()(req, res, next);
});

const client = new line.Client(config);

// Import controllers
const inventoryController = require('./controllers/inventoryController');

// Add verification endpoint
app.get('/webhook', (req, res) => {
  res.sendStatus(200);
});

// Webhook for LINE Bot events
app.post('/webhook', async (req, res) => {
  try {
    const events = req.body.events;
    console.log('Webhook event:', JSON.stringify(events, null, 2));

    await Promise.all(events.map(async (event) => {
      console.log('Processing event:', event.type);
      
      // For message events, log more details
      if (event.type === 'message') {
        console.log(`Message type: ${event.message.type}, Text: "${event.message.text}"`);
        console.log(`Source type: ${event.source.type}, ID: ${event.source.groupId || event.source.userId}`);
      }
      
      // Handle message commands
      if (event.type === 'message' && event.message.type === 'text') {
        const text = event.message.text.trim();
        
        // Command: !id - Get group/user ID
        if (text === '!id') {
          console.log('!id command detected, attempting to reply...');
          try {
            let idMessage = '';
            if (event.source.type === 'group') {
              idMessage = `Group ID: ${event.source.groupId}`;
            } else if (event.source.type === 'room') {
              idMessage = `Room ID: ${event.source.roomId}`;
            } else {
              idMessage = `User ID: ${event.source.userId}`;
            }
            
            await client.replyMessage(event.replyToken, {
              type: 'text',
              text: idMessage
            });
            console.log('Reply with ID sent successfully');
          } catch (replyError) {
            console.error('Error sending reply:', replyError);
          }
        } 
        // Command: !help - Show available commands
        else if (text === '!help') {
          try {
            await client.replyMessage(event.replyToken, {
              type: 'text',
              text: 'Available commands:\n!id - Get this chat\'s ID\n!help - Show this help message'
            });
          } catch (replyError) {
            console.error('Error sending help reply:', replyError);
          }
        }
        // Not a command
        else {
          console.log('Message received, but not a command');
        }
      }
    }));

    res.status(200).json({ status: 'ok' });
  } catch (err) {
    console.error('Webhook error:', err);
    res.status(200).json({ status: 'error' });
  }
});

// Endpoint for testing message sending
app.post('/test/message', async (req, res) => {
  try {
    const { groupId, message } = req.body;
    if (!groupId) throw new Error('groupId required');

    await client.pushMessage(groupId, {
      type: 'text',
      text: message
    });
    
    res.json({ success: true });
  } catch (error) {
    console.error('Push error:', error.originalError?.response?.data || error);
    res.status(500).json({ error: error.message });
  }
});

// Add a test endpoint for getting group IDs
app.post('/test/getId', async (req, res) => {
  try {
    const { groupId } = req.body;
    if (!groupId) throw new Error('groupId required');

    await client.pushMessage(groupId, {
      type: 'text',
      text: `This group's ID is: ${groupId}`
    });
    
    res.json({ success: true, groupId });
  } catch (error) {
    console.error('Get ID error:', error.originalError?.response?.data || error);
    res.status(500).json({ error: error.message });
  }
});

// Inventory update routes
app.post('/inventory/update', inventoryController.triggerInventoryUpdate);
app.post('/inventory/schedule/start', inventoryController.startWeeklyScheduler);
app.post('/inventory/schedule/stop', inventoryController.stopWeeklyScheduler);

// Status endpoint
app.get('/status', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString()
  });
});

// Add a simple route to test if server is receiving requests
app.get('/', (req, res) => {
  res.status(200).send('LINE Bot server is running.');
});

// Start the scheduler if AUTO_START_SCHEDULER is enabled
if (process.env.AUTO_START_SCHEDULER === 'true') {
  console.log('Auto-starting weekly inventory scheduler');
  const scheduler = require('./services/scheduler');
  scheduler.scheduleWeekly('inventory-update', inventoryController.sendWeeklyInventoryUpdate);
}

// Server startup
const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log('Server running on port', port);
  console.log('To test locally with ngrok:');
  console.log('1. Run: ngrok http ' + port);
  console.log('2. Copy the https URL from ngrok');
  console.log('3. Set the webhook URL in LINE Developer Console to: [ngrok-url]/webhook');
  console.log('4. Try sending !help or !id in your LINE group');
});