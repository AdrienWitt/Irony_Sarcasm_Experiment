import os
import librosa
import numpy as np
import pandas as pd
import random
from psychopy import visual, core, event, sound, gui, clock, prefs
   
class LoadStimuli:
    def __init__(self, stimuli_dir, num_repeats = 1, voices=('h1', 'h2', 'h3', 'h4', 'f1', 'f2', 'f3', 'f4'), contexts=('CP', 'CN'), statements=('SP', 'SN'), prosodies=('neg', 'pos')):
        self.voices = voices
        self.contexts = contexts
        self.statements = statements
        self.prosodies = prosodies
        self.stimuli_dir = stimuli_dir
        self.num_repeats = num_repeats

    def load_stimuli_dataframe(self):
        post = '.wav'
        stimuli_list = []

        for sit in range(1, 17):
            for item in self.contexts + self.statements:
                for voice in self.voices:                   
                        if item in self.contexts:
                            filename = os.path.join(self.stimuli_dir, item + voice + '_' + str(sit) + post)
                            name = item + voice + '_' + str(sit) + post
                            if os.path.exists(filename):
                                time = librosa.get_duration(path=filename)
                                stimuli_list.append({'name': name, 'type':'context', 'condition':item, 'time': time, 'situation': sit, 'voice': voice, 'prosody': None})
                        else:
                            for prosody in self.prosodies:
                                filename = os.path.join(self.stimuli_dir, item + prosody + voice + '_' + str(sit) + post)
                                name = item + prosody + voice + '_' + str(sit) + post
                                if os.path.exists(filename):
                                    time = librosa.get_duration(path=filename)
                                    stimuli_list.append({'name': name, 'type':'statement','condition':item, 'time': time, 'situation': sit, 'voice': voice, 'prosody': prosody})
      
                              
        stimuli_df = pd.DataFrame(stimuli_list)
        
        return stimuli_df
    
    def all_random_dataframe(self, randomized=True):
        
        df = self.load_stimuli_dataframe()
        all_random = []
        
        for sit in range(1, 17):
            for context in self.contexts:
                for statement in self.statements:
                    for prosody in self.prosodies:
                        voice_context, voice_statement = self.random_voices()
                        selected_context = df.loc[(df['condition'] == context) & (df['voice'] == voice_context) & (df['situation'] == sit)]
                        selected_statement = df.loc[(df['condition'] == statement) & (df['voice'] == voice_statement) & (df['situation'] == sit)]
                        condition_name = context + '_' + statement + prosody
                        all_random.append({'condition_name': condition_name, 'situation': sit, 'context': selected_context['name'].values[0], 'statement': selected_statement['name'].values[0], 'time_context': selected_context['time'].values[0], 'time_statement': selected_statement['time'].values[0], 'voice_context': voice_context, 'voice_statement': voice_statement, 'prosody' : prosody})
                        
        all_random_df = pd.DataFrame(all_random)           
        if randomized == True:
            all_random_df = all_random_df.sample(frac=1).reset_index(drop=True)
        
        return all_random_df

    def random_voices(self):
        # choose a voice for the context
        voice_context = random.choice(self.voices)
        
        # choose a voice for the statement that is different from the context
        voice_statement = random.choice([voice for voice in self.voices if voice != voice_context])
        
        return voice_context, voice_statement
                
               
    def matrix_random_voices(self, num_repeats, stim_number):
        # Define the number of voices
        num_voices = 8
        # Initialize the data matrix
        voices_matrix = np.zeros((stim_number, 2, num_repeats))
        for repeat_idx in range(num_repeats):
            # Generate the vector of possible statement voices
            possible_statement_voices = np.setdiff1d(np.arange(1, num_voices + 1), voices_matrix[:, 0, repeat_idx])
            for conv_idx in range(stim_number):
                # Randomly choose the context voice
                context_voice = np.random.randint(1, num_voices + 1)
                # Randomly choose the statement voice from the possible options
                statement_voice = np.random.choice(possible_statement_voices)
                # Update the data matrix
                voices_matrix[conv_idx, 0, repeat_idx] = context_voice
                voices_matrix[conv_idx, 1, repeat_idx] = statement_voice
                # Update the list of possible statement voices for the next iteration
                possible_statement_voices = np.setdiff1d(np.arange(1, num_voices + 1), context_voice)  
        return voices_matrix
    
    def select_condition(self, conditions = 'all'):
        if conditions == 'all':
            all_random = self.all_random_dataframe()
        else:
            all_random[all_random['condition'].isin(conditions)]
            
        return all_random
            
class IronicityExperiment:
    def __init__(self, stimuli_df, stimuli_path, instructions_irony=None, instructions_sarcasm=None, **kwarg):
        self.stimuli_df = stimuli_df
        self.stimuli_path = stimuli_path
        self.win =  self.win = visual.Window(fullscr=True, screen=1, 
        winType='pyglet', allowStencil=False,
        monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
        blendMode='avg', useFBO=True, 
        units='height')
        self.log = []
        self.ID, self.folder_name = self.create_participant_folder()
        self.df_irony_1, self.df_irony_2 = self.random_split(self.stimuli_df)
        self.df_sarcasm_1, self.df_sarcasm_2 = self.random_split(self.stimuli_df)
        self.instructions_irony = 'Press key irony'
        self.instructions_sarcasm = 'Press key sarcasm'
        self.labels_sarcasm = ['Pas du tout sarcastique', 'Peu sarcastique', 'Modérément sarcastique', 'Sarcastique', 'Très sarcastique']  
        self.labels_irony = ['Pas du tout ironique', 'Peu ironique', 'Modérément ironique', 'Ironique', 'Très ironique']  
        self.tasks = ["irony", "sarcasm"]
        self.intask_instructions = "Après avoir entendu la deuxième phrase, veuillez indiquer à l'aide du curseur si celle-ci vous paraît"
        self.keys = event.getKeys()
        self.tasks = random.sample(self.tasks, 2)     

        
    def main(self):
        self.run(getattr(self, f'df_{self.tasks[1]}_1'), getattr(self, f'instructions_{self.tasks[1]}'), getattr(self, f'labels_{self.tasks[1]}'), run = 1, task = self.tasks[1])
        self.run(getattr(self, f'df_{self.tasks[2]}_1'), getattr(self, f'instructions_{self.tasks[2]}'), getattr(self, f'labels_{self.tasks[2]}'), run = 2, task = self.tasks[2])
        self.run(getattr(self, f'df_{self.tasks[1]}_2'), getattr(self, f'instructions_{self.tasks[1]}'), getattr(self, f'labels_{self.tasks[1]}'), run = 3, task = self.tasks[1])
        self.run(getattr(self, f'df_{self.tasks[2]}_2'), getattr(self, f'instructions_{self.tasks[2]}'), getattr(self, f'labels_{self.tasks[2]}'), run = 4, task = self.tasks[2])
    
    def run(self, stimuli_df, instruction_text, scale_labels, run, task):
        self.show_instructions(instruction_text)
        for i in range(len(self.stimuli_df)):
            self.play_context(i)
            self.show_break()
            self.play_statement(i)
            self.get_evaluation(scale_labels)
            self.save_log(i, run, task)
                                 
    def show_instructions(self, instruction_text):
        text = visual.TextStim(self.win, text = instruction_text, height=0.1)
        text.draw()
        self.win.flip()
        event.waitKeys()

    def play_context(self, i):
        self.context = sound.Sound(os.path.join(self.stimuli_path, self.stimuli_df.loc[i, 'context']))
        background = visual.ImageStim(self.win, image='imageHP.jpg')
        background.draw()
        self.win.flip()
        self.context.play()
        core.wait(self.stimuli_df.loc[i, 'time_context'])
        self.win.flip()

    def show_break(self):
        fixation = visual.TextStim(self.win, text='+', height=0.1)
        fixation.draw()
        self.win.flip()
        core.wait(1)
        self.win.flip()

    def play_statement(self, i):
        self.statement = sound.Sound(os.path.join(self.stimuli_path, self.stimuli_df.loc[i, 'statement']))
        background = visual.ImageStim(self.win, image='imageHP.jpg')
        background.draw()
        self.win.flip()
        self.statement.play()
        core.wait(self.stimuli_df.loc[i, 'time_statement'])
        self.win.flip()

    def get_evaluation(self, scale_labels):
        ratingScale = visual.RatingScale(
        self.win, low=1, high=5, markerStart=random.randint(1,len(scale_labels)),
        leftKeys='left', rightKeys = 'right', acceptKeys='space', acceptSize = 1.6, acceptText = "Validé", acceptPreText = 'Valider avec espace',  choices = scale_labels, stretch = 2.6)    
        item = visual.TextStim(self.win, self.intask_instructions, height = .04, wrapWidth = 1.5)  
        event.clearEvents()
        while ratingScale.noResponse:
                item.draw()
                ratingScale.draw()
                self.win.flip() 
        core.wait(0.5)
        self.scale_validated = True
        self.evaluation, self.RT = ratingScale.getRating(), ratingScale.getRT()
        
        
    def create_participant_folder(self):
        ID = 1
        while True:
            folder_name = f"p{ID}"
            folder_path = f"data/{folder_name}"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                return ID, folder_name
            ID += 1
        
    def save_log(self, i, run, task):
        self.log.append((self.ID, run, task, *self.stimuli_df.iloc[i], self.evaluation, self.RT, self.scale_validated))
        log_df = pd.DataFrame(self.log, columns=['ID', 'run', 'task'] + list(self.stimuli_df.columns) + ['evaluation', 'RT', 'scale_validated'])
        log_df.to_csv(f"data/{self.folder_name}/{self.ID}_run{run}.csv", index=False)
        
    def random_split(self, stimuli_df):
        random.seed(random.randint(1, 1000000))
        df_shuffled = stimuli_df.sample(frac=1)
        half = len(df_shuffled) // 2
        df_first_half = df_shuffled.iloc[:half, :]
        df_second_half = df_shuffled.iloc[half:, :]
        return df_first_half, df_second_half
    

               

        
        
        

 

            
        
        


        
        
        
        

    
                                                        
                                        
