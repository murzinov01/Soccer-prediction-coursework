import csv
import numpy as np
import pandas as pd
import seaborn as sb
import random
import PIL
from PIL import Image
from matplotlib import image
from matplotlib import pyplot
from word2vec_model import PlayerEmbedding
from data_analytics import EmbeddingData

import torch
from torch import nn
from torch import optim
import torch.nn.functional as F
from torchvision import datasets, transforms, models
from collections import OrderedDict
from torch.utils.data import Dataset, DataLoader

import multiprocessing
from numpy import asarray
import os
import sys

#np.set_printoptions(threshold=sys.maxsize)


def show_image(data):
    pyplot.matshow(data)
    pyplot.show()

class ImageModel():
    train_loader = None
    test_loader = None
    valid_loader = None

    def __init__(self):
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    def define_data_loaders(self, data_dir):
        train_dir = data_dir + '/train'
        valid_dir = data_dir + '/valid'
        test_dir = data_dir + '/test'
        data_transforms = transforms.Compose([transforms.ToTensor(),
                                              transforms.Normalize([0.485, 0.456, 0.406],
                                                                   [0.229, 0.224, 0.225])])

        # Load the datasets with ImageFolder
        training_dataset = datasets.ImageFolder(train_dir, transform=data_transforms)
        validation_dataset = datasets.ImageFolder(valid_dir, transform=data_transforms)
        testing_dataset = datasets.ImageFolder(test_dir, transform=data_transforms)

        # Using the image datasets and the trainforms, define the dataloaders
        train_loader = DataLoader(training_dataset, batch_size=64, shuffle=True)
        validate_loader = DataLoader(validation_dataset, batch_size=32)
        test_loader = DataLoader(testing_dataset, batch_size=32)


class ImageGenerator:

    MIN_MAX_VAL = {

        "League": [0.0, 20.0], "Time": [0.0, 24.0], "TeamHome": [0.0, 300.0], "TeamAway": [0.0, 300.0],
        "ManagerHome": [0.0, 300.0], "ManagerAway": [0.0, 300.0], "FormationHome": [0.0, 100.0], "FormationAway":  [0.0, 100.0], "Stadium":  [0.0, 300.0], "Referee":  [0.0, 300.0],

        "RatingStartTeamHome":  [0.0, 10.0], "RatingSubstitutionHome": [0.0, 10.0],
        "RatingStartTeamAway": [0.0, 10.0], "RatingSubstitutionAway": [0.0, 10.0],
        "RatingStartTeamHome3": [0.0, 10.0], "RatingSubstitutionHome3": [0.0, 10.0],
        "RatingStartTeamAway3": [0.0, 10.0], "RatingSubstitutionAway3": [0.0, 10.0],
        "GPP_StartHome": [0.0, 50.0], "GPP_SubsHome": [0.0, 50.0], "GPP_StartAway": [0.0, 50.0], "GPP_SubsAway": [0.0, 50.0],

        "GoalsTeamHome": [0.0, 200.0], "AssistsTeamHome": [0.0, 200.0], "GoalsTeamAway": [0.0, 200.0], "AssistsTeamAway": [0.0, 200.0],

        "FormTeamHome3": [0.0, 100.0], "FormTeamAway3": [0.0, 100.0], "FormTeamHome6": [0.0, 100.0], "FormTeamAway6": [0.0, 100.0],

        # local stats (Only Home or Away)
        "RatingTeamHome": [0.0, 10.0], "RatingTeamAway": [0.0, 10.0],
        "TotalShotsHome": [0.0, 40.0], "TotalShotsAway": [0.0, 40.0], "PossessionHome": [0.0, 100.0], "PossessionAway": [0.0, 100.0],
        "PassAccuracyHome": [0.0, 100.0], "PassAccuracyAway": [0.0, 100.0], "DribblesHome": [0.0, 30.0], "DribblesAway": [0.0, 30.0],
        "AerialsWonHome": [0.0, 60.0], "AerialsWonAway": [0.0, 60.0], "TacklesHome": [0.0, 50.0], "TacklesAway": [0.0, 50.0],
        "CornersHome": [0.0, 20.0], "CornersAway": [0.0, 20.0], "DispossessedHome": [0.0, 30.0], "DispossessedAway": [0.0, 30.0],
        "YellowCardHome": [0.0, 60.0], "YellowCardAway": [0.0, 60.0], "RedCardHome": [0.0, 30.0], "RedCardAway": [0.0, 30.0],

        # average stats (Home + Away)
        "RatingTeamHomeA": [0.0, 10.0], "RatingTeamAwayA": [0.0, 10.0],
        "TotalShotsHomeA": [0.0, 40.0], "TotalShotsAwayA": [0.0, 40.0], "PossessionHomeA": [0.0, 100.0], "PossessionAwayA": [0.0, 100.0],
        "PassAccuracyHomeA": [0.0, 100.0], "PassAccuracyAwayA": [0.0, 100.0], "DribblesHomeA": [0.0, 30.0], "DribblesAwayA": [0.0, 30.0],
        "AerialsWonHomeA": [0.0, 60.0], "AerialsWonAwayA": [0.0, 60.0], "TacklesHomeA": [0.0, 50.0], "TacklesAwayA": [0.0, 50.0],
        "CornersHomeA": [0.0, 20.0], "CornersAwayA": [0.0, 20.0], "DispossessedHomeA": [0.0, 30.0], "DispossessedAwayA": [0.0, 30.0],
        "YellowCardHomeA": [0.0, 60.0], "YellowCardAwayA": [0.0, 60.0], "RedCardHomeA": [0.0, 30.0], "RedCardAwayA": [0.0, 30.0],

        # same but for 3 last match
        "RatingTeamHome3": [0.0, 10.0], "RatingTeamAway3": [0.0, 10.0],
        "TotalShotsHome3": [0.0, 40.0], "TotalShotsAway3": [0.0, 40.0], "PossessionHome3": [0.0, 100.0], "PossessionAway3": [0.0, 100.0],
        "PassAccuracyHome3": [0.0, 100.0], "PassAccuracyAway3": [0.0, 100.0], "DribblesHome3": [0.0, 30.0], "DribblesAway3": [0.0, 30.0],
        "AerialsWonHome3": [0.0, 60.0], "AerialsWonAway3": [0.0, 60.0], "TacklesHome3": [0.0, 50.0], "TacklesAway3": [0.0, 50.0],
        "CornersHome3": [0.0, 20.0], "CornersAway3": [0.0, 20.0], "DispossessedHome3": [0.0, 30.0], "DispossessedAway3": [0.0, 30.0],
        "YellowCardHome3": [0.0, 60.0], "YellowCardAway3": [0.0, 60.0], "RedCardHome3": [0.0, 30.0], "RedCardAway3": [0.0, 30.0],

        "RatingTeamHome3A": [0.0, 10.0], "RatingTeamAway3A": [0.0, 10.0],
        "TotalShotsHome3A": [0.0, 40.0], "TotalShotsAway3A": [0.0, 40.0], "PossessionHome3A": [0.0, 100.0], "PossessionAway3A": [0.0, 100.0],
        "PassAccuracyHome3A": [0.0, 100.0], "PassAccuracyAway3A": [0.0, 100.0], "DribblesHome3A": [0.0, 30.0], "DribblesAway3A": [0.0, 30.0],
        "AerialsWonHome3A": [0.0, 60.0], "AerialsWonAway3A": [0.0, 60.0], "TacklesHome3A": [0.0, 50.0], "TacklesAway3A": [0.0, 50.0],
        "CornersHome3A": [0.0, 20.0], "CornersAway3A": [0.0, 20.0], "DispossessedHome3A": [0.0, 30.0], "DispossessedAway3A": [0.0, 30.0],
        "YellowCardHome3A": [0.0, 60.0], "YellowCardAway3A": [0.0, 60.0], "RedCardHome3A": [0.0, 30.0], "RedCardAway3A": [0.0, 30.0],

        "PHome": [0.0, 58.0], "WHome": [0.0, 58.0], "DHome": [0.0, 58.0], "LHome": [0.0, 58.0], "GFHome": [0.0, 200.0], "GAHome": [0.0, 150.0], "GDHome": [-150.0, 150.0], "PointsHome": [0.0, 150.0],
        "PlaceHome": [-1.0, 30.0],
        "PAway": [0.0, 58.0], "WAway": [0.0, 58.0], "DAway": [0.0, 58.0], "LAway": [0.0, 58.0], "GFAway": [0.0, 200.0], "GAAway": [0.0, 150.0], "GDAway": [-150.0, 150.0], "PointsAway": [0.0, 150.0],
        "PlaceAway": [-1.0, 30.0],

        "FutureTeamHome": [0.0, 300.0], "FuturePlaceTeamHome": [-1.0, 30.0], "FutureStatusTeamHome": [0.0, 2.0],
        "FutureTeamAway": [0.0, 300.0], "FuturePlaceTeamAway": [-1.0, 30.0], "FutureStatusTeamAway": [0.0, 2.0]

    }
    MAIN_PATH = "/Users/sanduser/PycharmProjects/Parser/Images"
    DATA_MATRIX = None
    DATA_MATRIX_RGB = None
    DATA_STRINGS = None

    def __init__(self, model_name="5ligsS"):
        self.emb = PlayerEmbedding()
        self.emb_data = EmbeddingData()
        self.emb.w2v_load(model_name)
        self.emb.normalize_all_vectors()

    def create_dir(self, dir: str, sub_dir="1") -> str:
        try:
            os.mkdir(dir + '/')
        finally:
            try:
                os.mkdir(dir + '/' + sub_dir + '/')
            finally:
                return dir + '/' + sub_dir + '/'

    def generate_league_stats(self, league_name: str):
        self.DATA_STRINGS = list()
        with open(league_name + "_learn_data.csv", 'r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file, delimiter=';')
            for match in reader:
                match_data = {
                    "Date": match["Date"],
                    "TeamHomeName": match["TeamHomeStr"],
                    "TeamAwayName": match["TeamAwayStr"],
                    "StartTeamHome": match["StartTeamHome"],
                    "StartTeamAway": match["StartTeamAway"],
                    "SubsTeamHome": match["SubsTeamHome"],
                    "SubsTeamAway": match["SubsTeamAway"],
                    "Result": match["Result"],
                    "Total2.5": match["Total2.5"],
                    "Total1.5": match["Total1.5"]
                }
                self.DATA_STRINGS.append(match_data)
            field_names = reader.fieldnames[10:]
        self.DATA_MATRIX = np.genfromtxt(league_name + "_learn_data.csv", delimiter=';')
        self.DATA_MATRIX = self.DATA_MATRIX[1:, 10:]


        RGB_MATRIX = np.zeros([self.DATA_MATRIX.shape[0], self.DATA_MATRIX.shape[1], 3])

        for column_i in range(self.DATA_MATRIX.shape[1]):
            vec = self.DATA_MATRIX[:, column_i]
            column_name = field_names[column_i]
            norm_vec = self.emb.normalize_vector(vec, min_value=self.MIN_MAX_VAL[column_name][0],
                                                                        max_value=self.MIN_MAX_VAL[column_name][1])
            rgb_vec = self.emb.convert_to_rgb(norm_vec)
            RGB_MATRIX[:, column_i, :] = rgb_vec
            self.DATA_MATRIX_RGB = RGB_MATRIX

    def generate_match_images(self, league_name: str, image_size=72, delimiter=1, layers=3, ratio=0.2):
        dir = self.create_dir(self.MAIN_PATH + "/" + league_name, sub_dir= "d" + str(delimiter) + "l" + str(layers))
        dir_train = self.create_dir(dir, sub_dir="train")
        dir_test = self.create_dir(dir, sub_dir="test")
        dir_valid = self.create_dir(dir, sub_dir="valid")
        directories = {
            "Te1": self.create_dir(dir_test, sub_dir="1"),
            "Te2": self.create_dir(dir_test, sub_dir="2"),
            "Te3": self.create_dir(dir_test, sub_dir="0"),
            "Tr1": self.create_dir(dir_train, sub_dir="1"),
            "Tr2": self.create_dir(dir_train, sub_dir="2"),
            "Tr3": self.create_dir(dir_train, sub_dir="0"),
            "V1": self.create_dir(dir_valid, sub_dir="1"),
            "V2": self.create_dir(dir_valid, sub_dir="2"),
            "V3": self.create_dir(dir_valid, sub_dir="0"),
        }

        self.generate_league_stats(league_name)

        matches_num = self.DATA_MATRIX_RGB.shape[0]
        print("ДО:", matches_num)
        matches_split_test = random.sample(list(range(matches_num)), k=int(matches_num * ratio))

        matches_split = list()
        for match in list(range(matches_num)):
            if match not in matches_split_test:
                matches_split.append(match)

        matches_split_valid = random.sample(matches_split, k= int(len(matches_split) * ratio))

        matches_split_train = list()
        for match in matches_split:
            if match not in matches_split_valid:
                matches_split_train.append(match)

        print("После:", len(matches_split_train) + len(matches_split_valid) + len(matches_split_test))

        for match_i in range(matches_num):
            sys.stdout.write(f"\r| {match_i} / {matches_num-1}")
            sys.stdout.flush()

            image_matrix = np.zeros([image_size, image_size, 3])
            image_matrix[:, :, :] = 255

            # fill players vectors
            start_home = self.emb_data.define_players_list(self.DATA_STRINGS[match_i]["StartTeamHome"])
            start_away = self.emb_data.define_players_list(self.DATA_STRINGS[match_i]["StartTeamAway"])
            subs_home = self.emb_data.define_players_list(self.DATA_STRINGS[match_i]["SubsTeamHome"])
            subs_away = self.emb_data.define_players_list(self.DATA_STRINGS[match_i]["SubsTeamAway"])

            line_counter = 0
            vec_size_p = self.emb.VEC_SIZE
            for line_up in (start_home, subs_home[:7], start_away, subs_away[:7]):
                for player in line_up:
                    vec_n = self.emb.NORMALIZED_VECTORS[player] / delimiter
                    if layers == 2:
                        vec_rgb = self.emb.convert_to_rg(vec_n)
                    else:
                        vec_rgb = self.emb.convert_to_rgb(vec_n)

                    image_matrix[line_counter, : int(vec_size_p / 2), :] = vec_rgb[: int(vec_size_p / 2), :]
                    line_counter += 1
                    image_matrix[line_counter, : int(vec_size_p / 2), :] = vec_rgb[int(vec_size_p / 2):, :]
                    line_counter += 1

            # fill stats
            vec_size_s = self.DATA_MATRIX_RGB.shape[1]
            image_matrix[: int(vec_size_s / 2), int(vec_size_p / 2) + 1, :] = self.DATA_MATRIX_RGB[match_i, :int(vec_size_s / 2), :]
            image_matrix[: int(vec_size_s / 2), int(vec_size_p / 2) + 2, :] = self.DATA_MATRIX_RGB[match_i, int(vec_size_s / 2):, :]

            result = self.DATA_STRINGS[match_i]["Result"]
            selection = ""
            if match_i in matches_split_train:
                selection = "train"
            elif match_i in matches_split_test:
                selection = "test"
            elif match_i in matches_split_valid:
                selection = "valid"

            match_dir = dir + selection + '/' + result + '/'
            # create file name
            file_name = match_dir + self.DATA_STRINGS[match_i]["Result"] + self.DATA_STRINGS[match_i]["Total2.5"] \
                        + self.DATA_STRINGS[match_i]["Total1.5"] + '[' + self.DATA_STRINGS[match_i]["Date"] + ']' \
                        + self.DATA_STRINGS[match_i]["TeamHomeName"] + '-' + self.DATA_STRINGS[match_i]["TeamAwayName"]\
                        + ".png"

            int_matrix = np.uint8(image_matrix)
            im = Image.fromarray(int_matrix)
            im.save(file_name)

    def generate_match_images_test(self, league_name: str, image_size=72):
        dir = self.create_dir(league_name) + "TESTS/"
        self.generate_league_stats(league_name)

        for match_i in range(self.DATA_MATRIX_RGB.shape[0]):

            image_matrix = np.zeros([image_size, image_size, 3])
            image_matrix[:, :, :] = 255

            # fill players vectors
            start_home = self.emb_data.define_players_list(self.DATA_STRINGS[match_i]["StartTeamHome"])
            start_away = self.emb_data.define_players_list(self.DATA_STRINGS[match_i]["StartTeamAway"])
            subs_home = self.emb_data.define_players_list(self.DATA_STRINGS[match_i]["SubsTeamHome"])
            subs_away = self.emb_data.define_players_list(self.DATA_STRINGS[match_i]["SubsTeamAway"])

            line_counter = 0
            vec_size_p = self.emb.VEC_SIZE
            for line_up in (start_home, subs_home, start_away, subs_away):
                for player in line_up:
                    vec_n = self.emb.NORMALIZED_VECTORS[player] / 5
                    vec_rgb = self.emb.convert_to_rgb(vec_n)

                    image_matrix[line_counter, : int(vec_size_p), :] = vec_rgb[: int(vec_size_p)]
                    line_counter += 1
                line_counter += 1
            # fill stats

            # create file name
            file_name = dir + "5DEL" + self.DATA_STRINGS[match_i]["Result"] + self.DATA_STRINGS[match_i]["Total2.5"] \
                        + self.DATA_STRINGS[match_i]["Total1.5"] + '[' + self.DATA_STRINGS[match_i]["Date"] + ']' \
                        + self.DATA_STRINGS[match_i]["TeamHomeName"] + '-' + self.DATA_STRINGS[match_i]["TeamAwayName"] \
                        +".png"

            int_matrix = np.uint8(image_matrix)
            im = Image.fromarray(int_matrix)
            im.save(file_name)
            break

#
# img_gen = ImageGenerator()
# img_gen.generate_match_images("LaLiga (Spain)")
# img_gen.generate_match_images("LaLiga (Spain)", delimiter=10, layers=3)

# league_list = ("Premier League (Russia)", "LaLiga (Spain)", "Serie A (Italy)", "Super Lig (Turkey)")
#
# for league in league_list:
#     print("League: ", league)
#     img_gen.generate_match_images(league, image_size=72)
#     img_gen.generate_match_images(league, image_size=72, delimiter=2, layers=3)
#     img_gen.generate_match_images(league, image_size=72, delimiter=10, layers=3)
#     img_gen.generate_match_images(league, image_size=72, delimiter=100, layers=3)
#     img_gen.generate_match_images(league, image_size=72, delimiter=1, layers=2)


# Emb = PlayerEmbedding()
# Emb.w2v_load()
# Emb.normalize_all_vectors()
#
# rgb_img_matrix = np.zeros((80, Emb.VEC_SIZE, 3))
# print(rgb_img_matrix.shape)
#
# count = 0
# for vec in Emb.NORMALIZED_VECTORS.values():
#     rgb_img_matrix[count] += Emb.convert_to_rgb(vec)
#     if count >= 79:
#         break
#     count += 1
#
# print(rgb_img_matrix)


# new_array = np.uint8(image_matrix)
# #
# im = Image.fromarray(new_array)
# im.show()
# im.save("doska.png")

# matrix = np.array([[0] * 3])
# matrix = np.append(matrix, [[0, 1, 2]], axis=0)
# matrix = np.append(matrix, [[3, 4, 5]], axis=0)
# print("Matrix:", matrix, "Shape:", matrix.shape)



