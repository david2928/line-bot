const { getInventoryData, formatInventoryMessage } = require('../services/sheets');
const scheduler = require('../services/scheduler');
const LineMessagingService = require('../services/lineMessaging');

// Create LINE messaging service instance
const config = {
  channelAccessToken: process.env.CHANNEL_ACCESS_TOKEN,
  channelSecret: process.env.CHANNEL_SECRET
};
const lineMessaging = new LineMessagingService(config);

/**
 * Send weekly inventory update to configured LINE groups
 * Replacement for the Google Apps Script sendWeeklyInventoryUpdate function
 */
async function sendWeeklyInventoryUpdate() {
  try {
    console.log('Running weekly inventory update');
    
    // Get data from Google Sheets
    const reorderItems = await getInventoryData();
    
    // Format the message
    const message = formatInventoryMessage(reorderItems);
    
    // Get the target group ID(s) from environment variables
    const groupIds = process.env.LINE_GROUP_IDS 
                      ? process.env.LINE_GROUP_IDS.split(',') 
                      : [];
    
    if (groupIds.length === 0) {
      throw new Error('No LINE group IDs configured');
    }

    // Send the message to all configured groups
    await lineMessaging.broadcastToGroups(groupIds, message);
    
    console.log('Weekly inventory update sent successfully');
    return { success: true, message: 'Inventory update sent' };
  } catch (error) {
    console.error('Failed to send weekly inventory update:', error);
    return { 
      success: false, 
      error: error.message || 'Unknown error' 
    };
  }
}

/**
 * Manual trigger for inventory update
 */
async function triggerInventoryUpdate(req, res) {
  console.log('Received inventory update request');
  try {
    console.log('Starting inventory update process...');
    const result = await sendWeeklyInventoryUpdate();
    console.log('Inventory update process completed:', result);
    if (result.success) {
      res.json(result);
    } else {
      console.log('Sending error response:', result);
      res.status(500).json(result);
    }
  } catch (error) {
    console.error('Error in triggerInventoryUpdate:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message || 'Unknown error'
    });
  }
}

/**
 * Start or restart the weekly scheduler
 */
function startWeeklyScheduler(req, res) {
  try {
    scheduler.scheduleWeekly('inventory-update', sendWeeklyInventoryUpdate);
    res.json({ 
      success: true, 
      message: 'Weekly inventory update scheduled',
      jobs: scheduler.getJobs()
    });
  } catch (error) {
    console.error('Error starting scheduler:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message
    });
  }
}

/**
 * Stop the weekly scheduler
 */
function stopWeeklyScheduler(req, res) {
  try {
    const result = scheduler.cancelJob('inventory-update');
    res.json({ 
      success: true, 
      cancelled: result,
      jobs: scheduler.getJobs()
    });
  } catch (error) {
    console.error('Error stopping scheduler:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message
    });
  }
}

module.exports = {
  sendWeeklyInventoryUpdate,
  triggerInventoryUpdate,
  startWeeklyScheduler,
  stopWeeklyScheduler
}; 