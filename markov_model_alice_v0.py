import re
import random
from collections import defaultdict

# Carregar o texto
with open("acile.txt", encoding="utf-8") as f:
    text = f.read().lower()

# Quebrar em palavras
words = re.findall(r"\b\w+\b", text)

# Construir modelo de trigramas (Markov ordem 2)
markov_model = defaultdict(list)
for w1, w2, w3 in zip(words, words[1:], words[2:]):
    markov_model[(w1, w2)].append(w3)

# Função para gerar texto artificial
def generate_text(model, start_words, length=50):
    # Se o usuário passar apenas uma palavra, escolher uma segunda compatível
    if isinstance(start_words, str):
        candidates = [pair for pair in model.keys() if pair[0] == start_words]
        if not candidates:
            raise ValueError(f"Não encontrei pares começando com '{start_words}' no texto.")
        w1, w2 = random.choice(candidates)
    else:
        w1, w2 = start_words

    output = [w1, w2]
    for _ in range(length - 2):
        if (w1, w2) not in model:
            break
        w3 = random.choice(model[(w1, w2)])
        output.append(w3)
        w1, w2 = w2, w3
    return " ".join(output)

# Exemplos:
print(">>> Texto começando com 'alice':")
print(generate_text(markov_model, "alice", 60))

print("\n>>> Texto começando com 'coelho branco':")
print(generate_text(markov_model, ("coelho", "branco"), 60))

print("\n>>> Texto começando com 'rainha':")
print(generate_text(markov_model, "rainha", 60))


print(markov_model)