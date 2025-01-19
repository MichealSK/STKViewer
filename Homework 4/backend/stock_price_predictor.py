import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from keras.src.models import Sequential
from keras.src.layers import LSTM, Dense


# PRICE PREDICTION
def create_sequences(data, target_col, sequence_length=10):
    sequences = []
    targets = []

    if isinstance(data, np.ndarray):
        raise TypeError("Expected a Pandas DataFrame, but got a NumPy array.")

    for i in range(len(data) - sequence_length):
        seq = data.iloc[i:i + sequence_length].drop(columns=[target_col]).values
        target = data.iloc[i + sequence_length][target_col]
        sequences.append(seq)
        targets.append(target)

    return np.array(sequences), np.array(targets)


def predict_prices(df):
    encoder = LabelEncoder()
    df = df.fillna(0)
    df = df.replace([np.inf, -np.inf], 0)
    df = df.drop(columns=['Symbol', 'Date', 'Max', 'Min'])
    df['RSI_signal'] = encoder.fit_transform(df['RSI_signal'])
    df['MA_signal'] = encoder.fit_transform(df['MA_signal'])
    df['Overall_signal'] = encoder.fit_transform(df['Overall_signal'])
    # scaler = MinMaxScaler()
    # df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    x, y = create_sequences(df, 'Last_Trade_Price', 10)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, shuffle=False)

    model = Sequential([
        LSTM(50, activation='relu', input_shape=(x_train.shape[1], x_train.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(x_train, y_train, epochs=10, batch_size=32, verbose=1)
    loss = model.evaluate(x_test, y_test, verbose=0)
    # print(f"Model Loss (MSE): {loss:.2f}")

    def predict_future(steps):
        future_predictions = []
        last_sequence = x_test[-1]  # Use the last test sequence as the starting point
        for _ in range(steps):
            next_prediction = model.predict(last_sequence[np.newaxis, :, :])[0, 0]
            future_predictions.append(next_prediction)
            # Ensure the new prediction matches the input feature count
            next_prediction_array = np.full((1, last_sequence.shape[1]), next_prediction)
            # Update the sequence by appending the prediction and removing the oldest value
            last_sequence = np.append(last_sequence[1:], next_prediction_array, axis=0)
        return future_predictions

    # print(df['Last_Trade_Price'])

    predictions_1_day = predict_future(1)
    last_value = (df['Last_Trade_Price'].tail(1).values[0])
    # print(last_value)
    # print(float(predictions_1_day[-1]))
    adjusted_value = round((float(predictions_1_day[-1]) + last_value)/2)

    if float(predictions_1_day[-1]) < 0 or adjusted_value > last_value * 2 or adjusted_value < last_value / 2:
        return "Not enough conclusive information to make good predictions."
    else:
        return "Future Price Prediction: " + str(adjusted_value)