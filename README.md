# Heartbeat Guardian

A smart ECG monitoring and analysis system that combines hardware and software to provide real-time heart health monitoring. This project integrates an ECG sensor with a user-friendly web interface built using Streamlit, offering advanced analysis and visualization capabilities.

## 🌟 Key Features

- Real-time ECG data monitoring and visualization
- Secure user authentication system
- Machine learning-based anomaly detection
- Interactive data visualization with Plotly
- Natural language processing for medical reports
- Secure data storage with MongoDB

## 🚀 Quick Start

```bash
# 1. Create and activate the Python environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py
```

## 📋 Prerequisites

- Python 3.x
- ECG Sensor Hardware
- MongoDB (for user data storage)
- USB port for sensor connection

## 🔧 Setup Guide

### Software Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/shiomshrivastava/Heartbeat-Guardian.git
   cd Heartbeat-Guardian
   ```

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

## 🛠️ Troubleshooting

1. **Sensor Connection Issues**
   - Check USB connection
   - Verify COM port in Device Manager
   - Ensure correct port is configured in application

2. **MongoDB Connection Error**
   - Verify MongoDB service is running
   - Check connection string
   - Ensure database permissions are correct

3. **Package Installation Issues**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## � License

This project is licensed under the terms specified in the `LICENSE` file.

## 🙏 Acknowledgments

- Thanks to all contributors
- ECG sensor documentation and community
- Streamlit community for excellent documentation

## 🏗️ Project Structure

```
Heartbeat-Guardian/
├── app.py              # Main Streamlit application
├── ECG.json           # Sensor configuration
├── requirements.txt   # Python dependencies
├── iot_code/
│   └── iot_code.ino  # Arduino/ESP32 code for ECG sensor
└── pages/
    ├── login.py      # User authentication
    └── signup.py     # User registration
```

## � Dependencies

Key packages required:
- streamlit>=1.50.0 - Web interface
- pyserial>=3.5 - Serial communication
- plotly>=6.3.0 - Data visualization
- numpy>=2.3.1 - Numerical computations
- pandas>=2.3.3 - Data manipulation
- sentence-transformers>=4.1.0 - NLP processing
- nltk>=3.9.2 - Natural language toolkit
- pymongo>=4.13.0 - MongoDB integration
- scikit-learn>=1.7.1 - Machine learning
- bcrypt>=4.3.0 - Password hashing

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