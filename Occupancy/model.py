import pymc as pm
import numpy as np
import pandas as pd
import arviz as az

def run_model():
    # Load and clean the dataset
    df = pd.read_csv("formatteddata.csv")  

    # Encode species as categorical variable
    df["species_id"] = pd.Categorical(df["species"]).codes  

    # Standardize predictor
    df["pesticide_intensity_scaled"] = (df["avg_intensity_kg_per_ha"] - df["avg_intensity_kg_per_ha"].mean()) / df["avg_intensity_kg_per_ha"].std()

    num_species = df["species_id"].nunique()  # Number of unique species

    # Bayesian Multi-Species Occupancy Model
    with pm.Model() as occupancy_model:
        beta_0 = pm.Normal("beta_0", mu=0, sigma=1)
        beta_1 = pm.Normal("beta_1", mu=0, sigma=1)

        # If 'region' is categorical, use an index-based prior
        region_idx = pd.factorize(df["region"])[0]  # Convert regions to integer labels
        beta_region = pm.Normal("beta_region", mu=0, sigma=1, shape=len(set(region_idx)))

        logit_psi = beta_0 + beta_1 * df["pesticide_intensity_scaled"] + beta_region[region_idx]
        psi = pm.Deterministic("psi", pm.math.sigmoid(logit_psi))

        y_obs = pm.Bernoulli("y_obs", p=psi, observed=df["occupancy"])
        trace = pm.sample(500, tune=200, chains=2, cores=1, target_accept=0.9)

    print(trace)
    print(az.summary(trace))

    # Model evaluation
    az.plot_trace(trace)
    plt.show()
    print(az.summary(trace))

if __name__ == '__main__':
    run_model()
