pipeline {
    agent any
    environment {
        // Define your environment variables
        GITHUB_REPO = 'https://github.com/ade4sure/MyNetFlix.git'
        DOCKERFILE_PATH = 'path/to/Dockerfile'
        DOCKER_SERVER = '10.128.0.3'
        DOCKER_SERVER_USER = 'jenkinsMaster'
        DOCKER_IMAGE_NAME = 'frontendimage:latest'
        APP_TEMP_PATH = '/tmp/frontend'
        
    }
    stages {
        stage('Deploy to Remote Docker Server') {
            steps {
                script {
                    // Use SSH Agent to run Docker commands on the remote server
                    sshagent(['f355d542-7358-4d58-93a6-cc2e50f192fd']) {
                        
                        // Set the DOCKER_HOST environment variable to specify the remote Docker server
                        env.DOCKER_HOST = "ssh://${DOCKER_SERVER_USER}@${DOCKER_SERVER}"

                        //Show PWD
                        sh "ssh ${DOCKER_SERVER_USER}@${DOCKER_SERVER} 'pwd'"

                        // Display the hostname of the remote host using SSH
                        sh "ssh ${DOCKER_SERVER_USER}@${DOCKER_SERVER} 'hostname'"

                        //Clear frontEnd Temp
                        sh "ssh ${DOCKER_SERVER_USER}@${DOCKER_SERVER} 'sudo [ -d '/tmp/frontend' ] && rm -r /tmp/frontend || pwd'"

                        //get Git version
                        sh "ssh ${DOCKER_SERVER_USER}@${DOCKER_SERVER} 'git --version'"

                        // Clone the GitHub repository on the remote server
                        sh "ssh ${DOCKER_SERVER_USER}@${DOCKER_SERVER} git clone ${GITHUB_REPO} ${APP_TEMP_PATH}"

                        //Get Docker Image path
                        //env.IMAGES_PATH = sh(script: "ssh ${DOCKER_SERVER_USER}@${DOCKER_SERVER} 'docker info | grep -i 'docker root dir''", returnStdout: true).trim()
                        
                        //build Docker image
                        
                        sh '''
                                ssh ${DOCKER_SERVER_USER}@${DOCKER_SERVER} "
                                    cd /tmp/frontend/
                                    docker stop frontendapp
                                    docker rm frontendapp
                                    docker rmi ${DOCKER_IMAGE_NAME}
                                    docker build -f MyNetFlix/Dockerfile -t ${DOCKER_IMAGE_NAME} .
                                    docker run -d -p 80:8080 --name frontendapp ${DOCKER_IMAGE_NAME}"
                            '''
                    }
                }
            }
        }
    }
}

