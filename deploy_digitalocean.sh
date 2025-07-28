#!/bin/bash
# Digital Ocean Streamlit Deployment Script

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Clone your repository
git clone https://github.com/thegeekybeng/semiconductor-learning-system.git
cd semiconductor-learning-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Install PM2 for process management
sudo npm install -g pm2

# Create PM2 config
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'semiconductor-app',
    script: 'streamlit',
    args: 'run streamlit_demo_simple.py --server.port 8501 --server.address 0.0.0.0',
    interpreter: './venv/bin/python',
    env: {
      OPENAI_API_KEY: 'your-api-key-here'
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup

echo "Streamlit app running on http://your-droplet-ip:8501"
