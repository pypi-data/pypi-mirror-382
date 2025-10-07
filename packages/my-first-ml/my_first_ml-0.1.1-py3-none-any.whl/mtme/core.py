"""
Core functionality for mtme package
"""

def describe():
    """
    Returns a brief description of the mtme package.
    """
    return "mtme: A test package for ML explanation utilities"


def wine_classification():
    """
    Performs wine dataset classification analysis using Decision Tree and k-NN algorithms.
    
    Loads the wine dataset, visualizes data relationships through scatter matrix and 
    correlation heatmap, trains Decision Tree and k-NN classifiers with different 
    parameters (k=6, 8, 10), and evaluates model performance using accuracy scores 
    and confusion matrices.
    """
    with open("wine_analysis.txt", "r") as file:
        data = file.read() 
    return data


def iris_classification():
    """
    Performs iris dataset classification analysis using k-NN, Gaussian Naive Bayes, and SVM algorithms.
    
    Loads the iris dataset, splits data into training and testing sets, trains k-NN classifiers 
    with different k values (6, 20) and distance metrics (Euclidean, Manhattan), trains Gaussian 
    Naive Bayes and SVM classifiers with various kernels and hyperparameters, and evaluates model 
    performance using accuracy scores, confusion matrices, and classification reports.
    """
    with open("iris_analysis.txt", "r") as file:
        data = file.read() 
    return data


def matplotlib_sb():
    """
    Demonstrates data visualization using Matplotlib and Seaborn libraries.
    
    Showcases various plot types including line plots, scatter plots, histograms, pie charts, 
    and subplots using Matplotlib. Additionally, demonstrates Seaborn visualizations such as 
    distribution plots, count plots, box plots, violin plots, heatmaps, and pair plots.
    """
    with open("matplotlib_seaborn.txt", "r") as file:
        data = file.read() 
    return data 


def numpy_basic():
    """
    Demonstrates basic operations and functionalities of the NumPy library.
    
    Covers array creation, indexing, slicing, reshaping, broadcasting, mathematical operations, 
    random number generation, set operations, statistical functions, and polynomial operations 
    using NumPy.
    """
    with open("numpy_basics.txt", "r") as file:
        data = file.read() 
    return data 


def scipy_eda():
    """
    Demonstrates exploratory data analysis (EDA) using the SciPy library.
    
    Covers data exploration techniques, correlation analysis (Pearson and Spearman), 
    heatmap visualization, and statistical hypothesis testing (Chi-square test) using SciPy.
    """
    with open("scipy_eda.txt", "r") as file:
        data = file.read() 
    return data
