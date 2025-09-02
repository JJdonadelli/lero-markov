import re
import json
from collections import defaultdict

def export_markov_model(n=5):
    """
    Gera um modelo de Markov de ordem (n-1) a partir de dois arquivos.
    """

    # Tenta ler os dois arquivos, retorna silenciosamente se não achar
    try:
        text1 = open("data/maravilha_limpo.txt", encoding="utf-8").read().lower()
        text2 = open("data/espelho_limpo.txt", encoding="utf-8").read().lower()
    except FileNotFoundError:
        pass

    # Extrai  palavras 
    # words = re.findall(r"\b\w+\b", text1 + " " + text2)
    words = (text1 + " " + text2).split()

    # Modelo de Markov: chave = (n-1) palavras, valor = lista de próximas palavras
    markov = defaultdict(list)
    for i in range(len(words) - n + 1):
        prefix = tuple(words[i:i+n-1])  # sequência de (n-1) palavras
        next_word = words[i+n-1]       # palavra seguinte
        markov[prefix].append(next_word)

    # Converte as chaves (tuplas) para strings unidas por "|"
    markov_dict = {"|".join(key): val for key, val in markov.items()}

    # Exporta modelo em JSON
    with open("js/markov_model.json", "w", encoding="utf-8") as f:
        json.dump(markov_dict, f, ensure_ascii=False, indent=2)

    # Gera código JS para usar o modelo no browser
    js_code = (
        f"const ORDER={n-1};\n"  # Ordem do modelo no JS
        "const MARKOV_MODEL=" +
        json.dumps(markov_dict, ensure_ascii=False, indent=2) + ";\n"
        "function generateMarkovText(startWords,length=50){\n"
        "  let s=startWords.toLowerCase().trim().split(' ');\n"
        "  if(s.length<ORDER) throw `Informe pelo menos ${ORDER} palavras iniciais.`;\n"
        "  let r=s.slice(0,ORDER);\n"
        "  for(let i=ORDER;i<length;i++){\n"
        "    let key=r.slice(i-ORDER,i).join('|'),nxt=MARKOV_MODEL[key];\n"
        "    if(!nxt?.length) break;\n"
        "    let w=nxt[Math.floor(Math.random()*nxt.length)];\n"
        "    r.push(w);\n"
        "  }\nreturn r.join(' ')}\n"
        "function getAvailableStartKeys(){return Object.keys(MARKOV_MODEL)}\n"
    )
    with open("js/markov_model.js", "w", encoding="utf-8") as f:
        f.write(js_code)

    # Estatísticas simples
    start_counts = defaultdict(int)
    for key, ws in markov.items():
        start_counts[key[0]] += len(ws)

    stats = {
        "order": n-1,
        "total_words": len(words),
        "unique_sequences": len(markov),
        "unique_start_words": len(start_counts),
        "most_common_starts": sorted(start_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    }
    with open("js/model_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    export_markov_model(n=5)  # padrão: pentagrama
