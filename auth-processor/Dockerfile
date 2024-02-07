# Use an official Node.js runtime as the base image
FROM node:14

# Set the working directory in the Docker container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install the project dependencies
RUN npm install

# Copy the rest of the project files to the working directory
COPY . .

# Expose port 8080 for the app (change this if your app uses a different port)
#EXPOSE 8080

# Define the command to run the app using CMD
CMD [ "node", "processor.js" ]