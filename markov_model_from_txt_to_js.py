import re
import json
from collections import defaultdict

def export_markov_model():
    try:
        text = open("acile.txt", encoding="utf-8").read().lower()
    except FileNotFoundError:
        return

    words = re.findall(r"\b\w+\b", text)
    markov = defaultdict(list)
    for w1, w2, w3 in zip(words, words[1:], words[2:]):
        markov[(w1, w2)].append(w3)

    markov_dict = {f"{w1}|{w2}": ws for (w1, w2), ws in markov.items()}

    with open("markov_model.json", "w", encoding="utf-8") as f:
        json.dump(markov_dict, f, ensure_ascii=False, indent=2)

    js_code = (
        "const MARKOV_MODEL=" +
        json.dumps(markov_dict, ensure_ascii=False, indent=2) + ";\n"
        "function generateMarkovText(startWord,length=50){\n"
        "  startWord=startWord.toLowerCase().trim();\n"
        "  const c=Object.keys(MARKOV_MODEL).map(k=>k.split('|')).filter(([w])=>w===startWord);\n"
        "  if(!c.length) throw `Palavra \"${startWord}\" não encontrada.`;\n"
        "  let [w1,w2]=c[Math.floor(Math.random()*c.length)],r=[w1,w2];\n"
        "  for(let i=2;i<length;i++){\n"
        "    let key=`${w1}|${w2}`,n=MARKOV_MODEL[key];\n"
        "    if(!n?.length) break;\n"
        "    let w=n[Math.floor(Math.random()*n.length)];\n"
        "    r.push(w);w1=w2;w2=w;\n"
        "  }\nreturn r.join(' ')}\n"
        "function getAvailableStartWords(){return[...new Set(Object.keys(MARKOV_MODEL).map(k=>k.split('|')[0]))].sort()}\n"
    )
    with open("markov_model.js", "w", encoding="utf-8") as f:
        f.write(js_code)

    start_counts = defaultdict(int)
    for (w1, _), ws in markov.items():
        start_counts[w1] += len(ws)

    stats = {
        "total_characters": len(text),
        "total_words": len(words),
        "unique_trigrams": len(markov),
        "unique_start_words": len(start_counts),
        "most_common_starts": sorted(start_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    }
    with open("model_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    export_markov_model()
