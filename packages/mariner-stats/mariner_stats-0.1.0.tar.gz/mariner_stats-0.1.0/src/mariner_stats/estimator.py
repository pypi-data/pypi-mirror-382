# pkgs/mariner/src/mariner/estimator.py
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
import matplotlib.pyplot as plt
import seaborn as sns

from hiutils.core import (
    UniLasso, OLS,
    make_interactions, cv
)


class MARINER(BaseEstimator):
    """
    Two-stage regression with marginal selection and UniLasso on both main effects and interactions via CV.

    Parameters
    ----------
    lmda_path : array-like of shape (n_lmdas,)
        Path of the lambda values for UniLasso. If None, it will be generated using generate_lambda_path.   
    n_folds : int
        Number of folds for cross-validation.
    plot_cv_curve : bool  
        If true, plot the CV R2 against -log(λ)
    cv1se : bool 
        If true, use the one-standard error rule at CV. 
        
    Attributes
    ----------
    n_features\_ : int
        Number of features in the dataset.

    regressor\_ : UniLasso object
        Fitted regressor after cv.

    triplet_regressors\_ : dicts of OLS object
        OLS regressors per j<k for step 2

    selected_pairs\_ : array-like of shape (n_pairs, 2)
        selected interactions after scan 

    main_effects_active_set\_ : array-like
        Indices of the active set of main effects.

    n_folds\_ : int

    main_effects_names\_ : list of str

    interactions_names\_ : list of str

    cv_errors\_ : array-like of shape (n_folds, n_lmdas)

    lmda_path\_ : array-like
        lmda path for cv  

    plot_cv_curve\_ : bool
        If true, plot the CV R2 against -log(λ)

    cv1se\_ : bool 
        If true, use the one-standard error rule at CV. 

    """
    
    def __init__(self, lmda_path=None, n_folds=10, plot_cv_curve=False, cv1se=False):

        self.regressor_ = UniLasso(lmda_path=lmda_path)
        self.triplet_regressors_ = None
        
        self.n_folds_ = n_folds

        self.n_features_ = None
        self.main_effects_active_set_ = None
        self.selected_pairs_ = None

        self.main_effects_names_ = None
        self.interactions_names_ = None
        self.cv_errors = None
        self.lmda_path_ = None
        self.plot_cv_curve_ = plot_cv_curve
        self.cv1se_ = cv1se

    def fit_triplet_models(self,X, y):
        """
        Regress y on [X_j,X_k,X_j*X_k] with intercept for all j<k with intercept

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Design matrix.
        y : array-like of shape (n_samples,)
            Response vector.

        Returns
        -------
        None 
        """
        n, p = X.shape
        assert n>3
        assert p>1
        for j in range(p-1):
            for k in range(j+1,p):
                F = np.hstack([X[:,j:j+1],X[:,k:k+1],X[:,j:j+1]*X[:,k:k+1]])                                                  # (n_samples, 3)
                self.triplet_regressors_[j][k].fit(F,y)
    
    def scan_interactions(self, X, y):
        """
        Implements the screening procedure for the interactions.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Design matrix.
        y : array-like of shape (n_samples,)
            Response vector.
    
        Returns
        -------
        None
        """

        _, n_features = X.shape

        assert self.triplet_regressors_ is not None 
        scan_coefs = np.zeros((n_features,n_features))
        pvals = np.ones((n_features,n_features))
        for j in range(n_features-1):
            for k in range(j+1,n_features):
                pvals[j,k] = self.triplet_regressors_[j][k].p_value_t_test_[-1]
                scan_coefs[j,k] = np.abs(self.triplet_regressors_[j][k].slopes_[-1])
        

        pvals_ea = {(j,k):self.triplet_regressors_[j][k].p_value_t_test_[-1] for j in range(n_features-1) for k in range(j+1,n_features)}
        
        # point that best separates the two clusters 
        pvals_ea_sorted = sorted(pvals_ea.items(),key=lambda x: x[1],reverse=False) # ascending order 
        num_zeros_ea = len(pvals_ea_sorted) - len([pval for _,pval in pvals_ea_sorted if pval>1e-20])
        tmp = [pval for _,pval in pvals_ea_sorted if pval>1e-20]
        # forcing strong hierarchy 
        if len(tmp)<=1 : 
            selected_pairs_ea = [pair for (pair,_) in pvals_ea_sorted]
        else : 
            tmp = np.log(np.array(tmp)) # need to investigate why taking log of pvalues does better than using their raw value
            i_tmp = np.argmax(tmp[1:]-tmp[:-1]) + num_zeros_ea
            selected_pairs_ea = [pair for (pair,_) in pvals_ea_sorted[:i_tmp+1]]

        if self.plot_cv_curve_ : 
            
            mask = np.triu(np.ones_like(pvals, dtype=bool), k=1)
            pv = pvals[mask]
            plt.figure(figsize=(8, 5))
            plt.hist(pv, bins=int(len(pv)/20), edgecolor='black')

            sel_pv = [pvals[j,k] for j,k in selected_pairs_ea]
            plt.scatter(sel_pv, np.zeros_like(sel_pv), color='orange', s=50,label='selected pairs', zorder=10)

            plt.xlabel('p-value')
            plt.ylabel('Count')
            plt.legend()
            plt.tight_layout()
            plt.show()

            mask = np.tril(np.ones_like(pvals, dtype=bool), k=0)
            plt.figure(figsize=(8, 8))
            ax = sns.heatmap(
                pvals,
                mask=mask,
                cmap='viridis',
                xticklabels=self.main_effects_names_,
                yticklabels=self.main_effects_names_,
                vmin=0,
                vmax=1,
                square=True,
                cbar_kws={"shrink": .8}
            )
            ax.set_facecolor('white')
            for j, k in selected_pairs_ea:
                ax.text(k + 0.5,j + 0.5,'★',ha='center', va='center',color='white',fontsize=16,zorder=10)
            plt.tight_layout()
            plt.show()

        self.selected_pairs_ = np.array(selected_pairs_ea)
        
    def fit(self, X, y, lmda_path=None, tolerance=1e-10):
        """
        Fit the two-stage regression model with interactions.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Design matrix.
        y : array-like of shape (n_samples,)
            Response vector.

        Returns
        -------
        None
        """
        
        X, y = check_X_y(X, y, y_numeric=True)
        _, n_features = X.shape
        self.n_features_ = n_features
        self.main_effects_names_ = [f'X{j}' for j in range(n_features)]
        self.triplet_regressors_  = {j:{k:OLS(vars_names=[f'X{j}',f'X{k}',f'X{j}*X{k}']) for k in range(j+1,n_features)} for j in range(n_features-1)}
        if n_features > 1 : 
            self.fit_triplet_models(X, y)
            self.scan_interactions(X,y)
            interactions_X, self.interactions_names_ = make_interactions(X, self.selected_pairs_)                               # (n_samples, n_pairs)
            full_X = np.hstack([X,interactions_X])
        else :
            full_X = X
            self.interactions_names_ = []


        self.regressor_.set_vars_names(self.main_effects_names_+self.interactions_names_)
        cv_results = cv(
            base=self.regressor_,
            X=full_X,
            y=y,
            n_folds=self.n_folds_,
            lmda_path=lmda_path,
            plot_cv_curve=self.plot_cv_curve_,
            cv1se=self.cv1se_
        ) # self.regressor_ is fited in-place after CV
        self.lmda_path_ = cv_results['lmda_path']
        self.cv_errors_ = cv_results['cv_errors']
        main_effects_slopes = self.regressor_.slopes_[:1,:n_features]                                                           # (1, n_features)
        interactions_slopes = self.regressor_.slopes_[:1,n_features:]                                                           # (1, n_pairs)
        self.main_effects_active_set_ = np.where(np.abs(main_effects_slopes) > tolerance)[1] 
        self.interactions_active_set_ = np.where(np.abs(interactions_slopes) > tolerance)[1] 

    def get_active_variables(self):
        """
        Get the names of the active variables for the fitted model.
        This includes both main effects and interactions.

        Parameters
        ----------
        None

        Returns
        -------
        active_vars : list of str
            List of names of the active variables.
        """
        check_is_fitted(self.regressor_)
        
        active_vars = []
        
        for i in self.main_effects_active_set_:
            active_vars.append(self.main_effects_names_[i])
    
        if self.n_features_>1:
            for i in self.interactions_active_set_:
                active_vars.append(self.interactions_names_[i])

        return active_vars
    
    def get_fitted_function(self, tolerance=1e-10):
        """
        Get the fitted model string representation.

        Parameters
        ----------
        None

        Returns
        -------
        fitted_model_rep : str
            string representation of the fitted model
        """
        check_is_fitted(self.regressor_)
        
        return self.regressor_.get_fitted_function(self.regressor_.lmda_path_[0],tolerance) 
         
    def predict(self, X):
        """
        Predict using the two-stage regression model with interactions.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Design matrix.

        Returns
        -------
        y_pred : array-like of shape (n_samples,)
            Predicted values using the two-stage regression model.
        """
        check_is_fitted(self.regressor_)
        
        X = check_array(X)

        if self.n_features_>1:
            interactions_X, _ = make_interactions(X,self.selected_pairs_)
            full_X = np.hstack([X,interactions_X])
        else : 
            full_X = X

        return self.regressor_.predict(full_X)[:,0]                                                                             # (n_samples, )
    