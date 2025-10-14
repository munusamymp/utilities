#!/bin/bash

# --- CONFIGURATION ---
JENKINS_URL="http://jenkins-master:8080"
NODE_NAME="jenkins-slave-01"
WORK_DIR="/home/jenkins"
SECRET_NAME="jenkins/jnlp-token/slave-01"
REGION="us-east-1"

# Install dependencies
yum update -y
amazon-linux-extras enable corretto8
yum install -y java-1.8.0-amazon-corretto wget aws-cli

# Get the JNLP secret token from AWS Secrets Manager
JNLP_SECRET=$(aws secretsmanager get-secret-value \
  --region $REGION \
  --secret-id $SECRET_NAME \
  --query SecretString \
  --output text | jq -r .token)

# Create jenkins user
useradd -m -d $WORK_DIR jenkins
mkdir -p $WORK_DIR
chown jenkins:jenkins $WORK_DIR

# Download agent.jar
cd $WORK_DIR
sudo -u jenkins wget $JENKINS_URL/jnlpJars/agent.jar

# Create agent startup script
cat <<EOF > $WORK_DIR/start-agent.sh
#!/bin/bash
cd $WORK_DIR
exec java -jar agent.jar -jnlpUrl $JENKINS_URL/computer/$NODE_NAME/slave-agent.jnlp -secret $JNLP_SECRET -workDir "$WORK_DIR"
EOF

chmod +x $WORK_DIR/start-agent.sh
chown jenkins:jenkins $WORK_DIR/start-agent.sh

# Create systemd service
cat <<EOF > /etc/systemd/system/jenkins-agent.service
[Unit]
Description=Jenkins JNLP Agent
After=network.target

[Service]
User=jenkins
WorkingDirectory=$WORK_DIR
ExecStart=/bin/bash $WORK_DIR/start-agent.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start agent
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable jenkins-agent
systemctl start jenkins-agent

