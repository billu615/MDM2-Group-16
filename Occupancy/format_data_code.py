import pandas as pd
import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt

def generate_fake_data(n_sites=72, n_years=24):
    np.random.seed(42)
    
    # Generate site IDs
    site_ids = np.repeat(np.arange(1, n_sites + 1), n_years)
    
    # Generate survey years
    survey_years = np.tile(np.arange(2000, 2000 + n_years), n_sites)
    
    # Simulate pesticide exposure and species presence data
    pesticide_exposure = np.random.uniform(0, 1, size=n_sites * n_years)
    
    bombus_presence = np.random.choice([0, 1], size=n_sites * n_years)
    apis_presence = np.random.choice([0, 1], size=n_sites * n_years)
    solitary_presence = np.random.choice([0, 1], size=n_sites * n_years)
    
    # Create DataFrame
    data = pd.DataFrame({
        'site_id': site_ids,
        'survey_year': survey_years,
        'bombus_presence': bombus_presence,
        'apis_presence': apis_presence,
        'solitary_presence': solitary_presence,
        'pesticide_exposure': pesticide_exposure
    })
    
    return data

def run_bayesian_model(data):
    # Data for species presence and pesticide exposure
    y_species_1 = data['bombus_presence'].values
    y_species_2 = data['apis_presence'].values
    y_species_3 = data['solitary_presence'].values

    X_neonic = data['pesticide_exposure'].values
    X_year = data['survey_year'].values
    X_habitat = np.random.uniform(0, 1, size=data.shape[0])

    site_ids = data['site_id'].values

    with pm.Model() as model:
        # Priors
        sigma = pm.HalfNormal('sigma', sigma=1)

        # Coefficients for each species
        beta_intercept_1 = pm.Normal('beta_intercept_1', mu=0, sigma=sigma)
        beta_neonic_1 = pm.Normal('beta_neonic_1', mu=0, sigma=sigma)
        beta_year_1 = pm.Normal('beta_year_1', mu=0, sigma=sigma)
        beta_habitat_1 = pm.Normal('beta_habitat_1', mu=0, sigma=sigma)

        # Same for other species
        beta_intercept_2 = pm.Normal('beta_intercept_2', mu=0, sigma=sigma)
        beta_neonic_2 = pm.Normal('beta_neonic_2', mu=0, sigma=sigma)
        beta_year_2 = pm.Normal('beta_year_2', mu=0, sigma=sigma)
        beta_habitat_2 = pm.Normal('beta_habitat_2', mu=0, sigma=sigma)

        beta_intercept_3 = pm.Normal('beta_intercept_3', mu=0, sigma=sigma)
        beta_neonic_3 = pm.Normal('beta_neonic_3', mu=0, sigma=sigma)
        beta_year_3 = pm.Normal('beta_year_3', mu=0, sigma=sigma)
        beta_habitat_3 = pm.Normal('beta_habitat_3', mu=0, sigma=sigma)

        # Random effects for site_id (accounting for the fact that we have repeated measures)
        site_effect_1 = pm.Normal('site_effect_1', mu=0, sigma=1, shape=len(np.unique(site_ids)))
        site_effect_2 = pm.Normal('site_effect_2', mu=0, sigma=1, shape=len(np.unique(site_ids)))
        site_effect_3 = pm.Normal('site_effect_3', mu=0, sigma=1, shape=len(np.unique(site_ids)))

        # Linear models
        mu_occupancy_1 = (beta_intercept_1 + beta_neonic_1 * X_neonic + beta_year_1 * X_year + 
                           beta_habitat_1 * X_habitat + site_effect_1[site_ids - 1])

        mu_occupancy_2 = (beta_intercept_2 + beta_neonic_2 * X_neonic + beta_year_2 * X_year + 
                           beta_habitat_2 * X_habitat + site_effect_2[site_ids - 1])

        mu_occupancy_3 = (beta_intercept_3 + beta_neonic_3 * X_neonic + beta_year_3 * X_year + 
                           beta_habitat_3 * X_habitat + site_effect_3[site_ids - 1])

        # Logistic regression for species presence
        occupancy_prob_1 = pm.math.sigmoid(mu_occupancy_1)
        occupancy_prob_2 = pm.math.sigmoid(mu_occupancy_2)
        occupancy_prob_3 = pm.math.sigmoid(mu_occupancy_3)

        # Likelihood (Bernoulli distribution)
        y_obs_1 = pm.Bernoulli('y_obs_1', p=occupancy_prob_1, observed=y_species_1)
        y_obs_2 = pm.Bernoulli('y_obs_2', p=occupancy_prob_2, observed=y_species_2)
        y_obs_3 = pm.Bernoulli('y_obs_3', p=occupancy_prob_3, observed=y_species_3)

        # Sampling
        trace = pm.sample(2000, return_inferencedata=False, target_accept=0.95)

    # Plot trace using ArviZ (no need to convert to InferenceData in PyMC4)
    az.plot_trace(trace)
    plt.show()

    # Return summary statistics
    summary = az.summary(trace)
    return summary
    
def main():
    data = generate_fake_data()
    summary = run_bayesian_model(data)
    print(summary)

if __name__ == "__main__":
    main()
