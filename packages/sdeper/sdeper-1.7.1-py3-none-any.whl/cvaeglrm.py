#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 10 03:15:36 2022

@author: hill103

this script is the main function of the whole CVAE-GLRM pipeline

pipeline steps:
    
    1. receive and parse the command line parameters and then pass the parameters to CVAE-GLRM model
    2. pre-process
    3. building CVAE (if available)
    4. GLRM model fitting
    5. post-process and save the results
"""



def main():
    '''
    main function
    
    Parameters
    ----------
    None.

    Returns
    -------
    None.

    '''

    from config import print, cur_version, output_path
    import os
    os.environ['PYTHONHASHSEED'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    import warnings
    warnings.filterwarnings("ignore")
    
    
    print(f'\nSDePER (Spatial Deconvolution method with Platform Effect Removal) v{cur_version}\n')
    
    
    import pandas as pd
    from time import time
    from parse_opt import parseOpt
    from preprocess import preprocess
    from run_model import run_GLRM
    
    
    start_time = time()
    
    paramdict = parseOpt()
    
    
    # Configure a new global `tensorflow` session for reproductivity
    import tensorflow as tf
    tf.keras.utils.set_random_seed(paramdict['seed'])
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    session_conf = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=paramdict['n_cores'], inter_op_parallelism_threads=paramdict['n_cores'])
    sess = tf.compat.v1.Session(graph=tf.compat.v1.get_default_graph(), config=session_conf)
    tf.compat.v1.keras.backend.set_session(sess)
    
    
    print('\n\n######### Preprocessing... #########\n')
    data = preprocess(paramdict['spatial_file'], paramdict['ref_file'], paramdict['ref_celltype_file'], paramdict['marker_file'], paramdict['A_file'], paramdict['use_cvae'], paramdict['n_hv_gene'], paramdict['n_marker_per_cmp'], paramdict['n_pseudo_spot'], paramdict['pseudo_spot_min_cell'], paramdict['pseudo_spot_max_cell'], paramdict['seq_depth_scaler'], paramdict['cvae_input_scaler'], paramdict['cvae_init_lr'], paramdict['num_hidden_layer'], paramdict['use_batch_norm'], paramdict['cvae_train_epoch'], paramdict['use_spatial_pseudo'], paramdict['redo_de'], paramdict['use_fdr'], paramdict['p_val_cutoff'], paramdict['fc_cutoff'], paramdict['pct1_cutoff'], paramdict['pct2_cutoff'], paramdict['sortby_fc'], paramdict['filter_cell'], paramdict['filter_gene'], paramdict['diagnosis'])
    
    
    # whether to estimate gamma_g, if CVAE is used then disable gamma_g estimation
    if paramdict['use_cvae']:
        estimate_gamma_g = False
    else:
        estimate_gamma_g = True
    

    # release RAM before modeling
    #import gc
    #import psutil
    #print(f'before gc RAM usage: {psutil.Process().memory_info().rss/1024**2:.2f} MB')
    #gc.collect()
    #print(f'after gc RAM usage: {psutil.Process().memory_info().rss/1024**2:.2f} MB')
    
    
    result = run_GLRM(data, lambda_r=paramdict['lambda_r'], lambda_g=paramdict['lambda_g'], estimate_gamma_g=estimate_gamma_g, n_jobs=paramdict['n_cores'], threshold=paramdict['threshold'], diagnosis=paramdict['diagnosis'], verbose=paramdict['verbose'])
    
    
    # save result
    save_all = False
    
    if save_all:
        # save all related estimations to xlsx file
        output_file = os.path.join(output_path, 'celltype_proportions.xlsx')
        with pd.ExcelWriter(output_file) as writer:
            # theta
            pd.DataFrame(result['theta'], index=data['spot_names'], columns=data['celltype_names']).to_excel(writer, sheet_name='theta')
            pd.DataFrame(result['e_alpha'], index=data['spot_names'], columns=['e_alpha']).to_excel(writer, sheet_name='e_alpha')
            pd.DataFrame(result['gamma_g'], index=data['gene_names'], columns=['gamma_g']).to_excel(writer, sheet_name='gamma_g')
            pd.DataFrame([result['sigma2']], index=None, columns=['sigma2']).to_excel(writer, sheet_name='sigma2', index=False)
    else:
        # only save theta to a csv file
        output_file = os.path.join(output_path, 'celltype_proportions.csv')
        pd.DataFrame(result['theta'], index=data['spot_names'], columns=data['celltype_names']).to_csv(output_file)
        
    print(f'\n\ncell type deconvolution finished. Estimate results saved in {output_file}. Elapsed time: {(time()-start_time)/3600.0:.2f} hours.')
    
    
    # imputation
    if paramdict['use_imputation']:
        
        from imputation import do_imputation
        
        print('\n\n######### Start imputation #########')
        
        for x in paramdict['impute_diameter']:
            print(f'\n\nimputation for {x} µm ...')
            impute_start = time()
            # we now totally discard the transforming from integer coordinates to pixels
            # we use stepsize = impute_diameter / diameter inside imputation function
            result = do_imputation(paramdict['loc_file'], output_file, paramdict['spatial_file'], float(x)/paramdict['diameter'], paramdict['hole_min_spots'], paramdict['preserve_shape'], diagnosis=paramdict['diagnosis'])
            # return imputed spot locations, cell type proportions and gene expressions
            result[0].to_csv(os.path.join(output_path, f'impute_diameter_{x}_spot_loc.csv'))
            result[1].to_csv(os.path.join(output_path, f'impute_diameter_{x}_spot_celltype_prop.csv'))
            result[2].to_csv(os.path.join(output_path, f'impute_diameter_{x}_spot_gene_norm_exp.csv'))
            print(f'imputation for {x} µm finished. Elapsed time: {(time()-impute_start)/60.0:.2f} minutes')
        
    else:
        print('\n\n######### No imputation #########')
        
    print(f'\n\nwhole pipeline finished. Total elapsed time: {(time()-start_time)/3600.0:.2f} hours.')


if __name__ == '__main__':
    main()