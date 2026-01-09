# 🚀 Docker Deployment Guide for EC2

## Prerequisites
- EC2 instance (Ubuntu 20.04+ recommended)
- Security group allowing ports 80, 443, 22
- Domain name (optional but recommended)

## Quick Deployment

### 1. Connect to EC2
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. Run Deployment Script
```bash
curl -sSL https://raw.githubusercontent.com/Momin9/hotel_management/master/deploy.sh | bash
```

### 3. Manual Deployment (Alternative)

#### Install Docker & Docker Compose
```bash
# Update system
sudo apt-get update -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again
exit
```

#### Deploy Application
```bash
# Clone repository
git clone https://github.com/Momin9/hotel_management.git
cd hotel_management

# Configure environment
cp .env.production .env
nano .env  # Update SECRET_KEY, ALLOWED_HOSTS, etc.

# Build and start
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-super-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-ip
DB_HOST=db
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### SSL Certificate (Optional)
```bash
# Create SSL directory
mkdir ssl

# Add your certificate files
# ssl/cert.pem
# ssl/key.pem

# Or use Let's Encrypt
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
```

## Management Commands

### View Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f
docker-compose logs web
docker-compose logs nginx
```

### Restart Services
```bash
docker-compose restart
docker-compose restart web
```

### Update Application
```bash
git pull origin master
docker-compose down
docker-compose up -d --build
docker-compose exec web python manage.py migrate
```

### Backup Database
```bash
docker-compose exec db pg_dump -U postgres hotel_software > backup.sql
```

### Restore Database
```bash
docker-compose exec -T db psql -U postgres hotel_software < backup.sql
```

## Troubleshooting

### Check Container Status
```bash
docker-compose ps
docker-compose logs web
```

### Access Container Shell
```bash
docker-compose exec web bash
docker-compose exec db psql -U postgres hotel_software
```

### Reset Everything
```bash
docker-compose down -v
docker-compose up -d --build
```

## Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Set up SSL certificate
- [ ] Configure firewall (UFW)
- [ ] Regular backups
- [ ] Update containers regularly

## Monitoring
```bash
# Resource usage
docker stats

# Disk usage
docker system df

# Clean up
docker system prune -a
```