FROM node:18-slim

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy app source code (exclude .env file)
COPY . .

# Remove the .env file to prevent it from overriding environment variables
RUN rm -f .env

# Set the PORT environment variable
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

# Start the app
CMD ["node", "src/app.js"] 