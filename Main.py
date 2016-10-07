# -*- coding:utf-8 -*-

import time
import random


class Similarity:
    def __init__(self, med_id1=0, med_id2=0, maccs=0, fcfp4=0, ecfp4=0, topo=0, weighted_sim=0):
        self.med_molregno1 = med_id1
        self.med_molregno2 = med_id2
        self.maccs = maccs
        self.ecfp4 = ecfp4
        self.fcfp4 = fcfp4
        self.topo = topo
        self.weighted_sim = weighted_sim

    def get_simtable(self):
        return [self.med_molregno1, self.med_molregno2, self.maccs, self.ecfp4, self.fcfp4, self.topo, self.weighted_sim]

    def from_simtable(self, table):
        self.med_molregno1 = table[0]
        self.med_molregno2 = table[1]
        self.maccs = float(table[2])
        self.ecfp4 = float(table[3])
        self.fcfp4 = float(table[4])
        self.topo = float(table[5])
        self.weighted_sim = float(table[6])

    @staticmethod
    def read_similarities():
        similarities = []
        sim_file = open('result.txt')
        while 1:
            s = Similarity()
            line = sim_file.readline()
            if not line:
                break
            s.from_simtable(line.split())
            # s.print()
            similarities.append(s)
        sim_file.close()
        return similarities


class ChnMed:  # Chinese medicine class

    def __init__(self, lst):
        self.id = lst[0]
        self.chn_name = lst[1]
        self.chn_word_id = lst[2]
        self.component = lst[3]
        self.description = lst[4]
        self.chn_description = lst[5]

    # read chinese medicine data
    @staticmethod
    def read_chn_med():
        chn_med_file = open('CMedc.txt')
        chn_med = []
        while 1:
            line = chn_med_file.readline()
            if not line:
                break
            row = line.split()
            med = ChnMed(row)
            chn_med.append(med)
        chn_med_file.close()
        return chn_med

    def chn_str(self):
        return str(self.id) + ' ' + str(self.chn_name) + ' ' + str(self.chn_word_id) + ' ' +\
               str(self.component) + ' ' + str(self.description) + ' ' + str(self.chn_description)

    @staticmethod
    def write_chn_med(chn_med):
        file = open('CMedc1.txt', 'w')
        for item in chn_med:
            line = item.chn_str()
            file.write(line + '\n')
        file.close()


class WstMed:  # Western medicine class

    def __init__(self, lst):
        self.id = lst[0]  # drugs.com id
        self.name = lst[1]
        self.component = lst[2]
        self.molregno = lst[3]  # CHEMBL id
        self.smiles = lst[4]  # store medicine's SMILES notation, rather than mol object

    def wst_str(self):
        return str(self.id) + ' ' + str(self.name) + ' ' + str(self.component) + ' ' +\
               str(self.molregno) + ' ' + str(self.smiles)

    @staticmethod
    # read western medicine data
    def read_wstmed():
        wst_med_file = open('WMedc.txt')
        wst_med = []
        while 1:
            line = wst_med_file.readline()
            if not line:
                break
            row = line.split()
            med = WstMed(row)
            wst_med.append(med)
        wst_med_file.close()
        return wst_med


class Interaction:  # interaction between western medicines

    def __init__(self, lst):

        self.id = lst[0]
        self.medicine_id1 = lst[1]
        self.medicine_name1 = lst[2]
        self.medicine_id2 = lst[3]
        self.medicine_name2 = lst[4]
        self.interaction_level = lst[5]

    # read interaction data
    @staticmethod
    def read_interactions():
        interaction_file = open('interactions.txt')
        interactions = []
        while 1:
            line = interaction_file.readline()
            if not line:
                break
            row = line.split()
            inter = Interaction(row)
            interactions.append(inter)
        interaction_file.close()
        return interactions

    @staticmethod
    def write_interactions(interactions):
        interaction_file = open('interactions.txt', 'w')
        # interactions = []
        for item in interactions:
            line = item.interaction_str()
            interaction_file.write(line + '\n')
        interaction_file.close()

    def interaction_str(self):
        return self.id + ' ' + self.medicine_id1 + ' ' + self.medicine_name1 + ' ' + self.medicine_id2 + ' ' +\
               self.medicine_name2 + ' ' + self.interaction_level


class Validation:

    def __init__(self, wst_med, similarities, interaction):
        self.wst_med = wst_med
        self.sim = similarities
        self.interaction = interaction
        self.test_set = []
        self.validation_set = []

    def divide_data(self):
        self.test_set = []
        self.validation_set = []
        index = random.sample(range(0, 1366), 136)  # randomly select 1/10 data as test_set
        for i in range(0, self.wst_med.__len__()):
            if i not in index:
                self.validation_set.append(self.wst_med[i])
            else:
                self.test_set.append(self.wst_med[i])

    def __get_similarity(self, med1_id, med2_id):
        for item in self.sim:
            if item.drug1_id == med1_id and item.drug2_id == med2_id:
                return item.weighted_sim
        return -1

    def __get_interaction_level(self, med1_id, med2_id):
        for item in self.interaction:
            if item.medicine_id1 == med1_id and item.medicine_id2 == med2_id:
                return item.interaction_level
        return -1

    def find_pair(self, med_molregno1):
        # return most similar med_molregno2
        max_sim = 0
        # pair_med = WstMed([0,0,0,0,0,0])
        for sim_item in self.sim:
            if sim_item.med_molregno1 == med_molregno1:
                if sim_item.weighted_sim > max_sim:
                    for vali in self.validation_set:
                        if sim_item.med_molregno2 == vali.molregno:
                            pair_med = vali
                            max_sim = sim_item.weighted_sim
                            break
                    #pair_molregno = sim_item.med_molregno2
                    #max_sim = sim_item.weighted_sim
        return [pair_med, max_sim]

    def validate(self):
        for test_med in self.test_set:
            pair_med, pair_sim = self.find_pair(test_med.molregno)
            for known_med in self.validation_set:
                inter_level = float(self.__get_interaction_level(pair_med.id, known_med.id))
                if inter_level != -1:
                    c_index = inter_level * pair_sim
                    print(pair_med.id, known_med.id, pair_sim, c_index)


start = time.time()

# similarities = Similarity.read_similarities()
# interactions = Interaction.read_interactions()
# wst_med = WstMed.read_wstmed()
# chn_med = ChnMed.read_chn_med()
v = Validation(wst_med, similarities, interactions)
v.divide_data()


################# Generate Similarities #################
# sims = SimOperation.sim_table()
# SimOperation.write_similarities(sims)

end = time.time()
print(end - start)
