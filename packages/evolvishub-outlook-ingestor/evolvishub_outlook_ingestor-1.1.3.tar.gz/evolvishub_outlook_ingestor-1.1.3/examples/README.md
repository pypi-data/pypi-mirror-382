# 📚 **EVOLVISHUB OUTLOOK INGESTOR - EXAMPLES**

This directory contains comprehensive examples demonstrating how to use the Evolvishub Outlook Ingestor in various scenarios, from basic email ingestion to production-ready pipelines with monitoring and error handling.

## 📋 **EXAMPLES OVERVIEW**

### 🚀 **1. Basic Graph API Ingestion** (`basic_graph_api_ingestion.py`)
**Difficulty**: Beginner  
**Purpose**: Learn the fundamentals of email ingestion from Microsoft Graph API

**What you'll learn**:
- Setting up Microsoft Graph API credentials
- Basic email fetching and folder operations
- Secure credential management
- Error handling best practices
- Email streaming for large datasets

**Prerequisites**:
- Microsoft Azure App Registration
- Graph API permissions (Mail.Read)
- Client ID, Client Secret, and Tenant ID

**Key Features Demonstrated**:
- ✅ Authentication and connection setup
- ✅ Folder enumeration and email fetching
- ✅ Attachment handling
- ✅ Secure credential encryption
- ✅ Basic error handling patterns

---

### 🔄 **2. Batch Processing with PostgreSQL** (`batch_processing_postgresql.py`)
**Difficulty**: Intermediate  
**Purpose**: Implement efficient batch processing with database storage

**What you'll learn**:
- High-performance batch email processing
- PostgreSQL database integration
- Transaction management
- Memory-efficient streaming
- Performance monitoring and optimization

**Prerequisites**:
- PostgreSQL database server
- Database credentials
- Microsoft Graph API access (from Example 1)

**Key Features Demonstrated**:
- ✅ Batch processing for optimal performance
- ✅ Database transactions and error recovery
- ✅ Email and attachment processing pipeline
- ✅ Memory-efficient streaming operations
- ✅ Performance metrics and reporting
- ✅ Database query examples

---

### 🏭 **3. Complete Production Pipeline** (`complete_pipeline_monitoring.py`)
**Difficulty**: Advanced  
**Purpose**: Production-ready pipeline with comprehensive monitoring

**What you'll learn**:
- Production-grade architecture patterns
- Real-time monitoring and alerting
- Performance optimization techniques
- Caching strategies
- Error handling and recovery
- Notification systems

**Prerequisites**:
- All prerequisites from Examples 1 & 2
- Optional: Redis for enhanced caching
- Optional: Slack webhook for notifications

**Key Features Demonstrated**:
- ✅ Comprehensive system monitoring
- ✅ Real-time alerting and notifications
- ✅ Performance profiling and optimization
- ✅ Advanced caching with LRU cache
- ✅ Health checks and status reporting
- ✅ Production-ready error handling
- ✅ Slack integration for alerts
- ✅ Detailed performance analytics

---

## 🛠️ **SETUP INSTRUCTIONS**

### **1. Environment Setup**

```bash
# Clone the repository
git clone https://github.com/evolvisai/metcal.git
cd metcal/shared/libs/evolvis-outlook-ingestor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[all,dev]
```

### **2. Configuration**

Create a `.env` file in the examples directory:

```bash
# Microsoft Graph API Configuration
GRAPH_CLIENT_ID=your_client_id_here
GRAPH_CLIENT_SECRET=your_client_secret_here
GRAPH_TENANT_ID=your_tenant_id_here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=outlook_ingestor
DB_USER=ingestor_user
DB_PASSWORD=your_secure_password

# Optional: Encryption Key for Credential Manager
MASTER_ENCRYPTION_KEY=your_master_encryption_key

# Optional: Slack Webhook for Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### **3. Database Setup** (For Examples 2 & 3)

```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE outlook_ingestor;
CREATE USER ingestor_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE outlook_ingestor TO ingestor_user;

-- Connect to the outlook_ingestor database
\c outlook_ingestor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

---

## 🚀 **RUNNING THE EXAMPLES**

### **Example 1: Basic Graph API Ingestion**

```bash
cd examples
python basic_graph_api_ingestion.py
```

**Expected Output**:
```
🚀 Starting Basic Microsoft Graph API Email Ingestion Example
📡 Initializing Microsoft Graph API connection...
✅ Successfully connected and authenticated
📁 Fetching available folders...
✅ Found 3 folders:
   - Inbox (150 items, 5 unread)
   - Sent Items (75 items, 0 unread)
   - Drafts (2 items, 0 unread)
📧 Fetching recent emails from Inbox...
✅ Successfully fetched 10 emails
```

### **Example 2: Batch Processing**

```bash
cd examples
python batch_processing_postgresql.py
```

**Expected Output**:
```
🚀 Starting Batch Processing with PostgreSQL Example
🔧 Initializing batch processor components...
✅ All components initialized
🔄 Starting batch processing...
📧 Processing batch of 25 emails...
💾 Stored 25 emails in database
📊 Progress Update:
   Processed: 50
   Stored: 50
   Rate: 12.5 emails/second
```

### **Example 3: Complete Production Pipeline**

```bash
cd examples
python complete_pipeline_monitoring.py
```

**Expected Output**:
```
🚀 Starting Complete Production Pipeline Example
🔧 Initializing production pipeline components...
✅ System monitoring started
✅ All components initialized
🚀 Starting monitored email processing
📋 Cache hit for email msg_001
⚠️ ALERT [MEDIUM]: Low cache hit rate
📊 Comprehensive Pipeline Report:
   Processing Rate: 15.2 emails/second
   Cache Hit Rate: 75%
   Error Rate: 2.1%
```

---

## 🔧 **CUSTOMIZATION GUIDE**

### **Adding Custom Processing Logic**

```python
# Example: Custom email filter
class CustomEmailProcessor(EmailProcessor):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
    
    async def _process_data(self, email: EmailMessage, result: ProcessingResult):
        # Add custom logic here
        if "urgent" in email.subject.lower():
            email.priority = "high"
        
        # Call parent processing
        return await super()._process_data(email, result)
```

### **Custom Monitoring Metrics**

```python
# Add custom metrics to the monitoring system
monitor = get_system_monitor()

# Custom counter
monitor.metrics.increment_counter("custom.emails_filtered")

# Custom gauge
monitor.metrics.set_gauge("custom.processing_queue_size", queue_size)

# Custom timer
monitor.metrics.record_timer("custom.email_processing_time", duration)
```

### **Custom Alert Rules**

```python
# Add custom alert rules
monitor.alert_manager.add_alert_rule(
    name="custom_metric_threshold",
    metric_name="custom.processing_queue_size",
    threshold=100,
    comparison="greater_than",
    severity=AlertSeverity.HIGH,
    component="custom_processor"
)
```

---

## 🐛 **TROUBLESHOOTING**

### **Common Issues**

#### **Authentication Errors**
```
❌ Error: Authentication failed
```
**Solution**: 
- Verify your Microsoft Graph API credentials
- Check that your Azure app has the correct permissions
- Ensure the tenant ID is correct

#### **Database Connection Errors**
```
❌ Error: Could not connect to database
```
**Solution**:
- Verify PostgreSQL is running
- Check database credentials and connection details
- Ensure the database and user exist

#### **Import Errors**
```
❌ Error: No module named 'evolvishub_outlook_ingestor'
```
**Solution**:
- Ensure you've installed the package: `pip install -e .[all]`
- Activate your virtual environment
- Check your Python path

### **Performance Issues**

#### **Slow Processing**
- Increase batch size in configuration
- Enable connection pooling
- Use caching for repeated operations
- Monitor system resources

#### **High Memory Usage**
- Reduce batch size
- Enable streaming mode
- Clear caches periodically
- Monitor memory metrics

---

## 📞 **GETTING HELP**

### **Resources**
- 📚 **Documentation**: See the main README.md
- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions
- 📧 **Support**: support@evolvisai.com

### **Best Practices**
1. **Always use environment variables** for sensitive configuration
2. **Enable monitoring** in production environments
3. **Implement proper error handling** and retry logic
4. **Use batch processing** for high-volume scenarios
5. **Monitor performance metrics** and optimize accordingly
6. **Test thoroughly** before deploying to production

---

## 🎯 **NEXT STEPS**

After working through these examples, you should be ready to:

1. **Deploy to production** with confidence
2. **Customize the pipeline** for your specific needs
3. **Integrate with your existing systems**
4. **Scale horizontally** as your volume grows
5. **Monitor and optimize** performance continuously

For more advanced topics and deployment guides, see the main documentation in the `docs/` directory.

**Happy email processing! 🚀**
