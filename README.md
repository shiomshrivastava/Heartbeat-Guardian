# Heart ECG Analysis Project

A Streamlit-based web application for ECG data analysis and visualization with machine learning capabilities.

## 🚀 Quick Start

```bash
# 1. Activate the Conda environment
conda activate shiomenv

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py
```

## 📋 Prerequisites

- Python 3.13 or higher
- Anaconda or Miniconda
- MongoDB (for user authentication)
- ECG Sensor (for data collection)

## 🔧 Detailed Setup Guide

### First Time Setup

1. **Install Anaconda** (Skip if already installed)
   - Download from [Anaconda's website](https://www.anaconda.com/products/individual)
   - Follow the installation instructions for Windows

2. **Create a New Conda Environment**
   ```bash
   conda create -n shiomenv python=3.13
   conda activate shiomenv
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK Data**
   ```bash
   python -m nltk.downloader punkt
   python -m nltk.downloader wordnet
   python -m nltk.downloader stopwords
   ```

### Hardware Setup

1. **ECG Sensor Connection**
   - Connect the ECG sensor to your computer's USB port
   - Note the COM port number (usually shown in Device Manager)
   - Update the port in the application if needed

2. **MongoDB Setup**
   - Install MongoDB if not already installed
   - Ensure MongoDB service is running
   - Default connection string: `mongodb://localhost:27017/`

## 🏃‍♂️ Running the Application

1. **Activate Environment** (Every time you start)
   ```bash
   conda activate shiomenv
   ```

2. **Start the Application**
   ```bash
   streamlit run app.py
   ```

3. **Access the Web Interface**
   - Open your browser
   - Navigate to `http://localhost:8501`

## 🛠 Troubleshooting

### Common Issues and Solutions

1. **"Streamlit command not found"**
   ```bash
   conda activate shiomenv
   pip install streamlit
   ```

2. **Missing Package Errors**
   ```bash
   pip install [package_name]
   ```

3. **NLTK Resource Errors**
   ```bash
   python -m nltk.downloader [resource_name]
   ```

4. **MongoDB Connection Issues**
   - Check if MongoDB is running
   - Verify connection string in application
   - Ensure MongoDB service is started

5. **ECG Sensor Not Detected**
   - Check USB connection
   - Verify correct COM port in Device Manager
   - Update port settings in application

## 📦 Main Features

- Real-time ECG data visualization
- User authentication system
- Machine learning-based analysis
- Interactive data plots
- Natural language processing capabilities

## 🔍 Project Structure

```
Heart/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── ECG.json           # Configuration file
└── pages/
    ├── login.py       # Login page
    └── signup.py      # Signup page
```

## 💻 Development Notes

- Minimum Python version: 3.13
- Tested on Windows 11
- Uses Streamlit for web interface
- Requires active MongoDB instance
- ECG sensor must be connected

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## ⚙️ Environment Management

### Creating a New Environment
```bash
conda create -n shiomenv python=3.13
conda activate shiomenv
pip install -r requirements.txt
```

### Updating Requirements
```bash
pip freeze > requirements.txt
```

### Removing Environment
```bash
conda deactivate
conda env remove -n shiomenv
```