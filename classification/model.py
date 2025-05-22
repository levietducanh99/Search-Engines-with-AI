import torch
import torch.nn as nn


class Attention(nn.Module):
    """Attention layer for sequence models"""

    def __init__(self, feature_dim, step_dim, bias=True, **kwargs):
        super(Attention, self).__init__(**kwargs)

        self.supports_masking = True
        self.bias = bias
        self.feature_dim = feature_dim
        self.step_dim = step_dim
        self.features_dim = 0

        weight = torch.zeros(feature_dim, 1)
        nn.init.kaiming_uniform_(weight)
        self.weight = nn.Parameter(weight)

        if bias:
            self.b = nn.Parameter(torch.zeros(step_dim))

    def forward(self, x, mask=None):
        feature_dim = self.feature_dim
        step_dim = self.step_dim

        eij = torch.mm(
            x.contiguous().view(-1, feature_dim),
            self.weight
        ).view(-1, step_dim)

        if self.bias:
            eij = eij + self.b

        eij = torch.tanh(eij)
        a = torch.exp(eij)

        if mask is not None:
            a = a * mask

        a = a / (torch.sum(a, 1, keepdim=True) + 1e-10)

        weighted_input = x * torch.unsqueeze(a, -1)
        return torch.sum(weighted_input, 1)


class BERTClassifier(nn.Module):
    """Neural network for news title classification using BERT embeddings"""

    def __init__(self, bert_model, output_size, hidden_dim, seq_length, drop_prob=0.1):
        """Initialize the model by setting up the layers"""
        super(BERTClassifier, self).__init__()

        self.output_size = output_size
        self.hidden_dim = hidden_dim
        self.seq_length = seq_length
        
        # BERT model for embeddings
        self.bert = bert_model
        self.embedding_dim = self.bert.config.hidden_size  # 768 for bert-base

        # Dropout
        self.dropout = nn.Dropout(drop_prob)

        # LSTM and GRU layers
        self.lstm1 = nn.LSTM(self.embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.gru1 = nn.GRU(hidden_dim * 2, hidden_dim, bidirectional=True, batch_first=True)

        # Attention layer
        self.attention = Attention(hidden_dim * 2, seq_length)

        # Second LSTM and GRU layers
        self.lstm2 = nn.LSTM(hidden_dim * 2, hidden_dim, batch_first=True, bidirectional=True)
        self.gru2 = nn.GRU(hidden_dim * 2, hidden_dim, bidirectional=True, batch_first=True)

        # Linear layers
        self.fc = nn.Linear(hidden_dim * 2, 64)
        self.out = nn.Linear(64, self.output_size)

        self.relu = nn.ReLU()

    def forward(self, input_ids, attention_mask=None):
        """Perform a forward pass of the model"""
        batch_size = input_ids.size(0)
        
        # Get BERT embeddings
        with torch.no_grad():
            bert_outputs = self.bert(input_ids, attention_mask=attention_mask)
            # Use the last hidden states
            embeds = bert_outputs.last_hidden_state
            
        # Apply dropout
        embeds = self.dropout(embeds)

        # LSTM, GRU, and attention
        lstm_out, _ = self.lstm1(embeds)
        gru_out, _ = self.gru1(lstm_out)
        attention_out = self.attention(gru_out)
        attention_out = attention_out.view(batch_size, 1, self.hidden_dim * 2)
        lstm_out, _ = self.lstm2(attention_out)
        gru_out, _ = self.gru2(lstm_out)

        # Linear outputs
        out = gru_out.contiguous().view(-1, gru_out.shape[2])
        fc_out = self.relu(self.fc(out))
        final_out = self.out(fc_out)

        return final_out


# Keep the old RNN class for backward compatibility
class RNN(nn.Module):
    """Neural network for news title classification"""

    def __init__(self, weights_matrix, output_size, hidden_dim, seq_length, drop_prob=0.1):
        """Initialize the model by setting up the layers"""
        super(RNN, self).__init__()

        self.output_size = output_size
        self.hidden_dim = hidden_dim
        self.seq_length = seq_length

        # Embedding layer
        self.embedding, self.num_embeddings, self.embedding_dim = weights_matrix

        # Embedding dropout
        self.dropout = nn.Dropout2d(drop_prob)

        # First LSTM and GRU layers
        self.lstm1 = nn.LSTM(self.embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.gru1 = nn.GRU(hidden_dim * 2, hidden_dim, bidirectional=True, batch_first=True)

        # Attention layer
        self.attention = Attention(hidden_dim * 2, seq_length)

        # Second LSTM and GRU layers
        self.lstm2 = nn.LSTM(hidden_dim * 2, hidden_dim, batch_first=True, bidirectional=True)
        self.gru2 = nn.GRU(hidden_dim * 2, hidden_dim, bidirectional=True, batch_first=True)

        # Linear layers
        self.fc = nn.Linear(hidden_dim * 2, 64)
        self.out = nn.Linear(64, self.output_size)

        self.relu = nn.ReLU()

    def forward(self, x):
        """Perform a forward pass of the model"""
        batch_size = x.size(0)

        # Embedding
        x = x.long()
        embeds = self.embedding(x)
        embeds = torch.squeeze(torch.unsqueeze(embeds, 0))

        # LSTM, GRU, and attention
        lstm_out, _ = self.lstm1(embeds)
        gru_out, _ = self.gru1(lstm_out)
        attention_out = self.attention(gru_out)
        attention_out = attention_out.view(batch_size, 1, self.hidden_dim * 2)
        lstm_out, _ = self.lstm2(attention_out)
        gru_out, _ = self.gru2(lstm_out)

        # Linear outputs
        out = gru_out.contiguous().view(-1, gru_out.shape[2])
        fc_out = self.relu(self.fc(out))
        final_out = self.out(fc_out)

        return final_out
