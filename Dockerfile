FROM node:18-slim

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy app source code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Start the app
CMD ["node", "src/app.js"] 