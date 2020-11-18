import json, os
import spacy
import pandas as pd
import random
from spacy.util import minibatch,compounding
from fastprogress.fastprogress import master_bar, progress_bar


def prepare_data(file_path):
    with open(file_path) as f:
        data = [json.loads(line) for line in f]
    
    train_data = []
    for doc in data:
        text = doc['text']
        entities ={'entities': doc['labels']}
        document_list = [text,entities]
        train_data.append(document_list)
    return train_data


class NamedEntityRecognizer():
    def __init__(self, data):
        self.data=data
        entities = []
        for _,doc in data:
            for start,end,name in doc.get('entities'):
                entities.append(name)
        self.entities = list(set(entities))
        nlp = spacy.blank('en')
        if 'ner' not in nlp.pipe_names:
            ner = nlp.create_pipe('ner')
            nlp.add_pipe(ner)
        else:
            ner = nlp.get_pipe('ner')

        for i in self.entities:
            ner.add_label(i)# Inititalizing optimizerif model is None:
            optimizer = nlp.begin_training()
        else:
            optimizer = nlp.entity.create_optimizer()
        self.nlp=nlp
        self.optimizer=optimizer
        
    def train(self, epochs):
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != 'ner']
        mb = master_bar(range(epochs))
        mb.write(['epoch','loss','f1','precision','recall'],table=True)
        with self.nlp.disable_pipes(*other_pipes):  # only train NER
            for itn in mb:
                random.shuffle(self.data)
                losses = {}
                batches = minibatch(self.data, 
                                    size=compounding(4., 32., 1.001))
                for batch in progress_bar(list(batches), parent=mb):
                    texts, annotations = zip(*batch) 
                    # Updating the weights
                    self.nlp.update(texts, annotations, sgd=self.optimizer, 
                            drop=0.35, losses=losses)
                loss = losses.get('ner')
                metrics = self.nlp.evaluate(self.data[:len(self.data)//5])
                f1,precision,recall = metrics.ents_f,metrics.ents_p,metrics.ents_r
                line = [str(itn,round(loss,2)),str(round(f1,2)),str(round(precision,2)),str(round(recall,2))]
                mb.write(line,table=True)
    
    def save(self,name, path='models/'):
        if not os.path.exists(path):
            os.mkdir(path)
        self.nlp.to_disk(os.path.join(path,name))
        print(f'Model has been saved to {os.path.join(path,name)}')


    def load(self, path):
        try:
            self.nlp = spacy.load(path)
            print('Model loaded successfully')
        except Exception as E:
            print(f'Failed to load the model : {E}')

    def extract_entities(self, report_path, location_mapping):

        df = pd.read_csv(location_mapping)
        df.index=df.filename

        for entity in self.entities:
            df[entity]=''
        for filename,row in progress_bar(list(df.iterrows())): 
            for entity in self.entities:
                df[entity][filename]=[]
            with open(os.path.join(report_path,filename),'r') as f:
                #print(filename)
                txt = f.read()
                doc = self.nlp(txt)
                
                for entity in doc.ents:
                    en_txt = entity.text
                    df[entity.label_][filename].append(en_txt)
        return df







            

