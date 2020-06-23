import numpy as np
import random
from gensim.models import Word2Vec
from data_analytics import EmbeddingData as ed


# WORD2VEC
class PlayerEmbedding:

    MODEL = None
    NORMALIZED_VECTORS = None
    VEC_SIZE = 0

    def w2v_train(self, leagues: list, model_name="w2v", vec_size=138) -> None:
        # make sentences
        assembler = ed()
        for league_name in leagues:
            assembler.make_sentences_list(league_name)
        sentences = assembler.DATA
        random.shuffle(sentences)
        # train
        self.MODEL = Word2Vec(sentences, size=vec_size, window=10, min_count=1, workers=4)
        self.VEC_SIZE = vec_size
        self.MODEL.save(model_name + ".model")

    def w2v_load(self, model_name="w2v") -> None:
        self.MODEL = Word2Vec.load(model_name + ".model")
        self.VEC_SIZE = self.MODEL.vector_size

    def get_player_vector(self, player_name: str):
        if self.MODEL is None:
            return 0
        else:
            return self.MODEL.wv.get_vector(player_name)

    def get_all_vectors(self) -> dict:
        all_vectors = dict()
        for player_name in self.MODEL.wv.vocab.keys():
            all_vectors[player_name] = self.get_player_vector(player_name)
        return all_vectors

    def normalize_all_vectors(self) -> dict:
        all_vectors = self.get_all_vectors()

        max_value = 0
        min_value = 0
        for vec in all_vectors.values():
            min_v = np.min(vec)
            max_v = np.max(vec)
            if min_v < min_value:
                min_value = min_v
            if max_v > max_value:
                max_value = max_v
        print("Max -> Min: ", max_value, min_value)

        for key in all_vectors.keys():
            all_vectors[key] = (all_vectors[key] + abs(min_value)) / (max_value + abs(min_value))

        self.NORMALIZED_VECTORS = all_vectors
        return all_vectors

    @staticmethod
    def normalize_vector(data_vector, min_value=0.0, max_value=0.0):
        min_v = np.min(data_vector) if not min_value else min_value
        max_v = np.max(data_vector) if not max_value else max_value
        return (data_vector + abs(min_v)) / (max_v + abs(min_v))

    @staticmethod
    def convert_to_rgb(vec):
        rgb_vec = np.zeros([vec.shape[0], 3])

        new_vec = vec * 16777215
        new_vec = np.array(list(map(int, new_vec)))
        new_vec = np.array(list(map(hex, new_vec)))
        new_vec = np.array(list(map(str, new_vec)))
        list_vec = list(map(lambda x: x[2:], new_vec))
        new_list_vec = list()

        counter_index = 0
        for dim in list_vec:
            if len(dim) < 6:
                less_len = 6 - len(dim)
                new_list_vec.append('0' * less_len + dim)
            else:
                new_list_vec.append(dim)
            red = int("0x" + new_list_vec[-1][:2], 16)
            green = int("0x" + new_list_vec[-1][2:4], 16)
            blue = int("0x" + new_list_vec[-1][4:], 16)
            rgb_vec[counter_index, 0] = red
            rgb_vec[counter_index, 1] = green
            rgb_vec[counter_index, 2] = blue
            counter_index += 1

        return rgb_vec

    @staticmethod
    def convert_to_rg(vec):
        rgb_vec = np.zeros([vec.shape[0], 3])

        new_vec = vec * 65535
        new_vec = np.array(list(map(int, new_vec)))
        new_vec = np.array(list(map(hex, new_vec)))
        new_vec = np.array(list(map(str, new_vec)))
        list_vec = list(map(lambda x: x[2:], new_vec))
        new_list_vec = list()

        counter_index = 0
        for dim in list_vec:
            if len(dim) < 4:
                less_len = 4 - len(dim)
                new_list_vec.append('0' * less_len + dim)
            else:
                new_list_vec.append(dim)
            red = int("0x" + new_list_vec[-1][:2], 16)
            green = int("0x" + new_list_vec[-1][2:4], 16)
            blue = 255
            rgb_vec[counter_index, 0] = red
            rgb_vec[counter_index, 1] = green
            rgb_vec[counter_index, 2] = blue
            counter_index += 1

        return rgb_vec
