import numpy as np
import matplotlib.pyplot as plt
import h5py
import sklearn
import sklearn.datasets
import sklearn.linear_model
import scipy.io

def plot_decision_boundary(model, X, y):
    # Set min and max values and give it some padding
    x_min, x_max = X[:,0].min() - 1, X[:,0].max() + 1
    y_min, y_max = X[:,1].min() - 1, X[:,1].max() + 1
    h = 0.01
    # Generate a grid of points with distance h between them
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    xxr = xx.ravel().T
    yyr = yy.ravel().T
    Xmesh = np.vstack((xxr, yyr)).T
    # Predict the function value for the whole grid
    Z = model.predict(Xmesh)
    Z = np.round(Z)
    Z = Z.reshape(xx.shape)
    # Plot the contour and training examples
    plt.contourf(xx, yy, Z, cmap=plt.cm.Spectral)
    plt.ylabel('x2')
    plt.xlabel('x1')
    plt.scatter(X[:,0], X[:,1], c=y.ravel(), cmap=plt.cm.Spectral)
    plt.show()
    
    return
 
def load_2D_dataset():
    data = scipy.io.loadmat('data.mat')
    X_train = data['X'].T
    Y_train = data['y'].T
    X_valtest = data['Xval'].T
    Y_valtest = data['yval'].T
    X_test = X_valtest[:,:100]
    Y_test = Y_valtest[:,:100]
    X_val = X_valtest[:,100:]
    Y_val = Y_valtest[:,100:]
    
    plt.scatter(X_train[0, :], X_train[1, :], c=Y_train.ravel(), s=40, cmap=plt.cm.Spectral);   
    
    return X_train, Y_train, X_test, Y_test, X_val, Y_val