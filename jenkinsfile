pipeline {
    agent {
        kubernetes {
            yaml """
            apiVersion: v1
            kind: Pod
            metadata:
              labels:
                app: jenkins-agent
            spec:
              containers:
              - name: jnlp
                image: jenkins/inbound-agent:4.13-1
              - name: python
                image: python:3.8
                command:
                - cat
                tty: true
            """
            defaultContainer 'python'
        }
    }
    environment {
        GITHUB_CREDENTIALS = credentials('174b4957-65ad-43db-8932-b2b3ed54e859')
    }
    triggers {
        pollSCM('H/30 * * * *')
    }
    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/DrazThan/user-hasher.git', 
                    credentialsId: '174b4957-65ad-43db-8932-b2b3ed54e859', 
                    branch: 'main'
            }
        }
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Run Python Script') {
            steps {
                sh '/bin/bash ./list_user.sh | python ./check_user.py '
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
