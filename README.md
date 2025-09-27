# Stock AI App

A modern AI-powered application for stock analysis. This app provides insights into stock prices, financial metrics, and news headlines using advanced AI models and data pipelines.

## ✨ Features

- **Real-time Stock Analysis** - Get up-to-date stock prices and financial metrics
- **AI-Powered Insights** - Leverage AI to analyze stock trends and provide recommendations
- **Data Pipelines** - Automated ETL pipelines for loading and processing stock data
- **Responsive Design** - Clean, modern UI for seamless user experience

## 🏗️ Architecture

The Stock AI App follows a client-server architecture:

### Client (Next.js + React)
- Modern React application built with Next.js
- Components for user input, stock data display, and analysis results

### Server (FastAPI + Custom AI Models)
- Python backend using FastAPI for API endpoints
- Custom AI models for stock analysis and insights
- Integration with financial data APIs for real-time data

### Pipelines (ETL)
- Python scripts and Jupyter notebooks for data extraction, transformation, and loading
- Integration with databases for storing and querying stock data

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- API keys for financial data sources (e.g., Yahoo Finance, CoinCodex)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vincentsham/stock_ai_app.git
   cd stock_ai_app
   ```

2. **Set up the server**
   ```bash
   cd server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**  
   Create a `.env` file in the server directory:
   ```env
   API_KEY=your_api_key
   DATABASE_URL=your_database_url
   ```

4. **Set up the client**
   ```bash
   cd ../client
   npm install
   ```

### Running the Application

1. **Start the server**
   ```bash
   cd server
   uvicorn main:app --reload
   ```

2. **Start the client**
   ```bash
   cd client
   npm run dev
   ```

3. **Open your browser and navigate to http://localhost:3000**

## 🔍 How It Works

1. **User sends a query** through the interface (e.g., "What is the NVIDIA stock price?")
2. **Server processes the query** using AI models and data pipelines
3. **Data is retrieved** from financial APIs or databases
4. **AI generates insights** based on the data
5. **Results are displayed** to the user in real-time

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org/), [React](https://reactjs.org/), and [FastAPI](https://fastapi.tiangolo.com/)
- Powered by financial data APIs and custom AI models
