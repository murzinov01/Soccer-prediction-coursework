import csv
import pandas as pd
import seaborn as sb
from joblib import dump, load
from sklearn.svm import SVC
from sklearn import svm
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

matches = pd.read_csv("common_data.csv", sep=',')
print(matches.head())
print((matches["Result"].value_counts()))
print(sb.countplot(matches["Result"]))

# Separate data
X = matches.drop("Result", axis=1)
y = matches["Result"]

# Separate into train and test data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=13)

# Scale
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# RFC
# rfc = RandomForestClassifier(n_estimators=5, random_state=200)
# rfc.fit(X_train, y_train)
# pred_rfc = rfc.predict(X_test)
# dump(rfc, 'rfc_model.joblib')
# print(classification_report(y_test, pred_rfc))
# print(confusion_matrix(y_test, pred_rfc))

# SVM
# clf = svm.SVC()
# clf.fit(X_train, y_train)
# pred_clf = clf.predict(X_test)
# dump(clf, 'cvm_model.joblib')
# print(classification_report(y_test, pred_clf))
# print(confusion_matrix(y_test, pred_clf))

# NEURAL
# mlpc = MLPClassifier(hidden_layer_sizes=(142, 142, 142, 142), max_iter=150)
# mlpc.fit(X_train, y_train)
# pred_mlpc = mlpc.predict(X_test)
# dump(mlpc, 'n_model.joblib')
# print(classification_report(y_test, pred_mlpc))
# print(confusion_matrix(y_test, pred_mlpc))

# Decision
# dec = DecisionTreeClassifier(random_state=3)
# dec.fit(X_train, y_train)
# pred_dec = dec.predict(X_test)
# dump(dec, 'dec_model.joblib')
# print(classification_report(y_test, pred_dec))
# print(confusion_matrix(y_test, pred_dec))

# Load
# mlpc = load("rfc_model46+.joblib")
# pred_mlpc = mlpc.predict(X_test)
# print(classification_report(y_test, pred_mlpc))
# print(confusion_matrix(y_test, pred_mlpc))