# pkgs/hireg/src/hireg/estimator.py
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

from hiutils.core import (
    UniLasso, Lasso, OLS,
    make_interactions, cv
)


class HIREG(BaseEstimator):
    """
    Two-stage regression (UniLasso + Lasso) with interactions using 2D cross-validation.

    Parameters
    ----------
    hierarchy : {'strong','weak',None}
        Hierarchy constraint for interaction selection.
    lmda_path_main_effects : array-like of shape (n_lmdas,)
        Path of the lambda values for main effects. If None, it will be generated using generate_lambda_path.
    lmda_path_interactions : array-like of shape (n_lmdas,)
        Path of the lambda values for interactions. If None, it will be generated using generate_lambda_path.
    n_folds_main_effects : int
        Number of folds for cross-validation for main effects.
    n_folds_interactions : int
        Number of folds for cross-validation for interactions.
    plot_cv_curve : bool
    cv1se : bool

    Attributes
    ----------
    n_features_ : int
    main_effects_regressor_ : UniLasso
    interactions_regressor_ : Lasso
    triplet_regressors_ : dict of dict of OLS
    selected_pairs_ : array-like of shape (n_pairs, 2)
    prevalidated_preds_ : array-like of shape (n_samples,)
    main_effects_active_set_ : array-like
    n_folds_main_effects_ : int
    n_folds_interactions_ : int
    main_effects_names_ : list of str
    interactions_names_ : list of str
    stage1_cv_errors_ : array-like of shape (n_folds, n_lmdas)
    stage2_cv_errors_ : array-like of shape (n_folds, n_lmdas)
    lmda_path_main_effects_ : array-like
    lmda_path_interactions_ : array-like
    plot_cv_curve_ : bool
    cv1se_ : bool
    hierarchy_ : str
    """

    def __init__(
        self,
        hierarchy=None,
        lmda_path_main_effects=None,
        lmda_path_interactions=None,
        n_folds_main_effects=10,
        n_folds_interactions=10,
        plot_cv_curve=False,
        cv1se=False,
    ):
        """
        Two-stage regression (UniLasso + Lasso) with interactions using 2D cross-validation.

        Parameters
        ----------
        hierarchy : {'strong','weak',None}
            Hierarchy constraint for interaction selection.
        lmda_path_main_effects : array-like of shape (n_lmdas,)
            Path of the lambda values for main effects. If None, it will be generated using generate_lambda_path.
        lmda_path_interactions : array-like of shape (n_lmdas,)
            Path of the lambda values for interactions. If None, it will be generated using generate_lambda_path.
        n_folds_main_effects : int
            Number of folds for cross-validation for main effects.
        n_folds_interactions : int
            Number of folds for cross-validation for interactions.
        plot_cv_curve : bool
        cv1se : bool

        Attributes
        ----------
        n_features_ : int
        main_effects_regressor_ : UniLasso
        interactions_regressor_ : Lasso
        triplet_regressors_ : dict of dict of OLS
        selected_pairs_ : array-like of shape (n_pairs, 2)
        prevalidated_preds_ : array-like of shape (n_samples,)
        main_effects_active_set_ : array-like
        n_folds_main_effects_ : int
        n_folds_interactions_ : int
        main_effects_names_ : list of str
        interactions_names_ : list of str
        stage1_cv_errors_ : array-like of shape (n_folds, n_lmdas)
        stage2_cv_errors_ : array-like of shape (n_folds, n_lmdas)
        lmda_path_main_effects_ : array-like
        lmda_path_interactions_ : array-like
        plot_cv_curve_ : bool
        cv1se_ : bool
        hierarchy_ : str
        """
        if hierarchy not in (None, "weak", "strong"):
            raise ValueError("hierarchy must be one of None, 'weak', or 'strong'.")

        self.main_effects_regressor_ = UniLasso(lmda_path=lmda_path_main_effects)
        self.interactions_regressor_ = Lasso(lmda_path=lmda_path_interactions)
        self.triplet_regressors_ = None

        self.n_folds_main_effects_ = n_folds_main_effects
        self.n_folds_interactions_ = n_folds_interactions

        self.n_features_ = None
        self.main_effects_active_set_ = None
        self.prevalidated_preds_ = None
        self.selected_pairs_ = None

        self.main_effects_names_ = None
        self.interactions_names_ = None
        self.stage1_cv_errors = None
        self.stage2_cv_errors_ = None
        self.lmda_path_main_effects_ = None
        self.lmda_path_interactions_ = None
        self.plot_cv_curve_ = plot_cv_curve
        self.cv1se_ = cv1se
        self.hierarchy_ = hierarchy

    def regress_main_effects(self, X, y, lmda_path=None, tolerance=1e-10):
        """
        Fit the main effects model using cross-validation.
        """
        X, y = check_X_y(X, y, y_numeric=True)

        self.main_effects_names_ = [f"X{i}" for i in range(self.n_features_)]
        self.main_effects_regressor_.set_vars_names(self.main_effects_names_)
        cv_results = cv(
            base=self.main_effects_regressor_,
            X=X,
            y=y,
            n_folds=self.n_folds_main_effects_,
            lmda_path=lmda_path,
            plot_cv_curve=self.plot_cv_curve_,
            cv1se=self.cv1se_,
        )  # self.main_effects_regressor_ is fitted in-place after CV
        self.lmda_path_main_effects_ = cv_results["lmda_path"]
        self.stage1_cv_errors_ = cv_results["cv_errors"]
        self.prevalidated_preds_ = cv_results["prevalidated_preds"]                                                         # (n_samples, )
        main_effects_slopes = self.main_effects_regressor_.slopes_                                                          # (1, n_features)
        self.main_effects_active_set_ = np.where(np.abs(main_effects_slopes) > tolerance)[1]
 
    def fit_triplet_models(self, X, y):
        """
        Regress y on [X_j, X_k, X_j*X_k] with intercept for all j<k.
        """
        n, p = X.shape
        if not (n > 3):
            raise ValueError("Need at least 4 samples to fit triplet OLS models.")
        for j in range(p - 1):
            for k in range(j + 1, p):
                F = np.hstack([X[:, j : j + 1], X[:, k : k + 1], X[:, j : j + 1] * X[:, k : k + 1]])                        # (n, 3)
                self.triplet_regressors_[j][k].fit(F, y)

    def regress_interactions(self, X, y, lmda_path=None, tolerance=1e-10):
        """
        Fit stage 2 of the interactions model using cross-validation.
        """
        X, y = check_X_y(X, y, y_numeric=True)
        _, n_features = X.shape
        check_is_fitted(self.main_effects_regressor_)

        if self.triplet_regressors_ is None:
            raise RuntimeError("triplet_regressors_ not initialized. Call fit_triplet_models first.")

        scan_coefs = np.zeros((n_features, n_features))
        pvals = np.ones((n_features, n_features))
        for j in range(n_features - 1):
            for k in range(j + 1, n_features):
                pvals[j, k] = self.triplet_regressors_[j][k].p_value_t_test_[-1]
                scan_coefs[j, k] = np.abs(self.triplet_regressors_[j][k].slopes_[-1])

        # hierarchy handling
        active = set(self.main_effects_active_set_) if self.main_effects_active_set_ is not None else set()
        if len(active) == 0:
            self.hierarchy_ = None
            warnings.warn(
                "no main effects found. Dropping the hierarchy constraint",
                category=UserWarning,
                stacklevel=2,
            )
        if self.hierarchy_ == "strong":
            pvals_ea = {(j, k): self.triplet_regressors_[j][k].p_value_t_test_[-1]
                        for j in range(n_features - 1) for k in range(j + 1, n_features)
                        if (j in active and k in active)}
        elif self.hierarchy_ == "weak":
            pvals_ea = {(j, k): self.triplet_regressors_[j][k].p_value_t_test_[-1]
                        for j in range(n_features - 1) for k in range(j + 1, n_features)
                        if (j in active or k in active)}
        elif self.hierarchy_ is None:
            pvals_ea = {(j, k): self.triplet_regressors_[j][k].p_value_t_test_[-1]
                        for j in range(n_features - 1) for k in range(j + 1, n_features)}
        else:
            raise ValueError("incorrect value for hierarchy")

        # threshold by the biggest log-gap heuristic
        pvals_ea_sorted = sorted(pvals_ea.items(), key=lambda x: x[1], reverse=False)  # ascending order
        num_zeros_ea = len(pvals_ea_sorted) - len([pval for _, pval in pvals_ea_sorted if pval > 1e-20])
        tmp = [pval for _, pval in pvals_ea_sorted if pval > 1e-20]
        if len(tmp) <= 1:
            selected_pairs_ea = [pair for (pair, _) in pvals_ea_sorted]
        else:
            tmp = np.log(np.array(tmp))  # works better than raw p-values
            i_tmp = np.argmax(tmp[1:] - tmp[:-1]) + num_zeros_ea
            selected_pairs_ea = [pair for (pair, _) in pvals_ea_sorted[: i_tmp + 1]]

        if self.plot_cv_curve_:
            mask = np.triu(np.ones_like(pvals, dtype=bool), k=1)
            pv = pvals[mask]
            plt.figure(figsize=(8, 5))
            plt.hist(pv, bins=int(len(pv) / 20), edgecolor="black")

            sel_pv = [pvals[j, k] for j, k in selected_pairs_ea]
            plt.scatter(sel_pv, np.zeros_like(sel_pv), color="orange", s=50, label="selected pairs", zorder=10)

            plt.xlabel("p-value")
            plt.ylabel("Count")
            plt.legend()
            plt.tight_layout()
            plt.show()

            mask = np.tril(np.ones_like(pvals, dtype=bool), k=0)
            plt.figure(figsize=(8, 8))
            ax = sns.heatmap(
                pvals,
                mask=mask,
                cmap="viridis",
                xticklabels=self.main_effects_names_,
                yticklabels=self.main_effects_names_,
                vmin=0,
                vmax=1,
                square=True,
                cbar_kws={"shrink": 0.8},
            )
            ax.set_facecolor("white")
            for j, k in selected_pairs_ea:
                ax.text(k + 0.5, j + 0.5, "★", ha="center", va="center", color="white", fontsize=16, zorder=10)
            plt.tight_layout()
            plt.show()

        self.selected_pairs_ = np.array(selected_pairs_ea)

        stage2_X, self.interactions_names_ = make_interactions(X, self.selected_pairs_)                                      # (n_samples, n_pairs)
        stage2_y = y - self.prevalidated_preds_  # (n_samples, )

        self.interactions_regressor_.set_vars_names(self.interactions_names_)                                                # list of str
        cv_results = cv(
            base=self.interactions_regressor_,
            X=stage2_X,
            y=stage2_y,
            n_folds=self.n_folds_interactions_,
            lmda_path=lmda_path,
            plot_cv_curve=self.plot_cv_curve_,
            cv1se=False,
        )
        self.lmda_path_interactions_ = cv_results["lmda_path"]
        self.stage2_cv_errors_ = cv_results["cv_errors"]
        stage2_slopes = self.interactions_regressor_.slopes_                                                                  # (1, n_pairs)

        self.interactions_active_set_ = np.where(np.abs(stage2_slopes) > tolerance)[1]

    def fit(self, X, y):
        """
        Fit the two-stage regression model with interactions.
        """
        X, y = check_X_y(X, y, y_numeric=True)
        _, n_features = X.shape
        self.n_features_ = n_features
        self.triplet_regressors_ = {
            j: {k: OLS(vars_names=[f"X{j}", f"X{k}", f"X{j}*X{k}"]) for k in range(j + 1, n_features)}
            for j in range(n_features - 1)
        }
        self.regress_main_effects(X, y)
        if n_features == 1:
            return
        self.fit_triplet_models(X, y)
        self.regress_interactions(X, y)

    def get_active_variables(self):
        """
        Get the names of the active variables for the fitted model (mains + interactions).
        """
        check_is_fitted(self.main_effects_regressor_)
        check_is_fitted(self.interactions_regressor_)

        active_vars = []

        for i in self.main_effects_active_set_:
            active_vars.append(self.main_effects_names_[i])

        if self.n_features_ > 1:
            for i in self.interactions_active_set_:
                active_vars.append(self.interactions_names_[i])

        return active_vars

    def get_fitted_function(self, tolerance=1e-10):
        """
        Get the fitted model string representation.
        """
        check_is_fitted(self.main_effects_regressor_)
        check_is_fitted(self.interactions_regressor_)

        fitted_model_rep = (
            self.main_effects_regressor_.get_fitted_function(self.main_effects_regressor_.lmda_path_[0], tolerance)
            + " + "
        )
        if self.n_features_ > 1:
            fitted_model_rep = (
                fitted_model_rep
                + self.interactions_regressor_.get_fitted_function(
                    self.interactions_regressor_.lmda_path_[0], tolerance
                )
            )
        return fitted_model_rep

    def predict(self, X):
        """
        Predict using the two-stage regression model with interactions.

        Returns
        -------
        y_pred : array-like of shape (n_samples,)
        """
        check_is_fitted(self.main_effects_regressor_)
        check_is_fitted(self.interactions_regressor_)

        X = check_array(X)

        # stage 1
        y1_pred = self.main_effects_regressor_.predict(X)[:, 0]  # (n_samples, )

        # stage 2
        y2_pred = 0
        if self.n_features_ > 1:
            stage2_X, _ = make_interactions(X, self.selected_pairs_)
            y2_pred = self.interactions_regressor_.predict(stage2_X)[:, 0]                                                  # (n_samples, )

        return y1_pred + y2_pred
  