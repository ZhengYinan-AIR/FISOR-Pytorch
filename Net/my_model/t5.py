
import torch
import transformers
from transformers import T5Tokenizer, T5EncoderModel, T5Model

T5EncoderModel._keys_to_ignore_on_load_unexpected = ["decoder.*"]

class T5Encoder():
    def __init__(self, 
            model_path = 'google-t5/t5-base',
            device = "cuda",
            max_length = 256) -> None:
        self.device = device
        self.tokenizer = T5Tokenizer.from_pretrained(model_path)
        self.model = T5EncoderModel.from_pretrained(model_path)
        self.model.to(device)
        self.max_length = max_length


    @torch.no_grad()
    def embed_text(self, text, return_avg_pooling = True):
        encoded = self.tokenizer.batch_encode_plus(
            text,
            return_tensors = "pt",
            padding = 'longest',
            max_length = self.max_length,
            truncation = True
        )

        input_ids = encoded.input_ids.to(self.device)
        attn_mask = encoded.attention_mask.to(self.device)
        self.model.eval()

        with torch.no_grad():
            output = self.model(input_ids = input_ids, attention_mask = attn_mask)
            encoded_text = output.last_hidden_state.detach()

        attn_mask = attn_mask.bool()
        encoded_text.masked_fill_(~attn_mask[..., None], 0.)

        if return_avg_pooling:
            numer = encoded_text.sum(dim = -2)
            denom = attn_mask.sum(dim = -1)[..., None]
            numer.masked_fill_(denom == 0, 0.)
            mean_encodings = numer / denom.clamp(min = 1e-3)
            return mean_encodings

        return {
            'hidden_states': encoded_text,
            'avg_pooling': mean_encodings
        }


if __name__ == "__main__":
    model = T5Encoder(device="cuda")
    emb = model.embed_text(["test our models  and and and"])
    print(emb.shape)


