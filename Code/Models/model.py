import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn import svm
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from word2vec_model import PlayerEmbedding
from data_analytics import EmbeddingData


odd_feature = list()


def learn_rfc(label="Result", drop_list=None, estimators=10, test_size=0.1) -> None:
    # matches = pd.read_csv("common_data.csv", delimiter=',')
    matches = pd.read_csv("common_learn_data.csv", delimiter=';')
    # Separate data
    # default_drop_list = ["Result"]
    default_drop_list = ["Result", "Total2.5", "Total1.5", "TeamHomeStr", "TeamAwayStr", "Date", "StartTeamHome", "StartTeamAway", "SubsTeamHome", "SubsTeamAway"]
    if drop_list:
        default_drop_list += drop_list

    X = matches.drop(default_drop_list, axis=1)
    y = matches[label]
    print(X, y)

    # Players vectors
    w2v = PlayerEmbedding()
    w2v.w2v_load("5ligsS")

    all_players_names = list(w2v.get_all_vectors().keys())
    players_vecs = np.zeros([matches.shape[0], len(all_players_names)])

    for match_i in range(len(matches)):
        lineup_sh = EmbeddingData.define_players_list(matches["StartTeamHome"][match_i])
        lineup_sa = EmbeddingData.define_players_list(matches["StartTeamAway"][match_i])
        lineup_subh = EmbeddingData.define_players_list(matches["SubsTeamHome"][match_i])
        lineup_suba = EmbeddingData.define_players_list(matches["SubsTeamAway"][match_i])

        all_lineups = [lineup_subh, lineup_suba, lineup_sh, lineup_sa]

        for lineup in all_lineups:
            for player in lineup:
                player_index = all_players_names.index(player)
                players_vecs[match_i][player_index] = all_lineups.index(lineup) + 1

    X_players = pd.DataFrame(data=players_vecs, columns=all_players_names)
    X = pd.concat([X, X_players], axis=1, sort=False)
    keys = X.keys()
    # Separate into train and test data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=13)
    # X_test = X_test[:40]
    # y_test = y_test[:40]
    # Scale
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    #
    # RFC
    rfc = RandomForestClassifier(n_estimators=estimators)
    rfc.fit(X_train, y_train)
    dump(rfc, 'rfc_model.joblib')
    # rfc = load("neural models/rfc_modelBEST50.joblib")
    pred_rfc = rfc.predict(X_test)

    print(classification_report(y_test, pred_rfc))
    print(confusion_matrix(y_test, pred_rfc))

    importances = rfc.feature_importances_
    std = np.std([tree.feature_importances_ for tree in rfc.estimators_], axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")

    for f in range(X.shape[1]):
        print("%d. feature %s (%f)" % (f + 1, keys[indices[f]], importances[indices[f]]))

    for feature_n in indices[40:]:
        odd_feature.append(keys[feature_n])


# learn_rfc(label="Result", estimators=40)
# learn_rfc(label="Result", estimators=15, drop_list=odd_feature)


def learn_svm(label="Result", drop_list=None, test_size=0.1) -> None:
    # matches = pd.read_csv("common_data.csv", delimiter=',')
    matches = pd.read_csv("common_learn_data.csv", delimiter=';')
    # Separate data
    # default_drop_list = ["Result"]
    default_drop_list = ["Result", "Total2.5", "Total1.5", "TeamHomeStr", "TeamAwayStr", "Date", "StartTeamHome",
                         "StartTeamAway", "SubsTeamHome", "SubsTeamAway"]
    if drop_list:
        default_drop_list += drop_list

    X = matches.drop(default_drop_list, axis=1)
    y = matches[label]
    print(X, y)
    keys = X.keys()
    # Separate into train and test data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=13)
    # X_test = X_test[:20]
    # y_test = y_test[:20]
    # Scale
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    clf = svm.SVC()
    clf.fit(X_train, y_train)
    pred_clf = clf.predict(X_test)
    dump(clf, 'cvm_model.joblib')
    print(classification_report(y_test, pred_clf))
    print(confusion_matrix(y_test, pred_clf))


# learn_svm(label="Result")


def learn_neural(label="Result", drop_list=None, test_size=0.1) -> None:
    # NEURAL
    # matches = pd.read_csv("common_data.csv", delimiter=',')
    matches = pd.read_csv("common_learn_data.csv", delimiter=';')
    # Separate data
    # default_drop_list = ["Result"]
    default_drop_list = ["Result", "Total2.5", "Total1.5", "TeamHomeStr", "TeamAwayStr", "Date", "StartTeamHome", "StartTeamAway", "SubsTeamHome", "SubsTeamAway"]
    if drop_list:
        default_drop_list += drop_list

    X = matches.drop(default_drop_list, axis=1)
    y = matches[label]
    print(X, y)
    keys = X.keys()
    # Separate into train and test data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=13)
    # X_test = X_test[:20]
    # y_test = y_test[:20]
    # Scale
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    #
    mlpc = MLPClassifier(hidden_layer_sizes=(142, 142, 142), max_iter=150)
    mlpc.fit(X_train, y_train)
    # mlpc = load("neural models/n_model51.joblib")
    pred_mlpc = mlpc.predict(X_test)
    dump(mlpc, 'n_model.joblib')
    print(classification_report(y_test, pred_mlpc))
    print(confusion_matrix(y_test, pred_mlpc))


# learn_neural(label="Result")


def learn_decision(label="Result", drop_list=None, test_size=0.1) -> None:
    # matches = pd.read_csv("common_data.csv", delimiter=',')
    matches = pd.read_csv("common_learn_data.csv", delimiter=';')
    # Separate data
    # default_drop_list = ["Result"]
    default_drop_list = ["Result", "Total2.5", "Total1.5", "TeamHomeStr", "TeamAwayStr", "Date", "StartTeamHome",
                         "StartTeamAway", "SubsTeamHome", "SubsTeamAway"]
    if drop_list:
        default_drop_list += drop_list

    X = matches.drop(default_drop_list, axis=1)
    y = matches[label]
    print(X, y)

    # Players vectors
    w2v = PlayerEmbedding()
    w2v.w2v_load("5ligsS")

    all_players_names = list(w2v.get_all_vectors().keys())
    players_vecs = np.zeros([matches.shape[0], len(all_players_names)])

    for match_i in range(len(matches)):
        lineup_sh = EmbeddingData.define_players_list(matches["StartTeamHome"][match_i])
        lineup_sa = EmbeddingData.define_players_list(matches["StartTeamAway"][match_i])
        lineup_subh = EmbeddingData.define_players_list(matches["SubsTeamHome"][match_i])
        lineup_suba = EmbeddingData.define_players_list(matches["SubsTeamAway"][match_i])

        all_lineups = [lineup_subh, lineup_suba, lineup_sh, lineup_sa]

        for lineup in all_lineups:
            for player in lineup:
                player_index = all_players_names.index(player)
                players_vecs[match_i][player_index] = all_lineups.index(lineup) + 1

    X_players = pd.DataFrame(data=players_vecs, columns=all_players_names)
    X = pd.concat([X, X_players], axis=1, sort=False)
    keys = X.keys()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=13)
    # X_test = X_test[:40]
    # y_test = y_test[:40]
    # Scale
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    #
    # Decision
    dec = DecisionTreeClassifier(random_state=3)
    dec.fit(X_train, y_train)
    pred_dec = dec.predict(X_test)
    dump(dec, 'dec_model.joblib')
    print(classification_report(y_test, pred_dec))
    print(confusion_matrix(y_test, pred_dec))


# learn_decision(label="Result")
