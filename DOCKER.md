# 🐳 SpotiFLAC Docker Guide

Run SpotiFLAC in a Docker container - perfect for NAS devices and headless servers!

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/weedo078/SpotiFLAC.git
cd SpotiFLAC

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Using Docker CLI

```bash
# Build the image
docker build -t spotiflac:latest .

# Run the container
docker run -d \
  --name spotiflac \
  -v $(pwd)/downloads:/downloads \
  -v $(pwd)/settings:/app/settings \
  -e SPOTIFLAC_OUTPUT_DIR=/downloads \
  spotiflac:latest

# View logs
docker logs -f spotiflac

# Stop the container
docker stop spotiflac
```

## 📁 Directory Structure

```
SpotiFLAC/
├── downloads/          # Downloaded FLAC files (mounted volume)
├── settings/           # Persistent settings (mounted volume)
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
└── .dockerignore       # Files to exclude from image
```

## ⚙️ Configuration

### Environment Variables

- `SPOTIFLAC_OUTPUT_DIR`: Output directory for downloads (default: `/downloads`)
- `QT_QPA_PLATFORM`: Qt platform (default: `offscreen` for headless)
- `DISPLAY`: X11 display (default: `:99`)

### Volumes

- `/downloads`: Mount this to save downloaded files to your host
- `/app/settings`: Mount this to persist application settings

### Resource Limits

Adjust in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'        # Maximum CPU cores
      memory: 2G       # Maximum RAM
```

## 🖥️ NAS Setup

### Synology NAS

1. Install Docker from Package Center
2. Upload `docker-compose.yml` to your NAS
3. Create folders: `downloads` and `settings`
4. Run via Docker UI or SSH:
   ```bash
   docker-compose up -d
   ```

### QNAP NAS

1. Install Container Station
2. Create a new application from `docker-compose.yml`
3. Configure volume mappings
4. Start the container

### Unraid

1. Go to Docker tab
2. Add Container
3. Use image: `spotiflac:latest`
4. Map volumes:
   - Container: `/downloads` → Host: `/mnt/user/downloads/spotiflac`
   - Container: `/app/settings` → Host: `/mnt/user/appdata/spotiflac`

## 🔧 Advanced Usage

### Build with Custom Base Image

```dockerfile
# Use different Python version
FROM python:3.12-slim
```

### Run with X11 Display (for GUI)

```bash
docker run -d \
  --name spotiflac \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/downloads:/downloads \
  spotiflac:latest
```

### Multi-Architecture Build

```bash
# Build for ARM (Raspberry Pi, etc.)
docker buildx build --platform linux/arm64 -t spotiflac:arm64 .

# Build for AMD64 (x86_64)
docker buildx build --platform linux/amd64 -t spotiflac:amd64 .
```

## 📊 Resource Requirements

### Minimum
- **CPU**: 1 core
- **RAM**: 512 MB
- **Storage**: 2 GB (image) + downloads

### Recommended
- **CPU**: 2 cores
- **RAM**: 2 GB
- **Storage**: 5 GB (image) + downloads

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs spotiflac

# Verify permissions
chmod -R 755 downloads settings
```

### GUI not working
```bash
# Use offscreen platform
docker run -e QT_QPA_PLATFORM=offscreen ...
```

### Chrome/Selenium issues
```bash
# Rebuild with --no-cache
docker build --no-cache -t spotiflac:latest .
```

### Permission denied on downloads
```bash
# Fix ownership
sudo chown -R 1000:1000 downloads
```

## 🔄 Updates

```bash
# Pull latest code
git pull

# Rebuild image
docker-compose build --no-cache

# Restart container
docker-compose up -d
```

## 📝 Notes

- The container runs in **headless mode** by default
- GUI is available via X11 forwarding if needed
- Downloads are saved to the mounted volume
- Settings persist across container restarts
- Chrome/Selenium included for Spotify secret scraping

## 🆘 Support

For issues or questions:
- GitHub Issues: https://github.com/weedo078/SpotiFLAC/issues
- Docker Hub: (coming soon)

## 📜 License

Same as SpotiFLAC - see main README.md
