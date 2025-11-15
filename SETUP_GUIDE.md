# Setup Guide - AI-Powered Real-Time Speech Translation

This guide will walk you through setting up the speech translation system step by step.

## Table of Contents

1. [Azure Services Setup](#azure-services-setup)
2. [Local Environment Setup](#local-environment-setup)
3. [Configuration](#configuration)
4. [Testing the Installation](#testing-the-installation)
5. [Deployment](#deployment)
6. [Troubleshooting](#troubleshooting)

---

## 1. Azure Services Setup

### 1.1 Azure Speech Services

1. **Create Azure Speech Service**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Click "Create a resource"
   - Search for "Speech"
   - Click "Create"
   - Fill in the details:
     - Subscription: Your subscription
     - Resource group: Create new or use existing
     - Region: Choose closest region (e.g., East US)
     - Name: Your unique name
     - Pricing tier: Standard S0 (or Free F0 for testing)
   - Click "Review + Create"

2. **Get API Keys**:
   - Navigate to your Speech resource
   - Go to "Keys and Endpoint"
   - Copy **Key 1** and **Location/Region**
   - Save these for later

### 1.2 Azure OpenAI Service

1. **Request Access**:
   - Azure OpenAI requires approval
   - Apply at: https://aka.ms/oai/access

2. **Create Azure OpenAI Resource**:
   - Go to Azure Portal
   - Create a resource → "Azure OpenAI"
   - Fill in details:
     - Resource group: Same as Speech Service
     - Region: East US, West Europe, or other supported region
     - Name: Your unique name
     - Pricing tier: Standard
   - Click "Review + Create"

3. **Deploy a Model**:
   - Navigate to your OpenAI resource
   - Go to "Model deployments" or use Azure OpenAI Studio
   - Click "Create new deployment"
   - Select model: **gpt-4** or **gpt-35-turbo**
   - Give it a deployment name (e.g., "gpt-4")
   - Click "Create"

4. **Get API Keys and Endpoint**:
   - Go to "Keys and Endpoint"
   - Copy:
     - **Key 1**
     - **Endpoint** (e.g., https://your-resource.openai.azure.com/)
   - Note your **deployment name**

### 1.3 Cost Estimation

**Azure Speech Services**:
- Standard: $1 per hour of audio
- Free tier: 5 hours/month

**Azure OpenAI**:
- GPT-4: ~$0.03 per 1K tokens (input) + $0.06 per 1K tokens (output)
- GPT-3.5-Turbo: ~$0.0015 per 1K tokens (input) + $0.002 per 1K tokens (output)

**Estimated cost for 1 hour of live translation to 3 languages**:
- Speech recognition: ~$1
- Translation (GPT-4): ~$2-5
- Speech synthesis: ~$1-2
- **Total: ~$4-8 per hour**

---

## 2. Local Environment Setup

### 2.1 Prerequisites

- **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
- **Git**: Download from [git-scm.com](https://git-scm.com/)
- **Microphone**: For live speech input

### 2.2 Install Python Dependencies

```bash
# Navigate to project directory
cd speech_translation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 2.3 Verify Installation

```bash
# Check Python version
python --version

# Check installed packages
pip list
```

---

## 3. Configuration

### 3.1 Environment Variables

1. **Copy the template**:
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` file** with your Azure credentials:

   ```env
   # Azure Speech Services
   AZURE_SPEECH_KEY=your_speech_key_here
   AZURE_SPEECH_REGION=eastus

   # Azure OpenAI
   AZURE_OPENAI_KEY=your_openai_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   AZURE_OPENAI_API_VERSION=2023-12-01-preview

   # Application Settings
   LOG_LEVEL=INFO
   MAX_AUDIO_DURATION=300
   SAMPLE_RATE=16000
   ```

3. **Important**: Never commit `.env` file to version control!

### 3.2 Verify Configuration

Create a test script `test_config.py`:

```python
from config import settings

print("Configuration Test")
print("=" * 50)
print(f"Speech Region: {settings.azure_speech_region}")
print(f"OpenAI Endpoint: {settings.azure_openai_endpoint}")
print(f"Deployment: {settings.azure_openai_deployment_name}")
print(f"Supported Languages: {len(settings.supported_languages)}")
print("=" * 50)
```

Run it:
```bash
python test_config.py
```

---

## 4. Testing the Installation

### 4.1 Test Speech Recognition

```bash
python examples/test_speech_recognition.py
```

**Expected output**:
- Microphone initialization
- Real-time speech recognition
- Transcribed text displayed

### 4.2 Test Translation

```bash
python examples/test_translation.py
```

**Expected output**:
- Single translation example
- Multi-language translation
- Batch translation
- Quality metrics (BLEU score)

### 4.3 Test Full Pipeline

```bash
python examples/test_full_pipeline.py
```

**Expected output**:
- Real-time speech recognition
- Automatic translation to multiple languages
- Speech synthesis for each language

### 4.4 Test API Server

1. **Start the server**:
   ```bash
   python module4_deployment/api_server.py
   ```

2. **In another terminal, run tests**:
   ```bash
   python examples/test_api.py
   ```

3. **Access API documentation**:
   - Open browser: http://localhost:8000/docs
   - Interactive API documentation (Swagger UI)

---

## 5. Deployment

### 5.1 Local Development Server

```bash
# Start with auto-reload
python module4_deployment/api_server.py

# Or use uvicorn directly
uvicorn module4_deployment.api_server:app --reload --host 0.0.0.0 --port 8000
```

### 5.2 Production Deployment

#### Option A: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "module4_deployment.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t speech-translation .
docker run -p 8000:8000 --env-file .env speech-translation
```

#### Option B: Azure App Service

```bash
# Install Azure CLI
# https://docs.microsoft.com/cli/azure/install-azure-cli

# Login
az login

# Create App Service
az webapp up --name your-app-name --resource-group your-rg --runtime "PYTHON:3.9"

# Configure environment variables
az webapp config appsettings set --name your-app-name --resource-group your-rg --settings @.env
```

#### Option C: Azure Container Instances

```bash
# Build and push to Azure Container Registry
az acr build --registry your-acr --image speech-translation:latest .

# Deploy to ACI
az container create \
  --resource-group your-rg \
  --name speech-translation \
  --image your-acr.azurecr.io/speech-translation:latest \
  --cpu 2 --memory 4 \
  --ports 8000 \
  --environment-variables @.env
```

### 5.3 Production Checklist

- [ ] Use HTTPS/TLS encryption
- [ ] Implement authentication (API keys, OAuth)
- [ ] Set up monitoring and logging
- [ ] Configure auto-scaling
- [ ] Implement rate limiting
- [ ] Set up backup and disaster recovery
- [ ] Configure CDN for static assets
- [ ] Implement health checks
- [ ] Set up CI/CD pipeline
- [ ] Configure firewall rules

---

## 6. Troubleshooting

### 6.1 Common Issues

#### Issue: "Module not found" error

**Solution**:
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: "Authentication failed" error

**Solution**:
- Verify API keys in `.env` file
- Check Azure subscription status
- Ensure services are in the same region (if applicable)
- Regenerate keys in Azure Portal

#### Issue: "No microphone detected"

**Solution**:
- Check microphone permissions
- Test microphone in system settings
- Try different audio input device
- Install audio drivers

#### Issue: High latency (>5 seconds)

**Solution**:
- Use Azure region closer to your location
- Enable translation caching
- Reduce audio chunk size
- Check network connectivity
- Consider upgrading Azure tier

#### Issue: Poor translation quality

**Solution**:
- Use GPT-4 instead of GPT-3.5
- Provide context in translation requests
- Fine-tune system prompts
- Collect feedback and iterate

#### Issue: Rate limit exceeded

**Solution**:
- Implement request throttling
- Use caching for repeated translations
- Upgrade Azure subscription tier
- Implement queue system

### 6.2 Debug Mode

Enable debug logging:

```python
# In config/settings.py or .env
LOG_LEVEL=DEBUG
```

Run with verbose output:
```bash
python -u examples/test_full_pipeline.py
```

### 6.3 Performance Optimization

**For better latency**:
1. Use streaming recognition instead of batch
2. Enable parallel translation for multiple languages
3. Implement aggressive caching
4. Use Azure regions with low latency
5. Optimize audio chunk sizes

**For better quality**:
1. Use higher quality audio input (16kHz+)
2. Reduce background noise
3. Use GPT-4 for translation
4. Provide domain-specific context
5. Fine-tune prompts for your use case

### 6.4 Getting Help

- **Azure Support**: https://azure.microsoft.com/support/
- **Documentation**: Check README.md and code comments
- **Logs**: Check application logs for detailed errors
- **Community**: Azure forums and Stack Overflow

---

## Next Steps

1. ✅ Complete setup and testing
2. 📊 Run performance benchmarks
3. 🎨 Customize for your use case
4. 🚀 Deploy to production
5. 📈 Monitor and optimize
6. 🔄 Iterate based on feedback

---

## Additional Resources

- [Azure Speech Services Docs](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- [Azure OpenAI Docs](https://docs.microsoft.com/azure/cognitive-services/openai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Best Practices](https://docs.python-guide.org/)

---

**Need help?** Create an issue in the repository or consult the documentation.
