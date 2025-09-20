#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pré-processador ULTRA-RÁPIDO para Alice
Gera apenas dados essenciais para velocidade máxima
"""

import json
import re
import os
from collections import defaultdict, Counter

def preprocessar_texto(texto):
    """Preprocessa mantendo acentos."""
    if not texto:
        return ""
    
    texto = re.sub(r'\n+', ' ', texto)
    texto = re.sub(r'[^\wáàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ\s\.\!\?\,\;\:\-\"]', '', texto)
    texto = texto.lower()
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()

def tokenizar(texto):
    return [token for token in texto.split() if token]

def criar_ngramas_otimizados(tokens, n, limite=1000):
    """Cria apenas os n-gramas mais frequentes para velocidade."""
    ngramas = defaultdict(list)
    
    for i in range(len(tokens) - n + 1):
        chave = ' '.join(tokens[i:i+n-1])
        proxima_palavra = tokens[i+n-1]
        ngramas[chave].append(proxima_palavra)
    
    # Filtra apenas os mais frequentes
    ngramas_filtrados = {}
    for chave, palavras in ngramas.items():
        if len(palavras) >= 2:  # Só inclui se aparece pelo menos 2 vezes
            ngramas_filtrados[chave] = palavras
    
    # Pega só os mais usados
    items_ordenados = sorted(ngramas_filtrados.items(), key=lambda x: len(x[1]), reverse=True)
    return dict(items_ordenados[:limite])

def encontrar_palavras_top(tokens):
    """Encontra apenas as palavras mais relevantes."""
    palavras_alice = [
        'alice', 'coelho', 'chapeleiro', 'gato', 'rainha', 'rei',
        'chá', 'mesa', 'jardim', 'espelho', 'sonho', 'tempo',
        'país', 'maravilhas', 'pequena', 'grande', 'porta', 'chave',
        'através', 'então', 'coração', 'não', 'também', 'estava',
        'havia', 'disse', 'viu', 'pensou'
    ]
    
    contador = Counter(tokens)
    
    # Palavras Alice disponíveis
    alice_disp = [p for p in palavras_alice if contador.get(p, 0) > 2]
    
    # Top palavras frequentes
    top_freq = [palavra for palavra, freq in contador.most_common(20) 
               if len(palavra) > 3 and re.match(r'^[a-záàâãéèêíìîóòôõúùûç]+$', palavra)][:15]
    
    return sorted(list(set(alice_disp + top_freq)))

def main():
    print("⚡ ULTRA-FAST Preprocessor Alice")
    print("=" * 40)
    
    # Encontra arquivos
    caminhos = [
        ('public_html/estocastico/markov_lero/data/', 'maravilha-limpo.txt', 'espelho-limpo.txt'),
        ('data/', 'maravilha-limpo.txt', 'espelho-limpo.txt'),
        ('./', 'maravilha-limpo.txt', 'espelho-limpo.txt')
    ]
    
    texto_completo = ""
    
    for pasta, arq1, arq2 in caminhos:
        try:
            with open(os.path.join(pasta, arq1), 'r', encoding='utf-8') as f:
                maravilha = f.read()
            with open(os.path.join(pasta, arq2), 'r', encoding='utf-8') as f:
                espelho = f.read()
            
            texto_completo = maravilha + " " + espelho
            print(f"✅ Arquivos: {pasta}")
            break
        except:
            continue
    
    if not texto_completo:
        print("❌ Arquivos não encontrados!")
        return
    
    print(f"📖 Texto: {len(texto_completo):,} chars")
    
    # Processa
    texto_limpo = preprocessar_texto(texto_completo)
    tokens = tokenizar(texto_limpo)
    print(f"🔤 Tokens: {len(tokens):,}")
    
    palavras_top = encontrar_palavras_top(tokens)
    print(f"⭐ Palavras: {len(palavras_top)}")
    
    # N-gramas LIMITADOS para velocidade
    print("🚀 N-gramas otimizados...")
    ngramas = {
        '2': criar_ngramas_otimizados(tokens, 2, 800),   # Menos dados
        '3': criar_ngramas_otimizados(tokens, 3, 600),   # para velocidade
        '4': criar_ngramas_otimizados(tokens, 4, 400),   # máxima
        '5': criar_ngramas_otimizados(tokens, 5, 200),
        '6': criar_ngramas_otimizados(tokens, 6, 100)
    }
    
    for n, dados in ngramas.items():
        print(f"  {n}-gramas: {len(dados)}")
    
    # Dados MÍNIMOS
    dados_rapidos = {
        'palavras': palavras_top,
        'stats': {
            'tokens': len(tokens),
            'unicos': len(set(tokens)),
            'alice_count': len([p for p in palavras_top if p in ['alice', 'coelho', 'gato']])
        },
        'ng': ngramas  # Nome curto para economia
    }
    
    # Salva compacto
    arquivo = 'alice_fast.json'
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados_rapidos, f, ensure_ascii=False, separators=(',', ':'))
    
    tamanho_kb = os.path.getsize(arquivo) / 1024
    print(f"💾 Salvo: {arquivo} ({tamanho_kb:.1f} KB)")
    
    print(f"🎯 Top palavras: {', '.join(palavras_top[:8])}")
    print("🚀 PRONTO! Será MUITO mais rápido agora!")

if __name__ == "__main__":
    main()
