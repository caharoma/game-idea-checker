from transformers import set_seed, GPT2Tokenizer, GPT2Config, GPT2Tokenizer, GPT2ForSequenceClassification
import torch
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

set_seed(1)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
labels_ids = {'0':0,'1':1,'2':2,'3':3}
max_length = 60
batch_size=32

model_config = GPT2Config.from_pretrained(pretrained_model_name_or_path='model/gpt2_games_description_score/config.json')
tokenizer = GPT2Tokenizer.from_pretrained(pretrained_model_name_or_path='model/gpt2_games_description_score/tokenizer')
tokenizer.padding_size = "left"
tokenizer.pad_token = tokenizer.eos_token

model = GPT2ForSequenceClassification.from_pretrained(pretrained_model_name_or_path='model/gpt2_games_description_score/')
model.resize_token_embeddings(len(tokenizer))
model.config.pad_token_id = model.config.eos_token_id
model.to(device)

class DescriptionsDataset(Dataset):
  def __init__(self, text, use_tokenizer):
    self.text = text
    self.labels = [0]
    self.n_examples = len(self.labels)
    return

  def __len__(self):
    return len(self.text)

  def __getitem__(self, item):
    return {'text':self.text, 'label':0}
  

class Gpt2ClassificationCollator(object):
  def __init__(self, use_tokenizer, labels_encoder, max_sequence_len=None):
    self.use_tokenizer = use_tokenizer
    self.max_sequence_len = use_tokenizer.model_max_length if max_sequence_len is None else max_sequence_len
    self.labels_encoder = labels_encoder
    return
  
  def __call__(self, sequences):
    texts = [sequence['text'] for sequence in sequences]
    A_labels = [sequence['label'] for sequence in sequences]
    labels = [self.labels_encoder[str(label)] for label in A_labels]
    inputs = self.use_tokenizer(text=texts, return_tensors="pt", padding=True, truncation=True, max_length=self.max_sequence_len)
    inputs.update({'labels':torch.tensor(labels)})
    return inputs

def predict(dataloader, device):
    global model
    model.eval()
    predictions_labels = []
    
    for batch in tqdm(dataloader, total=len(dataloader)):
        batch = {k:v.type(torch.long).to(device) for k,v in batch.items()}
        with torch.no_grad():
            outputs = model(**batch)
            _, logits = outputs[:2]
            predictions_labels += logits.argmax(axis=-1).flatten().tolist()
    return predictions_labels[0]

#x = 'colorful ping pong - the game in which you have to navigate the colorful ball and hit the block with the same color that block is and getting a high score by doing that '

#gpt2_classification_collator = Gpt2ClassificationCollator(use_tokenizer=tokenizer, max_sequence_len=max_length, labels_encoder=labels_ids)
#valid_dataset = DescriptionsDataset(x,use_tokenizer=tokenizer)
#valid_dataloader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=False, collate_fn=gpt2_classification_collator)


#print(predict(valid_dataloader, device))
def get_score(prompt):
  gpt2_classification_collator = Gpt2ClassificationCollator(use_tokenizer=tokenizer, max_sequence_len=max_length, labels_encoder=labels_ids)
  valid_dataset = DescriptionsDataset(prompt,use_tokenizer=tokenizer)
  valid_dataloader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=False, collate_fn=gpt2_classification_collator)
  x = predict(valid_dataloader, device)
  return(x)