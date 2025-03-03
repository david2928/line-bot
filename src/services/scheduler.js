/**
 * This module provides scheduling capabilities for the application
 * For a production environment, consider using a more robust solution like:
 * - node-cron for simple scheduling
 * - node-schedule for more complex scheduling
 * - Or better yet, use a dedicated scheduling service like Google Cloud Scheduler
 */

class Scheduler {
  constructor() {
    this.jobs = new Map();
  }

  /**
   * Schedule a job to run weekly
   * @param {string} jobId - Unique identifier for the job
   * @param {Function} callback - Function to execute
   */
  scheduleWeekly(jobId, callback) {
    // Calculate milliseconds in a week
    const weekInMs = 7 * 24 * 60 * 60 * 1000;
    
    // Clear any existing job with this ID
    if (this.jobs.has(jobId)) {
      clearInterval(this.jobs.get(jobId));
    }
    
    // Schedule the job to run immediately and then weekly
    callback(); // Run once immediately
    
    const intervalId = setInterval(callback, weekInMs);
    this.jobs.set(jobId, intervalId);
    
    console.log(`Scheduled job ${jobId} to run weekly`);
    return intervalId;
  }

  /**
   * Cancel a scheduled job
   * @param {string} jobId - ID of the job to cancel
   */
  cancelJob(jobId) {
    if (this.jobs.has(jobId)) {
      clearInterval(this.jobs.get(jobId));
      this.jobs.delete(jobId);
      console.log(`Cancelled job ${jobId}`);
      return true;
    }
    return false;
  }

  /**
   * Get all scheduled jobs
   */
  getJobs() {
    return Array.from(this.jobs.keys());
  }
}

module.exports = new Scheduler(); 