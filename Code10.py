
import akshare as ak
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np


def fetch_stock_data(stock_code):
    # Fetch daily stock data using akshare
    # 新浪源 df = ak.stock_zh_a_daily(symbol=stock_code, adjust="qfq")
    df = ak.stock_zh_a_hist(symbol=stock_code, adjust="qfq").iloc[:, :6]
    df.columns = [
        'date',
        'open',
        'close',
        'high',
        'low',
        'volume',
    ]
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    #print(df)
    return df


def prepare_data(df):
    # Calculate some basic technical indicators
    df['SMA5'] = df['close'].rolling(window=5).mean()
    df['SMA20'] = df['close'].rolling(window=20).mean()
    df['RSI'] = calculate_rsi(df['close'], window=14)

    # Create target variable (1 if price goes up, 0 if it goes down)
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

    # Drop NaN values
    df = df.dropna()

    # Select features
    features = ['open', 'high', 'low', 'close', 'volume', 'SMA5', 'SMA20', 'RSI']
    X = df[features]
    y = df['target']

    return X, y


def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def train_model(X, y):
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train a Random Forest classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test_scaled)

    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")

    return model, scaler


def predict_next_day(model, scaler, last_data):
    last_data_scaled = scaler.transform(last_data.reshape(1, -1))
    prediction = model.predict(last_data_scaled)
    probability = model.predict_proba(last_data_scaled)
    return prediction[0], probability[0]


def main(stock_code):
    # Fetch stock data
    df = fetch_stock_data(stock_code)

    # Prepare data
    X, y = prepare_data(df)

    # Train model
    model, scaler = train_model(X, y)

    # Predict for the next day
    last_data = X.iloc[-1].values
    prediction, probability = predict_next_day(model, scaler, last_data)

    if prediction == 1:
        direction = "up"
    else:
        direction = "down"

    print(f"Prediction for the next day: Stock is likely to go {direction}")
    print(f"Probability: Up - {probability[1]:.2f}, Down - {probability[0]:.2f}")


if __name__ == "__main__":
    #新浪源 stock_code = input("Enter the stock code (e.g., sh600000): ")
    #东方财富源
    stock_code = input("Enter the stock code (e.g., 600000): ")
    main(stock_code)

# 1、先导入必要的库:

# - akshare: 用于获取股票数据

# - pandas: 用于数据处理和分析

# - scikit-learn: 用于机器学习模型的训练和预测

# - numpy: 用于数值计算

# 2、简单利用5日和20日移动平均线、RSI指标等指标，使用随机森林分类器模型。

# 备注：随机森林(Random Forest)是一种基于集成学习的机器学习算法，其目的是通过组合多个决策树模型来进行预测。
# 随机森林通过对训练数据进行随机采样，以及在构建每个决策树节点时对特征进行随机选择，来增加模型的多样性和鲁棒性。