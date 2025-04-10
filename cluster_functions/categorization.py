import numpy as np
from transformers import LongformerTokenizer, LongformerModel
import torch
import pandas as pd
import os
from VARIABLE import TRANSFORMER_DIRECTORY, TRANSFORMER_DNAME
from torch.utils.data import DataLoader


class TextDataset(torch.utils.data.Dataset):
    def __init__(self, texts):
        self.texts = texts

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.texts[idx]



def load_transformers():
    print("Adding model and transformers...")
    dirs = os.listdir("../")
    model_name = "allenai/longformer-base-4096"

    if TRANSFORMER_DNAME in dirs:
        tokenizer = LongformerTokenizer.from_pretrained(TRANSFORMER_DIRECTORY)
        model = LongformerModel.from_pretrained(TRANSFORMER_DIRECTORY)
    else:
        os.makedirs(TRANSFORMER_DIRECTORY)
        tokenizer = LongformerTokenizer.from_pretrained(model_name)
        model = LongformerModel.from_pretrained(model_name)
        tokenizer.save_pretrained(TRANSFORMER_DIRECTORY)
        model.save_pretrained(TRANSFORMER_DIRECTORY)

    return tokenizer, model


def categorize_issues(issues):
    print("Performing the embedding...")

    tokenizer, model = load_transformers()
    dataset = TextDataset(issues)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=False)

    embeddings_list = []
    for batch_texts in dataloader:
        inputs = tokenizer(
            batch_texts,
            padding="max_length",
            truncation=True,
            max_length=4096,
            return_tensors="pt"
        ).to("cuda" if torch.cuda.is_available() else "cpu")

        with torch.no_grad():
            outputs = model(**inputs)
        new_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()  
        embeddings_list.append(new_embedding)
    
    final_array = np.vstack(embeddings_list)  
    df = pd.DataFrame(final_array)
    df.columns = [f"dim_{i}" for i in range(df.shape[1])]
    df["texts"] = issues

    df.to_csv("../open_issue_embeddings.csv", index=False)



def main():
    df = pd.read_csv("../issues_folder/open_issues.csv")
    df.fillna("", inplace=True)
    issues = (df["title"] + '\n' + df["body"]).tolist()

    categorize_issues(issues)
    print("Completed the vectorization")


if __name__ == "__main__":
    print("Running...")
    main()