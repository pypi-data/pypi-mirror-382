# 🐳 Docker Hub Publishing Instructions

## Quick Commands to Publish

Run these commands from the `memory-journal-mcp` directory:

### 1. Build Both Images
```bash
# Build optimized Alpine-based version (with ML, ~225MB) 
docker build -f Dockerfile -t writenotenow/memory-journal-mcp:latest .
docker build -f Dockerfile -t writenotenow/memory-journal-mcp:full .
```

### 2. Push to Docker Hub
```bash
# Push optimized Alpine versions
docker push writenotenow/memory-journal-mcp:latest
docker push writenotenow/memory-journal-mcp:full
```

### 3. Test the Published Images
```bash
# Test Alpine version
docker pull writenotenow/memory-journal-mcp:latest
docker run --rm -v ./data:/app/data writenotenow/memory-journal-mcp:latest python -c "print('✅ Alpine version works!')"

# Test full version  
docker pull writenotenow/memory-journal-mcp:full
docker run --rm -v ./data:/app/data writenotenow/memory-journal-mcp:full python -c "print('✅ Full version works!')"
```

## After Publishing

Update the README.md with the new Docker Hub instructions:

```bash
# Quick start becomes:
docker pull writenotenow/memory-journal-mcp:lite
docker run -v ./data:/app/data writenotenow/memory-journal-mcp:lite
```

## Repository Info

- **Docker Hub**: https://hub.docker.com/r/writenotenow/memory-journal-mcp
- **Namespace**: writenotenow  
- **Repository**: memory-journal-mcp
- **Tags**: 
  - `lite` - Core features, no semantic search (~200MB)
  - `latest` / `full` - Complete with semantic search (~2GB)

## Expected Build Times

- **Lite version**: ~2-3 minutes
- **Full version**: ~10-15 minutes (downloads PyTorch, etc.)

Once published, users can skip the build step entirely! 🚀