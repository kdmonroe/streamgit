FROM python:3.10-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install -r requirements.txt

COPY app/ .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false", "--client.showErrorDetails", "false", "--client.toolbarMode", "minimal"]