# LOG FILE
open(r"./errors.log", "w")  # remove its contents
log_error = open(r"./errors.log", "a")

# TITLES AND HEADERS
chi = "Chi squared test values"
cors_comparison = "Correlation matrices"
dd_plot = "DDPlot"
dimensionality = "Dimensionality reduction"
distribution = "Distributions"
distribution_comparison = "Visual representation"
fidelity = "Fidelity"
fidelity_summary = "Fidelity metrics summary"
hellinger_distances = "Hellinger Distance"
mann_whitney = "Mann Whitney p-values"
metrics_by_variables = "Univariable metrics by categorical variables"
neighbour = "Neighbor graphs"
privacy = "Privacy"
privacy_summary = "Privacy metrics summary"
statistical_tests = "Statistical tests"
utility = "Utility"
utility_summary = "Utility metrics summary"
visualizations_section = "Visualizations"

# DOCUMENT TITLE
documentTitle = "Report"

# AUTHOR
author = "RAISE"

# PATHS
# logo
logo_path = "sd_evaluation/evaluation_report/images/EOSC-RAISE.png"

# fidelity
cors_png_path = "cors.png"
ddplot_png_path = "ddplot.png"
hellinger_png_path = "hellinger.png"
pdfPath = "data/"
vis_png_path = "vis.png"
distinguish_png_path = "AUC-ROC.png"

# utility
trtr_tstr_results_png_path = "trtr_tstr.png"

# global variables for execution
dist_image_rows = 6

# PAGE MARGINS
rm = 0.52
lm = 0.75
tm = 0.75
bm = 1.44


# REPORT EXPLANATIONS
hellinger_text = [
    [
        False,
        """The Hellinger Distance is used to quantify the similarity between two probability distributions.""",
    ],
    [
        True,
        """<bullet>&bull;</bullet>If the distance value is 0, the probability distributions of real and synthetic
        data are identical.""",
    ],
    [
        True,
        """<bullet>&bull;</bullet>If the distance value is 1 (maximum value), the probability distributions of real
        and synthetic data are different.""",
    ],
    [
        False,
        """<br/>The lower the Hellinger distance the more similar are the distributions of the real and
        synthetic variables. See Figure {}.<br/><br/>""",
    ],
]


distribution_text = [
    [
        False,
        """When comparing the distributions of two datasets, statistical
tests that can assess whether observed differences are statistically significant.
Two commonly used tests for this purpose are the Chi-Squared test and the Mann-Whitney U test.<br/><br/>
The Mann Whiteny U-test evaluates the distributions of the numerical data of the samples.<br/><br/>
Assumptions:<br/>""",
    ],
    [
        True,
        """<bullet>&bull;</bullet>Under the null hypothesis (H0), the distributions of both populations
        are identical.""",
    ],
    [
        True,
        """<bullet>&bull;</bullet>The alternative hypothesis (H1) is that the distributions are not identical.""",
    ],
    [False, """<br/>Interpretation of results:<br/>"""],
    [
        True,
        """<bullet>&bull;</bullet>If the H0 is rejected (p-value lower than a significance level), there is
        a significant difference in the distributions of the real and synthetic variables.""",
    ],
    [
        True,
        """<bullet>&bull;</bullet>If there is not enough evidence to reject H0 (p-value higher than
        a significance level), it cannot be confirmed that there is a significant difference in the
        distributions of the real and synthetic variables.""",
    ],
    [
        False,
        """ <br/>In Table {} the p-values of this test are shown.<br/><br/>
 The Chi-squared test determines if a difference between observed
 data and expected data is due to chance or if it is due to a relationship between the categorical
 variables.<br/><br/>
 Assumptions:<br/>""",
    ],
    [
        True,
        """<bullet>&bull;</bullet>Under the null hypothesis (H0), there is no significant difference between
        the observed frequencies and the expected frequencies. """,
    ],
    [
        True,
        """<bullet>&bull;</bullet>The alternative hypothesis (H1) there is a significant difference between the
        observed frequencies and the expected frequencies. """,
    ],
    [False, """<br/>Interpretation of results:<br/>"""],
    [
        True,
        """<bullet>&bull;</bullet>If the H0 is rejected (p-value lower than a significance level), there is a
        significant difference between the categorical variables.""",
    ],
    [
        True,
        """<bullet>&bull;</bullet>If there is not enough evidence to reject H0
        (p-value higher than a significance level), it cannot be confirmed whether there is a significant
        difference between the categorical variables. """,
    ],
    [
        False,
        """<br/>In Table {} the p-values of this test are shown.
 <br/><br/>Both of the statistical tests have been performed with a significance level of 0.1.
 <br/><br/>""",
    ],
]

distribution_visual_text = """In Figure {} a visual representation of distributions can be seen together with the mean
Hellinger distance per variable (h_d) and p-value of Mann-Whitney U-test if numerical variable or
Chi Squared-test if categorical variable."""

distribution_visual_text_remove = """mean Hellinger distance per variable (h_d) and """


correlation_text = [
    [
        False,
        """The Pairwise Correlation Difference (PCD) indicates how much the correlation matrices of real and
synthetic data differ.<br/>""",
    ],
    [
        True,
        """<bullet>&bull;</bullet> A lower value (near to 0) indicates that the correlations of real and synthetic data
        are not much different.""",
    ],
    [
        True,
        """<bullet>&bull;</bullet> A higher value (near to 1) indicates that the correlations of real and synthetic data
        are very different.""",
    ],
    [
        False,
        """<br/>The correlation matrices of real and synthetic data have been computed using the Phik (ϕk)
correlation constant that works consistently between categorical and numerical variables, captures
non-linear relationships between variables. See Figure {} <br/> <br/>""",
    ],
]


dd_plot_text = """Depth vs Depth plots the depth values of the combined sample
under two corresponding distributions. If the two distributions are identical,
the plot is a set of segments of the line y=x.
<br/><br/>
The plot shows us as well the R² value, which shows how well the model predicts the outcome.
A R² value of 0 means that the model explains or predicts 0% of the relationship between
the dependent and independent variables. Therefore, a value close to 1 will be the best.
See Figure {}.
<br/><br/>"""


tsne_text = [
    [
        False,
        """Dimensionality reduction is used to visualize real and synthetic sample distributions in
  a lower-dimensional space and assess how well synthetic samples capture the complexity and
  characteristics of real samples visually. However, determining accurate capture is subjective. Therefore,
  it serves as a supplementary tool alongside the following dimensionality reduction techniques:<br/><br/>""",
    ],
    [
        True,
        """<bullet>&bull;</bullet><b>t-distributed Stochastic Neighbor Embedding (t-SNE)</b>: it works by
        measuring similarities between pairs of data points in the high-dimensional space and then representing
        these similarities in the lower-dimensional space.<br/>""",
    ],
    [
        True,
        """<bullet>&bull;</bullet><b>Isomap</b>: starts by creating a neighborhood network, then uses graph distance to
 approximate the geodesic distance between all pairs of points, and finally, finds the low-dimensional
 embedding of the dataset.""",
    ],
    [
        True,
        """<bullet>&bull;</bullet><b>UMAP</b>: constructs a high dimensional graph representation of
        the data and then optimizes a low-dimensional graph to be as structurally similar as possible""",
    ],
    [False, """<br/><br/>"""],
]


TRTR_TSTR_text = """In the utility dimension, the ability of synhtetic data, instead of real data, to train machine
learning models is analyzed to determine if machine learning models trained with synthetic data produce similar
results to machine learning models trained with real data.
To do that, TRTR and TSTR analyses are done. Machine learning classifiers are trained with real data
and then separately with synthetic data.<br/><br/>

To analyze the {} results, {} and their absolute differences are proposed when TRTR and TSTR.<br/><br/>"""

privacy_attacks_text = """Attack-based privacy metrics caltulate the performance of an adversary, who
aims to extract sensitive information from a dataset without authorization.
The European General Data Protection Regulation (GDPR) counts three important indicators:
attack-based evaluations for the singling out, linkability, and inference risks.
<br/><br/>
To measure the Risk, a quantification phase rates the success of the privacy attack from the evaluation with
a measure of statistical uncertainties. Therefore, the lower the risk the better.
<br/><br/>
<b>Singling out</b> occurs when a single data record with a unique combination of attributes can be
identified within the original dataset. The attack involves two processes: univariate, which uses
unique attribute samples as predicates, and multivariate, which combines these predicates logically.
<br/><br/>
<b>Linkability</b> happens when attributes from two or more records, either within the same dataset
or across different datasets, can be linked to the same individual or group. The attack is successful
if known attributes and a synthetic dataset allow linking information from the original dataset.
<br/><br/>
<b>Membership inference</b> occurs when an original record can be linked to a set of synthetically
generated records. The attack identifies the k-closest synthetic records to a set of NA original
records, calculating the Gower distance between the attacked record and its closest neighbor.
Success is determined if the distance is below a specified tolerance.
 <br/><br/>
<b>Inference attribute</b> attack starts assuming the intruder possesses the values of a set of
attributes for a target of the original records. The values for the secret attribute
of the closest synthetic record correspond to the guess of the attacker for the secret set of
attributes. If they are closed enough (when numerical/continuous), or correspond to the
same category, the attack is considered as successful.
 <br/><br/>
"""


distinguishability_text = [
    [
        False,
        """The AUC-ROC and the propensity score measure the performance of a simple classifier
  to distinguish between real and synthetic samples.<br/>
    The ability of the classifier to distinguish between real and synthetic samples across various
    threshold settings is tested.<br/>""",
    ],
    [
        True,
        """A value around 0.5 indicates that the classifier performs no better than random guessing.""",
    ],
    [
        True,
        """A value higher than 0.5 and close to 1 suggests that the classifier is very good at distinguishing
        between real and synthetic samples.""",
    ],
    [
        False,
        """Propensity score estimates the probability that a random sample has to be identified as synthetic.<br/>""",
    ],
    [
        True,
        """A value around 0.5 indicates that the classifier is not able to distinguish between real
        and synthetic data.""",
    ],
    [
        True,
        """A value higher than 0.5 and close to 1 suggests that the classifier is biased to predict a
        random record as synthetic.""",
    ],
    [
        True,
        """A value between 0 and 0.5 suggests that the classifier is biased to predict a random record as real.""",
    ],
    #     [
    #         False,
    #         """The next steps have been applied to compute these metrics:<br/>
    #   1.   Combine and label real and synthetic samples in a single dataset.<br/>""",
    #     ],
    #     [True, """0 for real data (negative class)"""],
    #     [True, """1 for synthetic data (positive class)"""],
    #     [False, """  2.   Preprocess the combined dataset.<br/>"""],
    #     [True, """Standardize numerical variables."""],
    #     [True, """One-hot encode categorical variables."""],
    #     [
    #         False,
    #         """  3.   Train the classification model with the preprocessed dataset<br/>
    # RANDOM FOREST CLASSIFIER<br/>""",
    #     ],
    #     [True, """3 max depths"""],
    #     [True, """1000 estimators"""],
    #     [True, """Use AUC-ROC as the out-of-bag (OOB) score"""],
    #     [False, """  4.   Analyse the OOB score and the OOB decision function<br/>"""],
    #     [
    #         True,
    #         """The OOB score is the average AUC-ROC of each test sample that is not used in the training of
    #         the corresponding decision tree. This is used as the AUC-ROC.""",
    #     ],
    #     [
    #         True,
    #         """The OOB decision function is the aggregate predicted probability for each data point across
    #         trees when that data point is in the OOB sample of that tree. The mean predicted probabilities for
    #         the positive class (synthetic) are used as the Propensity score.""",
    #     ],
    #     [False, """<br/><br/>"""],
]
