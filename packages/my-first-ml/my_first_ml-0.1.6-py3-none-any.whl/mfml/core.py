"""
Core functionality for mfml package
"""

describe_text = """wine_classification -> EDA with shape, name, target info, Scatter matrix visualization, Correlation heatmap, Decision tree, k-NN

iris_classification -> Train-test split, k-NN with different k values (6, 20) and distance metrics (Euclidean, Manhattan), Gaussian Naive Bayes with confusion matrix and classification report, SVM with linear kernel (ovo and ovr), SVM with RBF kernel and different hyperparameters (gamma and C variations)

matplotlib_sb -> Line/scatter plots, Histograms, Pie charts, Plot customization, Subplots, Seaborn visualizations

numpy_basic -> Array operations, Broadcasting, Math functions, Random numbers, Set operations, Statistics, Polynomials

scipy_eda -> Data exploration, Correlation analysis (Pearson/Spearman), Heatmap, Chi-square test

imbalance -> Data loading, Train-test split, Baseline Logistic Regression model, SMOTE oversampling, Evaluation with confusion matrix and classification report"""

iris_classification_text = """# Import necessary libraries
import pandas as pd
from sklearn import datasets
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report

# Load the Iris dataset
iris1 = datasets.load_iris()

# Assign features to x and target to y
x = iris1.data
y = iris1.target

# Split the dataset into training and testing sets (70% train, 30% test)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

# --- K-Nearest Neighbors (KNN) ---

# Initialize the KNN classifier with k=6 and Euclidean distance (p=2)
knn1 = KNeighborsClassifier(n_neighbors=6, metric='minkowski', p=2)
# Train the model using the training data
knn1.fit(x_train, y_train)
# Make predictions on the test data
y_predict1 = knn1.predict(x_test)
# Print the accuracy score of the model
print("KNN (k=6, Euclidean) Accuracy:", knn1.score(x_test, y_test))

# Initialize another KNN classifier with k=20 and Euclidean distance
knn2 = KNeighborsClassifier(n_neighbors=20, metric='minkowski', p=2)
# Train the second KNN model
knn2.fit(x_train, y_train)
# Make predictions with the second model
y_predict2 = knn2.predict(x_test)
# Print the accuracy score of the second model
print("KNN (k=20, Euclidean) Accuracy:", knn2.score(x_test, y_test))

# Initialize a third KNN classifier with k=6 and Manhattan distance (p=1)
knn3 = KNeighborsClassifier(n_neighbors=6, metric='minkowski', p=1)
# Train the third KNN model
knn3.fit(x_train, y_train)
# Make predictions with the third model
y_predict3 = knn3.predict(x_test)
# Print the accuracy score of the third model
print("KNN (k=6, Manhattan) Accuracy:", knn3.score(x_test, y_test))


# --- Naive Bayes ---

# Initialize the Gaussian Naive Bayes classifier
gnb1 = GaussianNB()
# Train the model and make predictions on the test data
y_pred_nb = gnb1.fit(x_train, y_train).predict(x_test)
# Print the accuracy score
print("Gaussian Naive Bayes Accuracy:", gnb1.score(x_test, y_test))
# Print the confusion matrix
print("Confusion Matrix (Naive Bayes):", confusion_matrix(y_test, y_pred_nb))
# Print the classification report
print("Classification Report (Naive Bayes):", classification_report(y_test, y_pred_nb))


# --- Support Vector Machine (SVM) ---

# Initialize SVM with a linear kernel and 'one-vs-one' decision function
svc1 = SVC(kernel='linear', random_state=0, decision_function_shape='ovo')
# Train the model
svc1.fit(x_train, y_train)
# Make predictions
preds1 = svc1.predict(x_test)
# Print the predicted labels
print("Predicted labels (SVM Linear, ovo):", preds1)
# Print the accuracy score
print("SVM (Linear Kernel, ovo) Accuracy:", svc1.score(x_test, y_test))

# Initialize SVM with a linear kernel and 'one-vs-rest' decision function
svc2 = SVC(kernel='linear', random_state=0, decision_function_shape='ovr')
# Train the model
svc2.fit(x_train, y_train)
# Make predictions
preds2 = svc2.predict(x_test)
# Print the accuracy score
print("SVM (Linear Kernel, ovr) Accuracy:", svc2.score(x_test, y_test))

# Initialize SVM with RBF kernel, gamma=0.7, C=1.0
svc3 = SVC(kernel='rbf', gamma=0.7, C=1.0)
# Train the model
svc3.fit(x_train, y_train)
# Make predictions
preds3 = svc3.predict(x_test)
# Print the accuracy score
print("SVM (RBF Kernel, gamma=0.7) Accuracy:", svc3.score(x_test, y_test))

# Initialize SVM with RBF kernel, gamma=0.2, C=1.0
svc4 = SVC(kernel='rbf', gamma=0.2, C=1.0)
# Train the model
svc4.fit(x_train, y_train)
# Make predictions
preds4 = svc4.predict(x_test)
# Print the accuracy score
print("SVM (RBF Kernel, gamma=0.2) Accuracy:", svc4.score(x_test, y_test))

# Initialize SVM with RBF kernel, gamma=0.2, C=0.2
svc5 = SVC(kernel='rbf', gamma=0.2, C=0.2)
# Train the model
svc5.fit(x_train, y_train)
# Make predictions
preds5 = svc5.predict(x_test)
# Print the accuracy score
print("SVM (RBF Kernel, C=0.2) Accuracy:", svc5.score(x_test, y_test))"""


matplotlib_sb_text = """# --- Part 1: Matplotlib ---

# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt

# --- Line and Scatter Plots ---

# Define data for plotting
years = [1960, 1970, 1980, 1990, 2000, 2010]
population = [21.91, 23.90, 24.80, 20.93, 22.30, 26.90]

# Create a line plot
print("Generating Line Plot...")
plt.plot(years, population)
plt.show()

# Create a scatter plot using the same data
print("Generating Scatter Plot...")
plt.scatter(years, population)
plt.show()

# Create a scatter plot with custom colors
# Note: 'Years' and 'Population' must be defined and have the same length as 'colors'.
# Assuming a different dataset for this example as shown in the PDF.
print("Generating Colored Scatter Plot...")
years__new = [1990, 2000, 2010, 2020, 2030]
population_new = [26.7, 23.4, 27.5, 28.5, 24.9]
colors = ['violet', 'tomato', 'crimson', 'green', 'blue']
plt.scatter(years_new, population_new, c=colors)
plt.show()


# --- Histograms and Pie Charts ---

# Define new data for city populations
city_name = ['London', 'Paris', 'Tokyo', 'Beijing', 'Rome']
city_pop = [65342, 89123, 54239, 23098, 12367]

# Create a histogram of city populations with default bins
print("Generating Histogram (Default Bins)...")
plt.hist(city_pop)
plt.show()

# Create a histogram with automatically determined bins
print("Generating Histogram (Auto Bins)...")
plt.hist(city_pop, bins='auto')
plt.show()

# Create a histogram with a single bin
print("Generating Histogram (1 Bin)...")
plt.hist(city_pop, bins=1)
plt.show()

# Create a pie chart using city populations and names
print("Generating Pie Chart...")
plt.pie(city_pop, labels=city_name)
plt.show()


# --- Plot Customization ---

# Create a customized line plot
print("Generating Customized Line Plot...")
plt.plot(years, population)
# Set the label for the x-axis
plt.xlabel('Years')
# Set the label for the y-axis
plt.ylabel('Population')
# Customize the x-axis tick marks
plt.xticks([1960, 1970, 1980, 1990, 2000, 2010])
# Customize the y-axis tick marks with custom labels
plt.yticks([20.93, 21.91, 22.30, 23.90, 24.80, 26.90], ['20M', '21M', '22M', '23M', '24M', '26M'])
plt.show()


# Create a scatter plot with a title and custom x-axis labels
print("Generating Customized Scatter Plot...")
plt.scatter(np.arange(5), city_pop)
plt.xticks([0, 1, 2, 3, 4], ['1960', '1970', '1980', '1990', '2000'])
plt.title('Most Populated Cities')
plt.show()


# --- Multiple Plots ---

# Define data for Canada and USA populations
canada_pop = [21.91, 23.90, 24.80, 20.93, 22.30, 26.90]
usa_pop = [32.91, 24.80, 23.60, 21.92, 32.30, 26.90]

# Plot Canada and USA data on the same graph with specific styling
print("Generating Multiple Plots on One Graph...")
plt.plot(years, canada_pop, marker='s', mew=8, ls='-') # Using 's' for square marker
plt.plot(years, usa_pop, ls='--', lw=1)
# Add a legend to the plot in the 'best' location
plt.legend(['Canada', 'USA'], loc='best')
# Add a grid to the background
plt.grid()
plt.show()

# Create a figure with two subplots side-by-side
print("Generating Subplots...")
# Select the first subplot (1 row, 2 columns, 1st plot)
plt.subplot(1, 2, 1)
plt.plot(years, canada_pop, marker='s', mew=8, ls='-')
plt.title('Population of Canada')

# Select the second subplot (1 row, 2 columns, 2nd plot)
plt.subplot(1, 2, 2)
plt.plot(years, usa_pop, ls='--', lw=1)
plt.title('Population of United States')
plt.show()


# --- Part 2: Seaborn ---

# Import pandas and seaborn
import pandas as pd
import seaborn as sb

# Load the ozone dataset from a CSV file
# Note: You will need to replace the file path with the actual location of 'ozone1.csv'
file_path_ozone = 'F:/00-Douglas College/1- Semester 1/3- Machine Learning in Data Science (3290)/Slides/ozone1.csv'
# Using a try-except block in case the file is not found
try:
    data1 = pd.read_csv(file_path_ozone, low_memory=False)

    # Create a strip plot
    print("Generating Seaborn Strip Plot...")
    # A smaller subset for better visualization
    subset_states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California']
    data_subset = data1[data1['State Name'].isin(subset_states)]
    sb.stripplot(x='State Name', y='Site Num', data=data_subset, size=10, jitter=True)
    plt.show()

    # Create a box plot
    print("Generating Seaborn Box Plot...")
    sb.boxplot(x='State Name', y='Site Num', data=data_subset)
    plt.show()
    
    # Create a joint plot
    print("Generating Seaborn Joint Plot...")
    sb.jointplot(x='State Name', y='Site Num', data=data_subset, kind='scatter')
    plt.show()

except FileNotFoundError:
    print(f"Warning: The file '{file_path_ozone}' was not found.")
    print("Skipping Seaborn plots which depend on this file.")"""


numpy_basic_text = """# Import the NumPy library
import numpy as np
import math # Recommended for scalar math instead of the deprecated np.math

# --- NumPy Version ---
# Check the installed NumPy version
print("NumPy Version:", np.__version__)


# --- Array and Matrix Creation ---

# The following line causes a TypeError because the lists are not enclosed in a single list.
# a = np.array([1,2], [3,4])

# Correct way to create a 2D NumPy array
a_array = np.array([[1,2], [3,4]])
print("NumPy Array:", a_array)

# Create a NumPy matrix (Note: np.matrix is less common now; np.array is preferred)
b_matrix = np.matrix([[1,2], [3,4]])
print("NumPy Matrix:", b_matrix)


# --- Multiplication Operations ---

# Define a 2x2 array of 8-bit integers
a = np.array([[1,2], [3,4]], dtype='int8')

# Perform matrix multiplication (dot product)
dot_product = np.dot(a, a)
print("Dot Product (Matrix Multiplication):", dot_product)

# Perform element-wise multiplication
element_wise_mult = np.multiply(a, a)
print("Element-wise Multiplication:", element_wise_mult)

# Calculate the product of all elements in the array
total_product = np.prod(a)
print("Product of all elements:", total_product)


# --- Broadcasting ---

# Add a scalar to each element of an array
b = np.array([1, 2, 3])
print("Original array 'b':", b)
print("Broadcasting b + 5:", b + 5)

# Create a 3x3 array of all ones
c = np.ones((3, 3))
# Create a 1D array
d = np.array([5, 6, 7])
# Add the 1D array 'd' to each row of the 2D array 'c'
print("Array 'c' (3x3 of ones):", c)
print("Array 'd':", d)
print("Broadcasting c + d:", c + d)

# Create a 3x1 array (column vector)
e = np.ones((3, 1))
# Create a 1x3 array (row vector) is the same as d
f = np.array([5, 6, 7])
# Add the column and row vectors. Broadcasting expands both to a 3x3 shape before adding.
print("Array 'e' (3x1 of ones):", e)
print("Array 'f':", f)
print("Broadcasting e + f:", e + f)


# --- Basic Math Operations ---

# Define a 2x2 array
g = np.array([[1, 2], [3, 4]])
print("Original array 'g':", g)

# Calculate the sum of all elements
print("Sum of all elements in g:", np.sum(g))

# Calculate the cumulative sum along the columns (axis=0)
print("Cumulative sum along columns (axis=0):", np.cumsum(g, axis=0))

# Calculate the cumulative sum along the rows (axis=1)
print("Cumulative sum along rows (axis=1):", np.cumsum(g, axis=1))

# Perform element-wise subtraction
print("Element-wise subtraction (a - a):", np.subtract(a, a))

# Perform floating-point division
print("Floating-point division [5,6,7] / 3:", np.divide([5, 6, 7], 3))

# Perform integer (floor) division
print("Floor division [5,6,7] // 3:", np.floor_divide([5, 6, 7], 3))


# --- Deprecated np.math and Random Numbers ---

# The 'np.math' alias is deprecated. Use the standard 'math' library instead.
print("Using 'math' library for scalar operations:")
print("Square root of 5:", math.sqrt(5))
print("Not a Number (NaN):", math.nan)
print("Infinity:", math.inf)

# Create a 2x3 array with random numbers from a uniform distribution between 1 and 5
print("2x3 array with random numbers (uniform distribution):", np.random.uniform(1, 5, (2, 3)))

# Create a 2x1 array with random numbers from a standard normal distribution
print("2x1 array with random numbers (standard normal distribution):", np.random.standard_normal((2, 1)))


# --- Array Generation and Properties ---

# Generate an array with values from 1 up to (but not including) 10, with a step of 3
print("np.arange(1, 10, 3):", np.arange(1, 10, 3))

# Generate an array with 4 evenly spaced values from 1 to 10 (inclusive)
print("np.linspace(1, 10, 4):", np.linspace(1, 10, 4))

# Create arrays for property examples
a_props = np.ones((1, 3))
print("Array 'a_props':", a_props)

# Get the total number of elements in the array
print("Size of a_props:", np.size(a_props))

# Get the shape (dimensions) of the array
print("Shape of a_props:", np.shape(a_props))


# --- Set Operations and Statistics ---

# Define arrays for set operations
a_set = np.array([1, 7, 2, 3, 1, 2, 4, 3])
b_set = np.array([3, 4, 6, 7, 8, 1, 2])
print("--- Set Operations and Statistics ---")
print("Original array 'a_set':", a_set)

# Find the unique elements in an array
print("Unique elements in a_set:", np.unique(a_set))

# Find the union of two arrays
print("Union of a_set and b_set:", np.union1d(a_set, b_set))

# Find the intersection of two arrays
print("Intersection of a_set and b_set:", np.intersect1d(a_set, b_set))

# Calculate the mean, median, standard deviation, and variance
print("Mean of a_set:", np.mean(a_set))
print("Median of a_set:", np.median(a_set))
print("Standard Deviation of a_set:", np.std(a_set))
print("Variance of a_set:", np.var(a_set))


# --- Polynomial Operations ---

# Define polynomial coefficients for 1x^2 + 1x + 2
coeff = np.array([1, 1, 2])
print("--- Polynomial Operations ---")
print("Polynomial coefficients:", coeff)

# Evaluate the polynomial at x=1 (1*1^2 + 1*1 + 2 = 4)
print("Value of polynomial at x=1:", np.polyval(coeff, 1))

# Calculate the derivative of the polynomial (2x + 1)
print("Derivative coefficients:", np.polyder(coeff))

# Calculate the integral of the polynomial (1/3*x^3 + 1/2*x^2 + 2x + C)
print("Integral coefficients:", np.polyint(coeff))"""


scipy_eda_text = """# --- Part 1: Weather Data Analysis ---

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
from scipy.stats import pearsonr, spearmanr, chi2_contingency

# Load the weather dataset from a CSV file
# Note: You will need to replace the file path with the actual location of 'Weather1.csv'
file_path_weather = 'F:/00-Douglas College/1- Semester 1/3- Machine Learning in Data Science (3290)/Slides/Weather1.csv'
data1 = pd.read_csv(file_path_weather)

# Print the entire dataframe to see the loaded data
print("--- Weather Data Head ---")
print(data1.head())

# --- Basic Data Exploration ---

# Print the 'Humidity' column
print("--- Humidity Column ---")
print(data1.Humidity)

# Calculate and print the mean of the 'Humidity' column
print("Mean of Humidity:", np.mean(data1.Humidity))

# Calculate and print the standard deviation of the 'Humidity' column
print("Standard Deviation of Humidity:", np.std(data1.Humidity))

# Print the frequency count of each value in the 'Humidity' column
print("--- Value Counts for Humidity ---")
print(data1.Humidity.value_counts())

# --- Visualization ---

# Create a pairplot to visualize relationships between all numerical variables
print("Generating pairplot for weather data...")
sb.pairplot(data1)
# Display the plot
plt.show()

# --- Correlation Analysis ---

# Calculate the Pearson correlation coefficient between 'Temperature' and 'Humidity'
cor1_statistic, cor1_pvalue = pearsonr(data1['Temperature (C)'], data1.Humidity)
print("--- Pearson Correlation (Temperature vs Humidity) ---")
print("Pearson Statistic:", cor1_statistic)
print("P-value:", cor1_pvalue)


# Calculate the full correlation matrix for the dataframe using pandas
print("--- Full Correlation Matrix (Pearson) ---")
cor2 = data1.corr(numeric_only=True)
print(cor2)

# Create a heatmap to visualize the correlation matrix
print("Generating heatmap for correlation matrix...")
sb.heatmap(cor2)
plt.show()

# Calculate the Spearman rank correlation between 'WindBearing' and 'WindSpeed'
sp1_statistic, sp1_pvalue = spearmanr(data1['Wind Bearing (degrees)'], data1['Wind Speed (km/h)'])
print("--- Spearman Correlation (Wind Bearing vs Wind Speed) ---")
print("Spearman Statistic:", sp1_statistic)
print("P-value:", sp1_pvalue)


# --- Part 2: Smartphone Data and Chi-Square Test ---

# Load a new dataset containing smartphone data
# Note: You will need to replace the file path with the actual location of 'smartphone.csv'
file_path_smartphone = 'F:/00-Douglas College/1- Semester 1/3- Machine Learning in Data Science (3290)/Slides/smartphone.csv'
data2 = pd.read_csv(file_path_smartphone)

# Display the first 5 rows of the new dataframe
print("--- Smartphone Data Head ---")
print(data2.head())

# --- Chi-Square Test for Independence ---

# Create a contingency table (crosstab) between 'Brand' and 'Ram'
print("--- Contingency Table (Brand vs Ram) ---")
table1 = pd.crosstab(data2.Brand, data2.Ram)
print(table1)

# Perform the Chi-Square test on the contingency table's values
chi2, p_value, dof, expected = chi2_contingency(table1.values)

# Print the Chi-Square statistic
print("--- Chi-Square Test Results ---")
print("Chi-Square Statistic:", chi2)

# Print the p-value
print("P-value:", p_value)

# Print the degrees of freedom
print("Degrees of Freedom:", dof)

# Print the expected frequencies table
print("Expected Frequencies Table:", expected)"""


wine_classification_text = """import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from scipy.stats import pearsonr
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.datasets import load_wine
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
import seaborn as sb
from sklearn import tree

# Load and prepare data
wine1 = load_wine()
wineDF = pd.DataFrame(wine1.data, columns=wine1.feature_names)
wineDF['target'] = wine1.target

# Display data information
print("Dataset shape:", wine1.data.shape)
print("Feature names:", wine1.feature_names)
print("Target names:", wine1.target_names)
print("Target data:", wine1.target)

# Display scatter matrix
pd.plotting.scatter_matrix(wineDF, c=wine1.target, figsize=[11,11], s=150)
plt.title('DF Scatter Matrix')
plt.show()

# Display correlation heatmap
cor1 = wineDF.corr()
sb.heatmap(cor1)
plt.title('Correlation Heatmap')
plt.show()

# Split into training and test data
x = wine1.data
y = wine1.target
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

# Build and evaluate decision tree model
tree1 = DecisionTreeClassifier()
tree1.fit(x_train, y_train)
pre1 = tree1.predict(x_test)

print("Decision tree accuracy:", metrics.accuracy_score(y_test, pre1))
print("Decision tree classification report:", classification_report(y_test, pre1))
print("Decision tree confusion matrix:", confusion_matrix(y_test, pre1))

# Plot decision tree
plt.figure(figsize=(20,10))
tree.plot_tree(tree1, feature_names=wine1.feature_names, class_names=wine1.target_names, filled=True)
plt.title('Decision Tree Visualization')
plt.show()

# Build and evaluate k-NN model (k=6)
knn1 = KNeighborsClassifier(n_neighbors=6, metric='minkowski', p=2)
knn1.fit(x_train, y_train)
y_predict1 = knn1.predict(x_test)
print("k-NN (k=6) score:", knn1.score(x_test, y_test))

# Build and evaluate k-NN model (k=8)
knn2 = KNeighborsClassifier(n_neighbors=8, metric='minkowski', p=2)
knn2.fit(x_train, y_train)
y_predict2 = knn2.predict(x_test)
print("k-NN (k=8) score:", knn2.score(x_test, y_test))

# Build and evaluate k-NN model (k=10)
knn3 = KNeighborsClassifier(n_neighbors=10, metric='minkowski', p=2)
knn3.fit(x_train, y_train)
y_predict3 = knn3.predict(x_test)
print("k-NN (k=10) score:", knn3.score(x_test, y_test))
print("k-NN (k=10) confusion matrix:", confusion_matrix(y_test, y_predict3))"""


imbalance_text = """# --- Part 1: Initial Setup and Baseline Model ---

# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

# Load the dataset from a CSV file
# Note: You will need to replace the file path with the actual location of 'creditcard.csv'
file_path = 'C:/Users/Paris/Desktop/creditcard.csv'
try:
    data1 = pd.read_csv(file_path)

    # Print a summary of the dataframe
    print("--- Dataframe Info ---")
    data1.info()

    # Drop unnecessary columns
    data1 = data1.drop(['Time', 'Amount'], axis=1)
    print("Dropped 'Time' and 'Amount' columns.")

    # Check the distribution of the target variable 'Class'
    print("--- Class Distribution (Imbalance) ---")
    print(data1['Class'].value_counts())

    # Separate features (x) and target variable (y)
    x = data1.drop(['Class'], axis=1).values
    y = data1['Class'].values # Corrected from data['Class'] to data1['Class']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0)

    # Print the shapes of the datasets to confirm the split
    print("--- Shape of Train/Test Sets ---")
    print("Shape of X_train:", X_train.shape)
    print("Shape of y_train:", y_train.shape)
    print("Shape of X_test:", X_test.shape)
    print("Shape of y_test:", y_test.shape)

    # --- Train a baseline Logistic Regression model on the imbalanced data ---
    print("--- Training Baseline Model on Imbalanced Data ---")
    lr = LogisticRegression(max_iter=1000) # Increased max_iter for convergence
    lr.fit(X_train, y_train.ravel())

    # Make predictions on the test set
    predictions = lr.predict(X_test)

    # Print the classification report for the baseline model
    print("--- Classification Report (Baseline Model) ---")
    print(classification_report(y_test, predictions))

    # --- Part 2: Handling Imbalance with SMOTE (Oversampling) ---

    # Print the class distribution in the training set before oversampling
    print("--- Before Oversampling (SMOTE) ---")
    print("Count of label '1' in y_train: {}".format(sum(y_train == 1)))
    print("Count of label '0' in y_train: {}".format(sum(y_train == 0)))

    # Import the SMOTE library
    from imblearn.over_sampling import SMOTE

    # Initialize SMOTE
    sm = SMOTE(random_state=2)

    # Apply SMOTE to the training data
    X_train_res, y_train_res = sm.fit_resample(X_train, y_train.ravel())

    # Print the shape and class distribution after oversampling
    print("--- After Oversampling (SMOTE) ---")
    print('Shape of X_train_res: {}'.format(X_train_res.shape))
    print('Shape of y_train_res: {}'.format(y_train_res.shape))
    print("Count of label '1' in y_train_res: {}".format(sum(y_train_res == 1)))
    print("Count of label '0' in y_train_res: {}".format(sum(y_train_res == 0)))

    # Train a new Logistic Regression model on the balanced (oversampled) data
    lr1 = LogisticRegression(max_iter=1000)
    lr1.fit(X_train_res, y_train_res.ravel())
    predictions_smote = lr1.predict(X_test)

    # Print the classification report for the SMOTE model
    print("--- Classification Report (After SMOTE) ---")
    print(classification_report(y_test, predictions_smote))

    # --- Part 3: Handling Imbalance with NearMiss (Undersampling) ---

    # Print the class distribution in the training set before undersampling
    print("--- Before Undersampling (NearMiss) ---")
    print("Count of label '1' in y_train: {}".format(sum(y_train == 1)))
    print("Count of label '0' in y_train: {}".format(sum(y_train == 0)))
    
    # Import the NearMiss library
    from imblearn.under_sampling import NearMiss
    
    # Initialize NearMiss
    nr = NearMiss()
    
    # Apply NearMiss to the training data
    X_train_miss, y_train_miss = nr.fit_resample(X_train, y_train.ravel())
    
    # Print the shape and class distribution after undersampling
    print('--- After Undersampling (NearMiss) ---')
    print('Shape of X_train_miss: {}'.format(X_train_miss.shape))
    print('Shape of y_train_miss: {}'.format(y_train_miss.shape))
    print("Count of label '1' in y_train_miss: {}".format(sum(y_train_miss == 1)))
    print("Count of label '0' in y_train_miss: {}".format(sum(y_train_miss == 0)))

    # Train a third Logistic Regression model on the balanced (undersampled) data
    lr2 = LogisticRegression(max_iter=1000)
    lr2.fit(X_train_miss, y_train_miss.ravel())
    predictions_miss = lr2.predict(X_test)

    # Print the classification report for the NearMiss model
    print("--- Classification Report (After NearMiss) ---")
    print(classification_report(y_test, predictions_miss))

except FileNotFoundError:
    print(f"Warning: The file '{file_path}' was not found.")
    print("Skipping the analysis.")"""


def describe():
    """
    Returns a brief description of the mfml package.
    """
    return describe_text


def wine_classification():
    """
    Performs wine dataset classification analysis using Decision Tree and k-NN algorithms.
    
    Loads the wine dataset, visualizes data relationships through scatter matrix and 
    correlation heatmap, trains Decision Tree and k-NN classifiers with different 
    parameters (k=6, 8, 10), and evaluates model performance using accuracy scores 
    and confusion matrices.
    """
    return wine_classification_text


def iris_classification():
    """
    Performs iris dataset classification analysis using k-NN, Gaussian Naive Bayes, and SVM algorithms.
    
    Loads the iris dataset, splits data into training and testing sets, trains k-NN classifiers 
    with different k values (6, 20) and distance metrics (Euclidean, Manhattan), trains Gaussian 
    Naive Bayes and SVM classifiers with various kernels and hyperparameters, and evaluates model 
    performance using accuracy scores, confusion matrices, and classification reports.
    """
    return iris_classification_text


def matplotlib_sb():
    """
    Demonstrates data visualization using Matplotlib and Seaborn libraries.
    
    Showcases various plot types including line plots, scatter plots, histograms, pie charts, 
    and subplots using Matplotlib. Additionally, demonstrates Seaborn visualizations such as 
    distribution plots, count plots, box plots, violin plots, heatmaps, and pair plots.
    """
    return matplotlib_sb_text


def numpy_basic():
    """
    Demonstrates basic operations and functionalities of the NumPy library.
    
    Covers array creation, indexing, slicing, reshaping, broadcasting, mathematical operations, 
    random number generation, set operations, statistical functions, and polynomial operations 
    using NumPy.
    """
    return numpy_basic_text 


def scipy_eda():
    """
    Demonstrates exploratory data analysis (EDA) using the SciPy library.
    
    Covers data exploration techniques, correlation analysis (Pearson and Spearman), 
    heatmap visualization, and statistical hypothesis testing (Chi-square test) using SciPy.
    """
    return scipy_eda_text


def imbalance():
    """
    Demonstrates handling imbalanced datasets using oversampling and undersampling techniques.
    
    Loads a credit card fraud detection dataset, trains a baseline Logistic Regression model 
    on the imbalanced data, applies SMOTE for oversampling the minority class, trains a new 
    model on the balanced data, applies NearMiss for undersampling the majority class, and 
    trains another model on the balanced data. Evaluates model performance using classification 
    reports.
    """
    return imbalance_text