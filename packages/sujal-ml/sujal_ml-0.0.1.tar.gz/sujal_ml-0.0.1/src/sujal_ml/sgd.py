import numpy as np

def sgd(x, y, xval, yval, mini_batch_size=1, learning_rate=0.01, n_epochs=10):
    """
    SGD is the normal Stochastic Gradient Descent that we did in class.

    ---
    Parameters:
    x: np.array -> training data input
    y: np.array -> training data output
    xval: np.array -> validation data input
    yval: np.array -> validation data ouput
    mini_batch_size = 1: int -> mini batch size for sgd
    learning_rate = 0.01: float -> learning rate for sgd
    n_epochs = 10: int -> number of epochs for sgd

    ---
    Returns
    theta: np.array -> coeff of the linear regression
    train_loss_history: np.array -> history of train loss
    valloss_history: np.array -> history of validation loss
    """
    try:
        m, n = x.shape
    except:
        x = x[:, np.newaxis]
        m, n = x.shape

    x_b = np.c_[np.ones((m, 1)), x]

    mval = len(xval)
    xval_b = np.c_[np.ones((mval, 1)), xval]

    theta = np.random.randn(n + 1, 1)

    trainloss_history = []
    valloss_history = []

    n_batches = m // mini_batch_size

    for epoch in range(n_epochs):
        indices = np.random.permutation(m)
        x_shuffled = x_b[indices]
        y_shuffled = y[indices]

        for i in range(n_batches):
            start_idx = i * mini_batch_size
            end_idx = start_idx + mini_batch_size
            x_batch = x_shuffled[start_idx:end_idx]
            y_batch = y_shuffled[start_idx:end_idx].reshape(-1,1)

            predictions = x_batch.dot(theta)

            errors = y_batch - predictions

            gradients = (-2./mini_batch_size) * x_batch.T.dot(errors)

            theta -= learning_rate * gradients

        y_pred = x_b.dot(theta)
        MSE = np.mean((y.reshape(-1,1) - y_pred)**2)
        trainloss_history.append(MSE)

        yval_pred = xval_b.dot(theta)
        val_MSE = np.mean((yval.reshape(-1,1) - yval_pred)**2)
        valloss_history.append(val_MSE)

    return theta, trainloss_history, valloss_history