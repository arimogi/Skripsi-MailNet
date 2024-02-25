import numpy as np
import pandas as pd
from tqdm import trange
from sktime.performance_metrics.forecasting import \
    mean_absolute_error

def compute_mae_error(y, bm_preds, flag):
    loss_df = pd.DataFrame()
    for i in trange(bm_preds.shape[1], desc=f'[Compute Error {flag}]'):
        model_mae_loss = [mean_absolute_error(y[j], bm_preds[j, i, :], symmetric=True) for j in range(len(y))]
        loss_df[i] = model_mae_loss
    return loss_df

def load_data_rl(root):
    input_data = np.load(f'{root}input.npz', allow_pickle=True)
    train_X = input_data['train_X']
    valid_X = input_data['valid_X']
    test_X  = input_data['test_X' ]
    train_y  = input_data['train_y' ]
    valid_y  = input_data['valid_y' ]
    test_y  = input_data['test_y' ]
    train_error = input_data['train_error'] 
    valid_error = input_data['valid_error']  
    test_error  = input_data['test_error' ]  
    return (train_X, valid_X, test_X, train_y, valid_y, test_y,
            train_error, valid_error, test_error)

def unify_input_data(args):
    train_X   = np.load(f'{args.root_path}train_X.npy', allow_pickle=True)
    valid_X   = np.load(f'{args.root_path}valid_X.npy', allow_pickle=True)
    test_X    = np.load(f'{args.root_path}test_X.npy', allow_pickle=True)         
    # test_y    = np.load(f'{args.root_path}test_y.npy', allow_pickle=True)  

    train_y = train_X.reshape(train_X.shape[0] * train_X.shape[1],-1) 
    valid_y = valid_X.reshape(valid_X.shape[0] * valid_X.shape[1],-1)  
    test_y  = test_X.reshape(valid_X.shape[0] * valid_X.shape[1],-1)

    # predictions
    MODEL_LEARNER = [f"learner{i+1}" for i in range(args.n_learner)]

    bm_train_preds = np.load(f'{args.root_path}bm_train_preds.npz', allow_pickle=True)
    bm_valid_preds = np.load(f'{args.root_path}bm_valid_preds.npz', allow_pickle=True)
    bm_test_preds = np.load(f'{args.root_path}bm_test_preds.npz', allow_pickle=True)

    merge_train = [np.expand_dims(bm_train_preds[model_name], axis=1) for model_name in MODEL_LEARNER]
    merge_valid = [np.expand_dims(bm_valid_preds[model_name], axis=1) for model_name in MODEL_LEARNER]
    merge_test = [np.expand_dims(bm_test_preds[model_name], axis=1) for model_name in MODEL_LEARNER]

    train_preds = np.concatenate(merge_train, axis=1)
    valid_preds = np.concatenate(merge_valid, axis=1)
    test_preds = np.concatenate(merge_test, axis=1)

    np.save(f'{args.root_path}bm_train_preds_new.npy', train_preds)
    np.save(f'{args.root_path}bm_valid_preds_new.npy', valid_preds)
    np.save(f'{args.root_path}bm_test_preds_new.npy', test_preds)

    train_error_df = compute_mae_error(train_y, train_preds, "TRAIN")
    valid_error_df = compute_mae_error(valid_y, valid_preds, "VALIDATION")
    test_error_df = compute_mae_error(test_y, test_preds, "TEST")

    np.savez(f'{args.root_path}input.npz',
             train_X=train_X,
             valid_X=valid_X,
             test_X=test_X,
             train_y=train_y,
             valid_y=valid_y,
             test_y=test_y,
             train_error=train_error_df,
             valid_error=valid_error_df,
             test_error=test_error_df
            )