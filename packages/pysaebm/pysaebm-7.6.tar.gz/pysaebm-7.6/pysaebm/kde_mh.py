import numpy as np
import pandas as pd
import pysaebm.kde_utils as kde_utils
import pysaebm.utils as data_utils
from typing import List, Dict, Tuple
import logging

def metropolis_hastings_kde(
        data_we_have: pd.DataFrame,
        iterations: int,
        n_shuffle: int,
        burn_in:int,
        rng:np.random.Generator
) -> Tuple[np.ndarray, List[float], Dict[str, Dict], np.ndarray]:
    """
    Perform Metropolis-Hastings sampling with conjugate priors to estimate biomarker orderings.

    Args:
        data_we_have (pd.DataFrame): Raw participant data.
        iterations (int): Number of iterations for the algorithm.
        n_shuffle (int): Number of swaps to perform when shuffling the order.
        seed (int): for reproducibility

    Returns:
        Tuple[List[Dict], List[float], Dict[str, Dict], Dict[int, np.ndarray]]: 
            - List of accepted biomarker orderings at each iteration.
            - List of log likelihoods at each iteration.
            - Final theta phi estimates
            - Stage likelihood posterior 
    """
    best_ll = -np.inf
    best_order = None 
    best_theta_phi = None 
    best_stage_post = None 
    best_stage_prior = None 
    
    biomarkers = sorted(data_we_have.biomarker.unique())
    n_stages = len(biomarkers) + 1
    disease_stages = np.arange(start=1, stop=n_stages, step=1)
    n_disease_stages = n_stages - 1
    non_diseased_ids = data_we_have.loc[data_we_have.diseased ==
                                        False].participant.unique()
    diseased_ids = data_we_have.loc[data_we_have.diseased ==
                                        True].participant.unique()
    
    theta_phi_default = kde_utils.get_initial_kde_estimates(data_we_have, rng)
    current_theta_phi = theta_phi_default.copy()

    # initialize an ordering and likelihood
    current_order = rng.permutation(np.arange(1, n_stages))
    current_order_dict = dict(zip(biomarkers, current_order))
    current_ln_likelihood = -np.inf
    alpha_prior = np.array([1.0] * (n_disease_stages))
    # current_pi is the prior distribution of N disease stages.
    # Sample from uniform dirichlet dist.
    current_pi = rng.dirichlet(alpha_prior)
    # current_stage_post = {}
    acceptance_count = 0

    # Note that this records only the current accepted orders in each iteration
    all_accepted_orders = []
    # This records all log likelihoods
    log_likelihoods = []

    for iteration in range(iterations):
        log_likelihoods.append(current_ln_likelihood)

        new_order = current_order.copy()
        data_utils.shuffle_order(new_order, n_shuffle, rng)
        new_order_dict = dict(zip(biomarkers, new_order))

        """
        When we propose a new ordering, we want to calculate the total ln likelihood, which is 
        dependent on theta_phi_estimates, which are dependent on biomarker_data and stage_likelihoods_posterior,
        both of which are dependent on the ordering. 

        Therefore, we need to update participant_data, biomarker_data, stage_likelihoods_posterior
        and theta_phi_estimates before we can calculate the total ln likelihood associated with the new ordering
        """

        # Update participant data with the new order dict
        participant_data = kde_utils.preprocess_participant_data(data_we_have, new_order_dict)

        biomarker_data = kde_utils.preprocess_biomarker_data(data_we_have, new_order_dict)

        # --- Compute stage posteriors with OLD θ/φ ---
        # Only diseased participants have stage likelihoods
        _, stage_post_old = kde_utils.compute_total_ln_likelihood_and_stage_likelihoods(
            participant_data,
            non_diseased_ids,
            current_theta_phi,
            current_pi,
            disease_stages,
        )

        # Compute the new theta_phi_estimates based on new_order
        new_theta_phi = kde_utils.update_theta_phi_estimates(
            biomarker_data,
            current_theta_phi,  # Fallback uses current state’s θ/φ
            stage_post_old,
            disease_stages,
        )

        # NOTE THAT WE CANNOT RECOMPUTE P(K_J) BASED ON THIS NEW THETA PHI.
        # THIS IS BECAUSE IN MCMC, WE CAN ONLY GET NEW THINGS THAT ARE SOLELY CONDITIONED ON THE NEWLY PROPOSED S'

        # Recompute new_ln_likelihood using the new theta_phi_estimates
        new_ln_likelihood, stage_post_new = kde_utils.compute_total_ln_likelihood_and_stage_likelihoods(
            participant_data,
            non_diseased_ids,
            new_theta_phi,
            current_pi,
            disease_stages,
        )


        # Compute acceptance probability
        delta = new_ln_likelihood - current_ln_likelihood
        prob_accept = 1.0 if delta > 0 else np.exp(delta)

        # Accept or reject the new state
        if rng.random() < prob_accept:
            current_order = new_order
            current_order_dict = new_order_dict
            current_ln_likelihood = new_ln_likelihood
            # current_stage_post = stage_post_new
            current_theta_phi = new_theta_phi
            acceptance_count += 1

            stage_counts = np.zeros(n_disease_stages)
            # participant, array of stage likelihoods
            for p, stage_probs in stage_post_new.items():
                stage_counts += stage_probs  # Soft counts
            current_pi = rng.dirichlet(alpha_prior + stage_counts)

            if current_ln_likelihood > best_ll:
                best_ll = current_ln_likelihood
                best_order = current_order.copy()
                best_stage_prior = current_pi 
                # best_stage_post = current_stage_post
                best_theta_phi = current_theta_phi

        all_accepted_orders.append(current_order.copy())

        # Log progress
        if (iteration + 1) % max(10, iterations // 10) == 0:
            acceptance_ratio = 100 * acceptance_count / (iteration + 1)
            logging.info(
                f"Iteration {iteration + 1}/{iterations}, "
                f"Acceptance Ratio: {acceptance_ratio:.2f}%, "
                f"Log Likelihood: {current_ln_likelihood:.4f}, "
                f"Current Accepted Order: {current_order_dict.values()}, "
            )

    return all_accepted_orders, log_likelihoods, best_order, best_theta_phi, best_stage_prior
