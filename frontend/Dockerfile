
# Use Node LTS base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port React app will run on
EXPOSE 3000

# Start the React development server
CMD ["npm", "start"]
