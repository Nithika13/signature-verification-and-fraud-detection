import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.cm as cm
from scipy import ndimage
from skimage.measure import regionprops
from skimage import io
from skimage.filters import threshold_otsu   
import tensorflow as tf
import pandas as pd
import numpy as np
from time import time
import keras
from tensorflow.python.framework import ops
import tensorflow.compat.v1 as tf # type: ignore
tf.compat.v1.disable_v2_behavior()
genuine_image_paths = "C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\real"
forged_image_paths = "C:\\Users\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\forged"
def rgbgrey(img):
    greyimg = np.zeros((img.shape[0], img.shape[1]))
    for row in range(len(img)):
        for col in range(len(img[row])):
            greyimg[row][col] = np.average(img[row][col])
    return greyimg
def greybin(img):
    blur_radius = 0.8
    img = ndimage.gaussian_filter(img, blur_radius)  
    thres = threshold_otsu(img)
    binimg = img > thres
    binimg = np.logical_not(binimg)
    return binimg
def preproc(path, img=None, display=True):
    if img is None:
        img = mpimg.imread(path)
    if display:
        plt.imshow(img)
        plt.show()
    grey = rgbgrey(img) 
    if display:
        plt.imshow(grey, cmap = matplotlib.cm.Greys_r)
        plt.show()
    binimg = greybin(grey) 
    if display:
        plt.imshow(binimg, cmap = matplotlib.cm.Greys_r)
        plt.show()
    r, c = np.where(binimg==1)
    signimg = binimg[r.min(): r.max(), c.min(): c.max()]
    if display:
        plt.imshow(signimg, cmap = matplotlib.cm.Greys_r)
        plt.show()
    return signimg
def Ratio(img):
    a = 0
    for row in range(len(img)):
        for col in range(len(img[0])):
            if img[row][col]==True:
                a = a+1
    total = img.shape[0] * img.shape[1]
    return a/total
def Centroid(img):
    numOfWhites = 0
    a = np.array([0,0])
    for row in range(len(img)):
        for col in range(len(img[0])):
            if img[row][col]==True:
                b = np.array([row,col])
                a = np.add(a,b)
                numOfWhites += 1
    rowcols = np.array([img.shape[0], img.shape[1]])
    centroid = a/numOfWhites
    centroid = centroid/rowcols
    return centroid[0], centroid[1]
def EccentricitySolidity(img):
    r = regionprops(img.astype("int8"))
    return r[0].eccentricity, r[0].solidity
def SkewKurtosis(img):
    h,w = img.shape
    x = range(w)  
    y = range(h)  
    xp = np.sum(img,axis=0)
    yp = np.sum(img,axis=1)
    cx = np.sum(x*xp)/np.sum(xp)
    cy = np.sum(y*yp)/np.sum(yp)
    x2 = (x-cx)**2
    y2 = (y-cy)**2
    sx = np.sqrt(np.sum(x2*xp)/np.sum(img))
    sy = np.sqrt(np.sum(y2*yp)/np.sum(img))
    x3 = (x-cx)**3
    y3 = (y-cy)**3
    skewx = np.sum(xp*x3)/(np.sum(img) * sx**3)
    skewy = np.sum(yp*y3)/(np.sum(img) * sy**3)
    x4 = (x-cx)**4
    y4 = (y-cy)**4
    kurtx = np.sum(xp*x4)/(np.sum(img) * sx**4) - 3
    kurty = np.sum(yp*y4)/(np.sum(img) * sy**4) - 3
    return (skewx , skewy), (kurtx, kurty)
def getFeatures(path, img=None, display=False):
    if img is None:
        img = mpimg.imread(path)
    img = preproc(path, display=display)
    ratio = Ratio(img)
    centroid = Centroid(img)
    eccentricity, solidity = EccentricitySolidity(img)
    skewness, kurtosis = SkewKurtosis(img)
    retVal = (ratio, centroid, eccentricity, solidity, skewness, kurtosis)
    return retVal
def getCSVFeatures(path, img=None, display=False):
    if img is None:
        img = mpimg.imread(path)
    temp = getFeatures(path, display=display)
    features = (temp[0], temp[1][0], temp[1][1], temp[2], temp[3], temp[4][0], temp[4][1], temp[5][0], temp[5][1])
    return features
def makeCSV():
    if not(os.path.exists('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\Features')):
        os.mkdir('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\Features')
        print('New folder "Features" created')
    if not(os.path.exists('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\Features\\Training')):
        os.mkdir('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\Features\\Training')
        print('New folder "Features/Training" created')
    if not(os.path.exists('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\Features\\Testing')):
        os.mkdir('C:\\Users\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\Features\\Testing')
        print('New folder "Features/Testing" created')
    gpath = genuine_image_paths
    fpath = forged_image_paths
    for person in range(1,13):
        per = ('00'+str(person))[-3:]
        print('Saving features for person id-',per)  
        with open('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\Features\\Training\\training_'+per+'.csv', 'w') as handle:
            handle.write('ratio,cent_y,cent_x,eccentricity,solidity,skew_x,skew_y,kurt_x,kurt_y,output\n')
            for i in range(0,3):
                source = os.path.join(gpath, per+per+'_00'+str(i)+'.png')
                features = getCSVFeatures(path=source)
                handle.write(','.join(map(str, features))+',1\n')
            for i in range(0,3):
                source = os.path.join(fpath, '021'+per+'_00'+str(i)+'.png')
                features = getCSVFeatures(path=source)
                handle.write(','.join(map(str, features))+',0\n')
        with open('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\Features\\Testing\\testing_'+per+'.csv', 'w') as handle:
            handle.write('ratio,cent_y,cent_x,eccentricity,solidity,skew_x,skew_y,kurt_x,kurt_y,output\n')
            for i in range(3, 5):
                source = os.path.join(gpath, per+per+'_00'+str(i)+'.png')
                features = getCSVFeatures(path=source)
                handle.write(','.join(map(str, features))+',1\n')
            for i in range(3,5):
                source = os.path.join(fpath, '021'+per+'_00'+str(i)+'.png')
                features = getCSVFeatures(path=source)
                handle.write(','.join(map(str, features))+',0\n')
def testing(path):
    feature = getCSVFeatures(path)
    if not(os.path.exists('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\TestFeatures')):
        os.mkdir('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\TestFeatures')
    with open('C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\TestFeatures\\testcsv.csv', 'w') as handle:
        handle.write('ratio,cent_y,cent_x,eccentricity,solidity,skew_x,skew_y,kurt_x,kurt_y\n')
        handle.write(','.join(map(str, feature))+'\n')  
makeCSV()
n_input = 9
train_person_id = input("Enter person's id : ")
test_image_path = input("Enter path of signature image : ")
train_path = 'C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\Features\\Training\\training_' + train_person_id + '.csv'
testing(test_image_path)
test_path = 'C:\\Users\\Shobi\\OneDrive\\Desktop\\PROJECT\\Signature-Forgery-Detection-main\\TestFeatures\\testcsv.csv'
def readCSV(train_path, test_path, type2=False):
    df = pd.read_csv(train_path, usecols=range(n_input))
    train_input = np.array(df.values)
    train_input = train_input.astype(np.float32, copy=False)  
    df = pd.read_csv(train_path, usecols=(n_input,))
    temp = [elem[0] for elem in df.values]
    correct = np.array(temp)
    corr_train = keras.utils.to_categorical(correct,2)    
    df = pd.read_csv(test_path, usecols=range(n_input))
    test_input = np.array(df.values)
    test_input = test_input.astype(np.float32, copy=False)
    if not(type2):
        df = pd.read_csv(test_path, usecols=(n_input,))
        temp = [elem[0] for elem in df.values]
        correct = np.array(temp)
        corr_test = keras.utils.to_categorical(correct,2)    
    if not(type2):
        return train_input, corr_train, test_input, corr_test
    else:
        return train_input, corr_train, test_input
ops.reset_default_graph()
learning_rate = 0.001
training_epochs = 1000
display_step = 1
n_hidden_1 = 7 
n_hidden_2 = 10 
n_hidden_3 = 30 
n_classes = 2 
X = tf.placeholder("float", [None, n_input])
Y = tf.placeholder("float", [None, n_classes])
weights = {
    'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1], seed=1)),
    'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
    'h3': tf.Variable(tf.random_normal([n_hidden_2, n_hidden_3])),
    'out': tf.Variable(tf.random_normal([n_hidden_1, n_classes], seed=2))
}
biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1], seed=3)),
    'b2': tf.Variable(tf.random_normal([n_hidden_2])),
    'b3': tf.Variable(tf.random_normal([n_hidden_3])),
    'out': tf.Variable(tf.random_normal([n_classes], seed=4))
}
def multilayer_perceptron(x):
    layer_1 = tf.tanh((tf.matmul(x, weights['h1']) + biases['b1']))
    layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])
    layer_3 = tf.add(tf.matmul(layer_2, weights['h3']), biases['b3'])
    out_layer = tf.tanh(tf.matmul(layer_1, weights['out']) + biases['out'])
    return out_layer
logits = multilayer_perceptron(X)
loss_op = tf.reduce_mean(tf.squared_difference(logits, Y))
optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=learning_rate) 
train_op = optimizer.minimize(loss_op)
pred = tf.nn.softmax(logits)  
correct_prediction = tf.equal(tf.argmax(pred,1), tf.argmax(Y,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
init = tf.global_variables_initializer()
#import pyfiglet
#ascii_art = pyfiglet.figlet_format("Genuine Image")
#print('\033[91m' + ascii_art + '\033[0m')
def evaluate(train_path, test_path, type2=False):   
    if not(type2):
        train_input, corr_train, test_input, corr_test = readCSV(train_path, test_path)
    else:
        train_input, corr_train, test_input = readCSV(train_path, test_path, type2)
    ans = 'Random'
    with tf.Session() as sess:
        sess.run(init)
        for epoch in range(training_epochs):
            _, cost = sess.run([train_op, loss_op], feed_dict={X: train_input, Y: corr_train})
            if cost<0.0001:
                break
        accuracy1 =  accuracy.eval({X: train_input, Y: corr_train})
        if type2 is False:
            accuracy2 =  accuracy.eval({X: test_input, Y: corr_test})
            return accuracy1, accuracy2
        else:
            prediction = pred.eval({X: test_input})
            if prediction[0][1]>prediction[0][0]:
                print('\033[91mGenuine Image\033[0m')
                return True
            else:
                print('\033[91mForged Image\033[0m')
                return False
def trainAndTest(rate=0.001, epochs=1700, neurons=7, display=False):    
    start = time()
    global training_rate, training_epochs, n_hidden_1
    learning_rate = rate
    training_epochs = epochs
    n_hidden_1 = neurons 
    n_hidden_2 = 7 
    n_hidden_3 = 30  
    train_avg, test_avg = 0, 0
    n = 10
    for i in range(1,n+1):00
    if display:
        print("Running for Person id",i)
        temp = ('0'+str(i))[-2:]
        train_score, test_score = evaluate(train_path.replace('01',temp), test_path.replace('01',temp))
        train_avg += train_score
        test_avg += test_score
    if display:
        print("Training average-", train_avg/n)
        print("Testing average-", test_avg/n)
        print("Time taken-", time()-start)
    return train_avg/n, test_avg/n, (time()-start)/n
evaluate(train_path, test_path, type2=True)