import os
import sys
import time

import numpy
import cPickle as pickle
import theano
import theano.tensor as T
from theano.tensor.signal import downsample
from theano.tensor.nnet import conv

from logistic_sgd import LogisticRegression, load_data
from mlp import HiddenLayer
from loadHITS import *

class ChunkLoader():
    def __init__(self, folder, n_cand_chunk, batch_size, n_rot = 3):
	self.files = [i for i in os.listdir(folder) if i[:5]=='chunk']
        self.files.sort()
	self.current_file = 0
	self.batch_i = 0
        self.folder = folder
        self.n_cand_chunk = n_cand_chunk
        self.batch_size = batch_size
	self.current_file_data = []
        self.current_file_data.append(np.load(self.folder + self.files[self.current_file]))# 0 deg
        self.current_file_data.append(np.load(self.folder + '90_'+self.files[self.current_file]))# 90 deg
        self.current_file_data.append(np.load(self.folder + '180_'+self.files[self.current_file]))# 180 deg
        self.current_file_data.append(np.load(self.folder + '270_'+self.files[self.current_file]))# 270 deg
        self.lastSNRs = []
        self.done = False
        #self.n_rot = n_rot
        
    def normalizeImage(self, im):
	return 1. * (im - im.min())/(im.max() - im.min())
	
    def normalizeSet(self, data):
	for i in range(len(data)):
	    data[i] = self.normalizeImage(data[i])
	return data

    def current_minibatch_SNR(self):
        return self.lastSNRs
    
    def nextFile (self):
	self.batch_i = 0
	self.current_file = (self.current_file+1)%len(self.files)
        self.current_file_data = []
        self.current_file_data.append(np.load(self.folder + self.files[self.current_file]))# 0 deg
        self.current_file_data.append(np.load(self.folder + '90_'+self.files[self.current_file]))# 90 deg
        self.current_file_data.append(np.load(self.folder + '180_'+self.files[self.current_file]))# 180 deg
        self.current_file_data.append(np.load(self.folder + '270_'+self.files[self.current_file]))# 270 deg
        if self.current_file == 0:
            self.done = True
            
    def getNext(self, normalize=True):
	print self.current_file, self.batch_i, self.files[self.current_file]
	keys = ['temp_images', 'sci_images', 'diff_images', 'SNR_images']

	#N = len(train_pkl['labels'])
        self.lastSNRs = self.current_file_data[0]['SNRs'][self.batch_i:self.batch_i+self.batch_size]
	data_all_rots = []
        for rot in self.current_file_data:
            data = []
	    for k in keys:
	        temp = rot[k][self.batch_i:self.batch_i+self.batch_size]
	        if normalize:
	            temp = self.normalizeSet(temp)
	            data.append(temp)
            
	    data = np.array(data, dtype = "float32")
	    data = np.swapaxes(data, 0, 1)
	    s = data.shape
	    data = data.flatten().reshape((s[0], s[1]*s[2]))
            data_all_rots.append(data)
        data_all_rots = np.concatenate(data_all_rots, axis=0)
	labels = np.array(self.current_file_data[0]['labels'][self.batch_i:self.batch_i+self.batch_size], dtype="int32")
	train_set = [data_all_rots, labels]
	self.batch_i += self.batch_size
        if train_set[0].shape[0] < self.batch_size*4:
            print "ERROR: ", self.folder + self.files[self.current_file], " has ", train_set[0].shape[0]/4.0, " candidates."
            self.nextFile()
            return self.getNext (normalize)

	if self.batch_i+self.batch_size>self.n_cand_chunk:
            self.nextFile()

	return train_set
	    
if __name__=="__main__":
    c = ChunkLoader('/home/shared/Fields_12-2015/chunks_feat_50000/chunks_train/', 50000, 50000, n_rot=0)
    n_epochs = 3
    for e in np.arange(n_epochs):
        print "e = ", e
        total = 0
        while not c.done:
	    x,y = c.getNext()
            total += len(y)
	    print e, total, x.shape, y.shape
            sys.stdout.flush()
            break
        break
        c.done = False
