import sys
import numpy as np
import pylab as pl

train = np.load (sys.argv[1] + "/training_buffer_history.pkl")
valid = np.load (sys.argv[1] + "/validation_history.pkl")

i_tr = np.array(train['iter_train_buf_history'])
e_tr = np.array(train['train_buf_err_history'])

i_val = valid['iter_val_history']
e_val = valid['val_err_history']

pl.clf()
#pl.plot (i_tr[crit], e_tr[crit], label = "Training set")
pl.plot (i_tr, e_tr, label = "Training set")
pl.plot (i_val, e_val, label = "Validation set")
pl.ylim([0, 0.02])
pl.show()
#pl.savefig (sys.argv[1] + "/learning_history")

assert len(i_val)==len(i_tr)

overfit = np.divide((e_val-e_tr), e_tr)
pl.plot(i_tr, overfit)
pl.show()