from __future__ import print_function

#!/usr/bin/env python
# Example script for recurrent network usage in PyBrain.
__author__ = "Martin Felder"
__version__ = '$Id$'

import common
import pickle
import numpy as np
from pylab import plot, hold, show
from scipy import sin, rand, arange
from sklearn.metrics import confusion_matrix
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.tools.validation    import testOnSequenceData
from sklearn.neighbors  		 import KNeighborsClassifier
from pylab import figure, ioff, clf, contourf, ion, draw, show
from pybrain.structure.modules   import LSTMLayer, SoftmaxLayer
from pybrain.datasets            import SequenceClassificationDataSet
from pybrain.supervised          import RPropMinusTrainer,BackpropTrainer
from sklearn.cross_validation 	 import train_test_split,StratifiedKFold
from os.path import exists
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader

from sklearn.metrics import precision_score,recall_score,accuracy_score,f1_score,roc_auc_score


# create training and test data
DS = common.generate_ucf_dataset('frames')
X, y = DS


precision= []
recall   = []
f1       = []
accuracy = []
stf = StratifiedKFold(y, n_folds=10)
for train_index, test_index in stf:    
    X_train = []
    X_test  = []
    y_train = []
    y_test  = []

    for x in train_index:
        X_train.append(X[x])
        y_train.append(y[x])

    for x in test_index:
        X_test.append(X[x])
        y_test.append(y[x])
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.3)

    trndata = SequenceClassificationDataSet(100,1, nb_classes=2)
    tstdata = SequenceClassificationDataSet(100,1, nb_classes=2)

    for index in range(len(y_train)):
    	trndata.addSample(X_train[index], y_train[index])

    for index in range(len(y_test)):
    	tstdata.addSample(X_test[index], y_test[index])

    trndata._convertToOneOfMany( bounds=[0.,1.] )
    tstdata._convertToOneOfMany( bounds=[0.,1.] )

    if exists("params.xml"):
        rnn = NetworkReader.readFrom('params.xml')
    else:
        # construct LSTM network - note the missing output bias
        rnn = buildNetwork( trndata.indim, 5, trndata.outdim, hiddenclass=LSTMLayer, outclass=SoftmaxLayer, outputbias=False, recurrent=True)

    # define a training method
    #trainer = RPropMinusTrainer( rnn, dataset=trndata, verbose=True )
    # instead, you may also try
    trainer = BackpropTrainer( rnn, dataset=trndata, momentum=0.1, weightdecay=0.01)

    # carry out the training
    for i in range(100):
        trainer.trainEpochs( 2 )
        trnresult = (1.0-testOnSequenceData(rnn, trndata))
        tstresult = (1.0-testOnSequenceData(rnn, tstdata))
        #print("train error: %5.2f%%" % trnresult, ",  test error: %5.2f%%" % tstresult)

        out = rnn.activate(X_train[0])
        out = out.argmax(axis=0)

    index=0
    result = []
    for x in X_test:
    	result.append(rnn.activate(x).argmax())

    mresult = confusion_matrix(y_test,result)
    precision.append((precision_score(y_test,result)))
    recall.append((recall_score(y_test,result)))
    f1.append((f1_score(y_test,result)))
    accuracy.append((accuracy_score(y_test,result)))

    # saving the params
    NetworkWriter.writeToFile(rnn, 'params.xml')

    
        

print ("precision %4.2f,%4.2f"%(np.mean(precision),np.std(precision)))
print ("recall    %4.2f,%4.2f"%(np.mean(recall),np.std(recall)))
print ("f1        %4.2f,%4.2f"%(np.mean(f1),np.std(f1)))
print ("accuracy  %4.2f,%4.2f"%(np.mean(accuracy),np.std(accuracy)))

