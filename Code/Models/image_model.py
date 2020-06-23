import csv
import os
import sys
import random
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from matplotlib import pyplot
from word2vec_model import PlayerEmbedding
from data_analytics import EmbeddingData
from torch import nn
from torchvision import datasets, transforms, models
from torch.utils.data import Dataset, DataLoader


def show_image(data):
    pyplot.matshow(data)
    pyplot.show()


class CNN(nn.Module):

    def __init__(self) -> None:
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=10, kernel_size=3)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=3)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(980, 5184)
        self.fc2 = nn.Linear(5184, 3)

    def forward(self, x) -> None:
        x = F.relu(F.max_pool2d(self.conv1(x), 3))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 3))
        x = x.view(x.shape[0], -1)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return x


class ImageModel:

    train_loader = None
    test_loader = None
    valid_loader = None
    predict_loader = None

    def __init__(self, data_dir):
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.num_epochs = 8
        self.num_classes = 3
        self.batch_size = 25
        self.learning_rate = 0.001

        # define model
        self.model = CNN().to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)

        # define data loaders
        self.define_data_loaders(data_dir=data_dir)

    def define_data_loaders(self, data_dir):
        train_dir = data_dir + '/train'
        valid_dir = data_dir + '/valid'
        test_dir = data_dir + '/test'
        data_transforms = transforms.Compose([transforms.ToTensor(),
                                              transforms.Normalize([0.485, 0.456, 0.406],
                                                                   [0.229, 0.224, 0.225])])

        # Load the data_sets with ImageFolder
        training_dataset = datasets.ImageFolder(train_dir, transform=data_transforms)
        validation_dataset = datasets.ImageFolder(valid_dir, transform=data_transforms)
        testing_dataset = datasets.ImageFolder(test_dir, transform=data_transforms)
        # predict_data_set = datasets.ImageFolder(predict_dir, transform=data_transforms)

        # Using the image data_sets and the trainforms, define the data_loaders
        self.train_loader = DataLoader(training_dataset, batch_size=64, shuffle=True)
        self.valid_loader = DataLoader(validation_dataset, batch_size=32)
        self.test_loader = DataLoader(testing_dataset, batch_size=32)
        # self.predict_loader = DataLoader(predict_data_set, batch_size=32)

    def train_model(self):
        train_losses = []
        valid_losses = []

        for epoch in range(1, self.num_epochs + 1):
            # keep-track-of-training-and-validation-loss
            train_loss = 0.0
            valid_loss = 0.0

            # training-the-model
            self.model.train()
            for data, target in self.train_loader:
                # move-tensors-to-GPU
                data = data.to(self.device)
                target = target.to(self.device)

                # clear-the-gradients-of-all-optimized-variables
                self.optimizer.zero_grad()
                # forward-pass: compute-predicted-outputs-by-passing-inputs-to-the-model
                output = self.model(data)
                # calculate-the-batch-loss
                loss = self.criterion(output, target)
                # backward-pass: compute-gradient-of-the-loss-wrt-model-parameters
                loss.backward()
                # perform-a-ingle-optimization-step (parameter-update)
                self.optimizer.step()
                # update-training-loss
                train_loss += loss.item() * data.size(0)

            # validate-the-model
            self.model.eval()
            for data, target in self.valid_loader:
                data = data.to(self.device)
                target = target.to(self.device)

                output = self.model(data)

                loss = self.criterion(output, target)

                # update-average-validation-loss
                valid_loss += loss.item() * data.size(0)

            # calculate-average-losses
            train_loss = train_loss / self.batch_size
            valid_loss = valid_loss / self.batch_size
            train_losses.append(train_loss)
            valid_losses.append(valid_loss)

            # print-training/validation-statistics
            print('Epoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
                epoch, train_loss, valid_loss))

    def test_model(self):
        # test-the-model
        self.model.eval()  # it-disables-dropout
        with torch.no_grad():
            correct = 0
            total = 0
            for images, labels in self.test_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                outputs = self.model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

            print('Test Accuracy of the model: {} %'.format(100 * correct / total))

        # Save
        torch.save(self.model.state_dict(), 'model.ckpt')

    def load_model(self, model_path: str):
        self.model = torch.load(model_path)

    def predict(self):
        self.model.eval()  # it-disables-dropout
        with torch.no_grad():
            correct = 0
            total = 0
            for images, labels in self.predict_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                outputs = self.model(images)
                _, predicted = torch.max(outputs.data, 1)

                print(predicted)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()


            print('Test Accuracy of the model: {} %'.format(100 * correct / total))

        # Save
        torch.save(self.model.state_dict(), 'model.ckpt')


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

    def __init__(self, model_name="5ligs"):
        self.emb = PlayerEmbedding()
        self.emb_data = EmbeddingData()
        self.emb.w2v_load(model_name)
        self.emb.normalize_all_vectors()

    @staticmethod
    def create_dir(directory: str, sub_dir="1") -> str:
        try:
            os.mkdir(directory + '/')
        finally:
            try:
                os.mkdir(directory + '/' + sub_dir + '/')
            finally:
                return directory + '/' + sub_dir + '/'

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

    def generate_match_images(self, league_name: str, image_size=72, delimiter=1, layers=3, ratio=0.2, common_path=None):
        main_floder_name = league_name if not common_path else common_path
        directory = self.create_dir(self.MAIN_PATH + "/" + main_floder_name, sub_dir= "d" + str(delimiter) + "l" + str(layers))
        dir_train = self.create_dir(directory, sub_dir="train")
        dir_test = self.create_dir(directory, sub_dir="test")
        dir_valid = self.create_dir(directory, sub_dir="valid")
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
            image_matrix[: int(vec_size_s / 2), int(vec_size_p / 2) + 2, :] = self.DATA_MATRIX_RGB[match_i, :int(vec_size_s / 2), :]
            image_matrix[: int(vec_size_s / 2), int(vec_size_p / 2) + 3, :] = self.DATA_MATRIX_RGB[match_i, :int(vec_size_s / 2), :]
            image_matrix[: int(vec_size_s / 2), int(vec_size_p / 2) + 4, :] = self.DATA_MATRIX_RGB[match_i, :int(vec_size_s / 2), :]

            image_matrix[: int(vec_size_s / 2), int(vec_size_p / 2) + 5, :] = self.DATA_MATRIX_RGB[match_i, int(vec_size_s / 2):, :]
            image_matrix[: int(vec_size_s / 2), int(vec_size_p / 2) + 6, :] = self.DATA_MATRIX_RGB[match_i, int(vec_size_s / 2):, :]
            image_matrix[: int(vec_size_s / 2), int(vec_size_p / 2) + 7, :] = self.DATA_MATRIX_RGB[match_i, int(vec_size_s / 2):, :]
            image_matrix[: int(vec_size_s / 2), int(vec_size_p / 2) + 8, :] = self.DATA_MATRIX_RGB[match_i, int(vec_size_s / 2):, :]

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
        directory = self.create_dir(league_name) + "TESTS/"
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
            file_name = directory + "5DEL" + self.DATA_STRINGS[match_i]["Result"] + self.DATA_STRINGS[match_i]["Total2.5"] \
                + self.DATA_STRINGS[match_i]["Total1.5"] + '[' + self.DATA_STRINGS[match_i]["Date"] + ']' \
                + self.DATA_STRINGS[match_i]["TeamHomeName"] + '-' + self.DATA_STRINGS[match_i]["TeamAwayName"] + ".png"

            int_matrix = np.uint8(image_matrix)
            im = Image.fromarray(int_matrix)
            im.save(file_name)
            break


img_m = ImageModel("/Users/sanduser/PycharmProjects/Parser/Images/Common leagues/d1l3")
img_m.train_model()
img_m.test_model()
