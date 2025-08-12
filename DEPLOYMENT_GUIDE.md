# Talkbridge Production Deployment Guide

## 🚀 Copy-Paste Steps for Deployment

### 1. Prepare the server

```bash
# Create system user
sudo useradd -m -s /bin/bash talkbridge
sudo usermod -aG sudo talkbridge

# Create project directory
sudo mkdir -p /srv/talkbridge
sudo chown talkbridge:talkbridge /srv/talkbridge

# Copy code
sudo -u talkbridge rsync -av /path/to/local/talkbridge/ /srv/talkbridge/
# Use git:
# sudo -u talkbridge git clone https://github.com/tu-usuario/talkbridge.git /srv/talkbridge
```

### 2. Configure Conda for the Talkbridge user

```bash
# Change Talkbridge user
sudo -u talkbridge -i

# Install miniconda (if it does not exist)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# Initialize Conda
~/miniconda3/bin/conda init bash
source ~/.bashrc

# Create environment and install dependencies
conda create -n talkbridge python=3.11 -y
conda activate talkbridge
pip install -r /srv/talkbridge/requirements.txt

# Out of Talkbridge User
exit
```

### 3. Configure environment variables

```bash
# Copy configuration template
sudo -u talkbridge cp /srv/talkbridge/.env.example /srv/talkbridge/.env

# Edit configuration (replace <i_DOMINIO> with your real domain)
sudo -u talkbridge nano /srv/talkbridge/.env
```

### 4. Install and enable services

```bash
# Go to the project directory
cd /srv/talkbridge

# Instalar Systemd Service
sudo make install-systemd

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable --now talkbridge

# Check state
sudo systemctl status talkbridge
```

### 5. CONFIGURE NGINX

```bash
# Install nginx (if no is installed)
sudo apt update
sudo apt install nginx

# Install Talkbridge configuration (replace tu-dominio.com)
make install-nginx DOMAIN=tu-dominio.com

# Verify configuration
sudo nginx -t

# Recharge Nginx
sudo systemctl reload nginx
```

### 6. Obtain SSL certificate

```bash
# Configure https certificate (replace your-domain.com)
make tls DOMAIN=tu-dominio.com

# Manually:
# sudo certbot --nginx -d your-domain.com
```

### 7. VERIFICAR DEPLOYMENT

```bash
# Verify application health
make health-check DOMAIN=your-domain.com

# See service logs
make logs

# See service status
make status

# Manual test
curl -I https://your-domain.com
```

## 🔧 MAINTENANCE COMMANDS

```bash
# Restart application
make restart

# See logs in real time
sudo journalctl -u talkbridge -f

# Update code
sudo -u talkbridge git pull origin main
make restart

# Configuration backup
sudo cp /srv/talkbridge/.env /srv/talkbridge/.env.backup.$(date +%Y%m%d)
```

## 🐛 COMMON PROBLEMS ANS SOLUTIONS

### Occupied port
```bash
# Verify what the port 8000 uses
sudo netstat -tlnp | grep :8000
sudo systemctl stop talkbridge
```

### File permissions
```bash
# Correct permissions
sudo chown -R talkbridge:talkbridge /srv/talkbridge
sudo chmod -R 755 /srv/talkbridge
```

### Canda in the found
```bash
# Verify Conda Route at Systemd Service
sudo -u talkbridge which conda
# Edit /etc/systemd/system/talkbridge.service if necessary
```

### Nginx can't connect with backend
```bash
# Verify that the service is running
curl -I http://localhost:8000
sudo systemctl status talkbridge

# Verificar logs de Nginx
sudo tail -f /var/log/nginx/talkbridge_error.log
```

### SELinux issues (CentOS/RHEL)
```bash
# Allow NGINX connections
sudo setsebool -P httpd_can_network_connect 1
```

### Falling SSL certificate
```bash
# Check DNS
nslookup your-domain.com

# Verify that Puerto 80 is free
sudo netstat -tlnp | grep :80

# Reintear certificate
sudo certbot --nginx -d tu-dominio.com -v
```

## 📊 MONITORING

### IMPORTANT LOGS
```bash
# Application logs
sudo journalctl -u talkbridge -f

# Logs de Nginx
sudo tail -f /var/log/nginx/talkbridge_access.log
sudo tail -f /var/log/nginx/talkbridge_error.log

# Logs of the system
sudo tail -f /var/log/syslog | grep talkbridge
```

### Basic metrics
```bash
# CPU use and process memory
ps aux | grep streamlit

# Active connections
sudo netstat -an | grep :8000

# Disk space
df -h /srv/talkbridge
```

## ✅ CHECKLIST FINAL

-[] Code copied to `/srv/talkbridge`
-[] User `talkbridge` created and configured
-[] Conda Environment `talkbridge` created and installed
-[] `.env` file configured with correct domain
-[] Systemd service installed and enabled
-[] nginx configured and recharged  
-[] SSL certificate obtained and installed
-[] Health Check works locally
-[] Health Check works from the Internet
-[] DNS points to the server correctly
-[] Firewall allows traffic in 80/443 ports
-[] Logs do not show critical errors
