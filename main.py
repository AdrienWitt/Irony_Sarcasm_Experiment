# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 15:49:48 2023

@author: wittmann
"""

import os
from Utility import LoadStimuli
from Utility import IronicityExperiment

path = r'C:\Users\wittmann\OneDrive - unige.ch\Documents\Sarcasm_experiment\Adrien\Study_Python'
os.chdir(path)

def Experiment():
    stimuli_dir = path + '\Stimuli'
    loader = LoadStimuli(stimuli_dir, prosodies=('neg', 'pos', 'mon'))
    all_random = loader.all_random_dataframe()
    IronicityExperiment(all_random, stimuli_dir).main()
    
if __name__ == '__main__':
    Experiment()



