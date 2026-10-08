# PaperReview.ai Review

## Metadata

- title: Machine Learning-Driven Optimized Land Use Mix Planning for Sustainable Urban Development
- venue: Sustainability Analytics and Modeling
- submission_date: 2026-10-08T04:18:57.452374
- Retrieved at: 2026-10-08T09:54:54

## Summary

The paper proposes a machine learning pipeline to predict vehicle environmental indicators (environmental score, green vehicle score, fuel efficiency score, and CO2 emissions) using a Kaggle vehicle listings dataset, evaluating linear models, Random Forest, and XGBoost. The authors report that XGBoost achieves the best performance (e.g., R2 = 0.834 for environmental score; R2 = 0.967 for CO2 emissions) and suggest the approach can support data-driven optimization of sustainable urban transportation systems. Despite a title and framing that emphasize land use mix planning, the actual contribution centers on supervised prediction of vehicle environmental attributes; no optimization or land-use modeling is implemented.

## Strengths

- Technical novelty and innovation
  - Applies a standard but relevant suite of ML regressors (linear, regularized linear, Random Forest, XGBoost) to a sustainability-motivated prediction problem.
  - Introduces a set of engineered features intended to capture cost, efficiency, and performance relationships.

- Experimental rigor and validation
  - Uses multiple baseline models and standard metrics (RMSE, MAE, R2) on a reasonably large dataset (reported 100,000 listings).
  - Reports a simple model comparison showing non-linear models outperform linear baselines for key targets.

- Clarity of presentation
  - The modeling pipeline and high-level steps (preprocessing, encoding, training) are outlined in a generally understandable way.
  - Results communicate headline performance numbers clearly.

- Significance of contributions
  - The general ambition to support sustainable transportation decisions with data-driven tools is important to the community.
  - Predicting environmental performance of vehicles is a meaningful subproblem that, if done robustly and interpretably, could inform policy and fleet decisions.

## Weaknesses

- Technical limitations or concerns
  - There is a high risk of target leakage: the feature list includes “co2_per_km” while a primary target is “co2_emissions_g_km,” and “green_score_ratio” while “green_vehicle_score” is a target. This likely explains the very high R2 for CO2 and undermines the validity of results.
  - Categorical encoding via LabelEncoder for linear models is inappropriate and can distort linear relationships; one-hot encoding is standard.
  - Hyperparameter tuning appears minimal or absent (fixed n_estimators, max_depth, alpha), undermining the fairness and rigor of model comparisons.
  - The paper claims optimization of fleet composition and land use planning but presents no optimization model, objective, constraints, or decision framework.

- Experimental gaps or methodological issues
  - The dataset description is not credible as presented: typical Kaggle car listing datasets do not include “annual driving, commute distance, family size.” Targets such as “environmental_score” and “green_vehicle_score” are not properly defined or sourced.
  - The train/test protocol is unclear and possibly inconsistent (“3-seed cross-validation” and a “20% holdout” are both mentioned without detail); no group-wise or model-year-wise splits to test generalization across unseen vehicle models.
  - The results table is incomplete (ellipses for Ridge/Lasso and partial metrics), and ablation studies for engineered features are not provided.
  - No external validation on authoritative datasets (e.g., EPA FuelEconomy.gov, WLTP/NEDC/Euro 6) or across geography/time; no uncertainty quantification or robustness checks.

- Clarity or presentation issues
  - Major mismatch between title/keywords/intro (land use mix planning) and the actual content (vehicle-level environmental prediction). The core optimization objective articulated in the abstract and introduction is not executed in the methods or results.
  - Key terms (environmental_score, green_vehicle_score) are undefined; it is unclear how they are computed and whether they are consistent or comparable across observations.
  - The references include placeholders, possibly non-existent or incomplete citations; prior work context is cursory and does not engage the sustainability modeling literature.

- Missing related work or comparisons
  - Absent engagement with optimization methods for fleet composition (e.g., fleet size and mix, multi-objective planning), dynamic emissions modeling, or integrated urban sustainability assessments.
  - No comparison to physics-based/standard emissions factor models or regulatory label estimates as simple baselines (which could be near-sufficient for CO2).
  - Does not situate contributions against recent sustainability analytics efforts in multi-objective EV infrastructure planning, dynamic emissions modeling, routing under uncertainty, travel behavior/ABM, or 15-minute city evaluations.

## Detailed Comments

- Technical soundness evaluation
  - The presence of “co2_per_km” as a predictor while modeling “co2_emissions_g_km” is a critical red flag for label leakage. If “co2_per_km” is a re-scaled or duplicated target, the reported R2 is not meaningful. The same concern applies to “green_score_ratio” when predicting “green_vehicle_score.” The authors must explicitly list all input features used in each target’s prediction and remove any that are functionally dependent on the target or use near-proxies.
  - Encoding choices are not tailored to model families (e.g., label encoding for linear models). For linear/ridge/lasso, one-hot encoding is standard to avoid imposing ordinal structure on categories.
  - Model selection lacks tuning and controls. Without systematic hyperparameter optimization (e.g., nested CV or Bayesian/ grid search), reported performance may reflect arbitrary settings rather than fair comparisons.
  - The generalization protocol is weak. Random train/test splits with vehicles can leak information across similar trims/years. Grouped splits (by make–model–year) or temporal splits are needed to assess how models perform on unseen models/years—essential for decision support.

- Experimental evaluation assessment
  - Results are under-reported and inconsistent. The table omits Ridge/Lasso results and only partially reports metrics for some targets. Report mean and standard deviation across multiple seeds/folds with clear splits. Include MAE systematically.
  - Provide strong baselines. For CO2, simple physics-based or label-based baselines (e.g., a linear model using engine displacement, cylinders, and stated fuel consumption alone) could be competitive. Show that ML adds incremental value beyond such baselines.
  - Interpretability and diagnostics are missing. Use SHAP or permutation importance to assess whether learned relationships align with domain knowledge, and present partial dependence/ICE for top predictors. Conduct ablations on engineered features to justify their inclusion.
  - Robustness and uncertainty are absent. Include sensitivity to data noise, calibration, and geographic/time shifts; quantify uncertainty to support decision use.

- Comparison with related work (using the summaries provided)
  - The field is advancing toward integrated modeling and decision frameworks: dynamic emissions coupling (e.g., detector-informed NO2 with SUMO–LES), EV infrastructure capacity planning with multi-objective optimization, stochastic fleet mix and routing, and agent-based multi-policy evaluations. Compared to these, the current paper is an isolated, off-the-shelf prediction exercise lacking optimization, system coupling, or policy/operational realism.
  - Prior work demonstrates best practices for validation and robustness (e.g., scenario analyses, equity constraints, grid constraints, out-of-sample generalization), which are not reflected here.
  - The paper also does not engage evidence on urban form and emissions (e.g., 15-minute city analysis), despite framing around land use planning.

- Discussion of broader impact and significance
  - In principle, accurate vehicle-level environmental predictions could inform procurement, incentives, and fleet transition strategies. However, the current study stops at prediction and does not implement the “optimization of fleet composition” that it claims. Absent a decision model (objectives, constraints, uncertainty, and trade-offs), the link to sustainable urban development remains aspirational.
  - A path to impact would entail: (i) using validated, authoritative emissions data; (ii) designing a multi-objective fleet composition optimization (e.g., minimize lifecycle cost and operational CO2 subject to service and budget constraints), potentially robust to prediction error; (iii) performing scenario analyses to inform policy with sensitivity to demand, technology, and grid emissions; and (iv) incorporating distributional/equity considerations aligned with sustainability goals.

## Questions

1. What are the precise definitions and data sources for environmental_score, green_vehicle_score, fuel_efficiency_score, and co2_emissions_g_km? Are these labels directly present in the Kaggle dataset or derived by you? Please provide formulas and provenance.
2. Did the feature set used for predicting each target include any direct or indirect proxies for that target (e.g., co2_per_km when predicting co2_emissions_g_km; green_score_ratio when predicting green_vehicle_score)? If so, please remove these and re-run. If not, explain how you ensured no leakage.
3. How were the train/test splits constructed? Were splits grouped by make–model–year to avoid train/test contamination across near-identical vehicles? If not, what is your plan to assess generalization to unseen models/years?
4. What hyperparameter tuning protocol did you use for each model family? Please report search spaces, selection criteria, and cross-validation details. If fixed defaults were used, justify them and discuss fairness across models.
5. Why was label encoding chosen for linear models instead of one-hot encoding? Please quantify the impact of using appropriate encodings on performance.
6. Can you provide a complete, reproducible results table (RMSE, MAE, R2) for all model–target pairs with mean±std across seeds/folds, and include simpler physics-based baselines?
7. What is the rationale for the engineered features, and which contribute most after leakage-safe controls? Please provide ablation results and SHAP-based interpretability analyses.
8. How do your predictions compare against authoritative benchmarks (e.g., EPA FuelEconomy.gov, WLTP/Euro 6 label data) on a held-out, curated subset?
9. The title and abstract refer to land use mix planning and optimization of fleet composition. What is the specific optimization model (objective, constraints, solution method), and where are the results? If not performed, please revise the scope and title or include the optimization component.
10. Do you plan to release code, data processing scripts, and model artifacts to enable reproduction?

## Assessment

While the topic is important and the general aim of data-driven sustainability decision support is aligned with the venue, the present manuscript has foundational issues that preclude publication in its current form. There is a major mismatch between the stated problem (land use mix and fleet composition optimization) and the actual content (isolated prediction experiments). More critically, the feature set appears to include target-proximate variables (e.g., co2_per_km when predicting co2 emissions), creating a high risk of label leakage that likely inflates performance metrics and undermines the central empirical claims. The experimental design lacks rigorous hyperparameter tuning, robust cross-validation with group-wise splits, ablations, interpretability, and external validation against authoritative datasets. Related work is thin and does not position the contribution relative to established optimization and integrated modeling approaches in sustainability analytics.

A constructive path forward would be to (i) remove any leakage, adopt appropriate encodings, and implement rigorous, grouped CV with thorough tuning and ablations; (ii) validate against authoritative emissions datasets; (iii) provide interpretability and uncertainty analyses; and (iv) deliver the promised decision component by formulating and solving a transparent, multi-objective fleet composition optimization (potentially robust to prediction error), or else re-scope the paper to focus on a cleaned, validated predictive contribution with policy-relevant insights. As written, I recommend rejection, with the hope the authors can substantially revise along these lines.

## Binary Scores

TRIPLE_SCORES:
- Claims_Support: [-1]  # Are the central claims adequately supported with evidence?
- Experimental_Soundness: [-1]  # Are the experimental setup and research methodology sound?
- Writing_Clarity: [-1]  # Is the writing clear and well-organized?
- Prior_Work_Context: [-1]  # Is the work properly contextualized relative to prior work?
- Question_Importance: [0]  # Are the research questions being asked important?
- Originality: [-1]  # Does the paper bring significant originality of ideas and/or execution?
- Value_to_Community: [-1]  # Are the results valuable to share with the broader Sustainability Analytics and Modeling community?
