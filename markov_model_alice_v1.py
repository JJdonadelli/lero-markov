import streamlit as st
import re
import random
from collections import defaultdict
import os

# Configuração da página
st.set_page_config(
    page_title="Gerador de Texto Markoviano",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para deixar mais bonito
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .stAlert > div {
        padding: 1rem;
        border-radius: 10px;
    }
    
    .example-words {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .generated-text {
        background: #f8f9fa !important;
        color: #2c3e50 !important;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        font-family: Georgia, serif;
        line-height: 1.8;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    /* Garantir que o texto seja sempre visível */
    .generated-text * {
        color: #2c3e50 !important;
    }
    
    /* Melhorar contraste em modo escuro */
    [data-theme="dark"] .generated-text {
        background: #1e1e1e !important;
        color: #e0e0e0 !important;
        border-left-color: #667eea;
    }
    
    [data-theme="dark"] .generated-text * {
        color: #e0e0e0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar e processar o texto
@st.cache_data
def load_and_process_text(file_path="data/acile.txt"):
    """Carrega o arquivo de texto e constrói o modelo Markov"""

    
    try:
        with open(file_path, encoding="utf-8") as f:
            text = f.read().lower()
        
        # Quebrar em palavras
        words = re.findall(r"\b\w+\b", text)
        
        # Construir modelo de trigramas
        markov_model = defaultdict(list)
        for w1, w2, w3 in zip(words, words[1:], words[2:]):
            markov_model[(w1, w2)].append(w3)
        
        return markov_model, len(words)
    
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return None, 0

# Função para gerar texto (adaptada do seu código original)
def generate_text(model, start_words, length=46):
    """Gera texto usando o modelo Markov"""
    try:
        # Se o usuário passar apenas uma palavra, escolher uma segunda compatível
        if isinstance(start_words, str):
            candidates = [pair for pair in model.keys() if pair[0] == start_words]
            if not candidates:
                return None, f"❌ Não encontrei pares começando com '{start_words}' no texto."
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
        
        return " ".join(output), None
    
    except Exception as e:
        return None, f"❌ Erro ao gerar texto: {e}"

# Interface principal
def main():
    # Cabeçalho
    st.markdown('<h1 class="main-header"> Gerador de Texto Markoviano</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Demonstração de Cadeia de Markov para Geração de Texto Artificial<br>Baseado em "Alice no País das Maravilhas"</p>', unsafe_allow_html=True)
    
    # Carregar o modelo
    with st.spinner("🔄 Carregando modelo Markov..."):
        markov_model, total_words = load_and_process_text()
    
    if markov_model is None:
        st.error("❌ Não foi possível carregar o modelo.")
        return
    
    # Informações sobre o modelo na sidebar
    st.sidebar.markdown("## 📊 Informações do Modelo")
    st.sidebar.info(f"""
    **Total de palavras:** {total_words:,}
    
    **Trigramas únicos:** {len(markov_model):,}
    
    **Ordem do modelo:** 2 (trigrama)
    
    **Arquivo base:** acile.txt
    """)
    
    # Palavras disponíveis no modelo
    available_words = list(set([pair[0] for pair in markov_model.keys()]))
    popular_words = sorted(available_words)[:20]  # Primeiras 20 em ordem alfabética
    
    st.sidebar.markdown("## 💡 Palavras Disponíveis")
    st.sidebar.info(f"O modelo contém **{len(available_words)}** palavras iniciais diferentes.")
    
    # Inicializar session_state
    if 'selected_word' not in st.session_state:
        st.session_state.selected_word = ""
    
    # Exemplos de palavras - ANTES do input para funcionar
    st.markdown("### 🔤 Experimente estas palavras:")
    example_words = ['alice', 'coelho', 'rainha', 'gato', 'chapeleiro']
    
    cols = st.columns(len(example_words))
    for i, word in enumerate(example_words):
        if cols[i].button(f"**{word}**", key=f"btn_{word}"):
            st.session_state.selected_word = word
            st.rerun()
    
    # Área principal de entrada
    col1, col2 = st.columns([3, 1])
    
    with col1:
        start_word = st.text_input(
            "🎯 Palavra inicial:",
            value=st.session_state.selected_word,
            placeholder="Digite uma palavra (ex: alice, coelho, rainha...)",
            help="Digite uma palavra que aparece no texto de Alice",
            key="word_input"
        )
        
        # Sincronizar com session_state
        if start_word != st.session_state.selected_word:
            st.session_state.selected_word = start_word
    
    with col2:
        length = st.number_input(
            "📏 Comprimento:",
            min_value=10,
            max_value=200,
            value=46,
            help="Número de palavras a gerar"
        )
    
    # Botão de geração
    if st.button("🎲 Gerar Texto", type="primary", use_container_width=True):
        if not start_word:
            st.warning("⚠️ Por favor, digite uma palavra inicial!")
        else:
            with st.spinner("🔄 Gerando texto..."):
                generated_text, error = generate_text(markov_model, start_word.lower().strip(), length)
                
                if error:
                    st.error(error)
                    
                    # Sugerir palavras similares
                    similar_words = [word for word in available_words if start_word.lower() in word][:10]
                    if similar_words:
                        st.info(f"💡 Palavras similares disponíveis: {', '.join(similar_words)}")
                else:
                    st.markdown("### 📝 Texto Gerado:")
                    # Usar st.text_area para garantir legibilidade
                    st.text_area(
                        label="",
                        value=generated_text,
                        height=200,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                    
                    # Opções adicionais
                    # col1, col2, col3 = st.columns(3)
                    # col1, col2 = st.columns(2)

                    # with st.columns(1):
                    if st.button("🔄 Gerar Novamente"):
                            st.rerun()
                    
                    # with col2:
                        # st.download_button(
                        #     "💾 Baixar Texto",
                        #     data=generated_text,
                        #     file_name=f"texto_markov_{start_word}.txt",
                        #     mime="text/plain"
                        # )
                    
                    # with col3: 
                        # if st.button("📋 Copiar"):
                            # st.info("Use Ctrl+C para copiar o texto acima!")

    # Explicação do algoritmo na parte inferior
    with st.expander("Como funciona o Algoritmo Markov"):
        st.markdown("""
        ### 🔍 **Cadeia de Markov de Ordem 2 (Trigramas)**
        
        1. **Processamento do texto:**
           - O texto é dividido em palavras
           - Cada sequência de 3 palavras consecutivas forma um "trigrama"
           - Exemplo: "Alice estava muito" → ("Alice", "estava") → "muito"
        
        2. **Construção do modelo:**
           - Para cada par de palavras, guardamos quais palavras podem vir a seguir
           - Exemplo: após ("Alice", "estava") podem vir ["muito", "pensando", "curiosa"...]
        
        3. **Geração do texto:**
           - Começamos com a palavra escolhida
           - Encontramos um par compatível 
           - Escolhemos aleatoriamente a próxima palavra baseada no modelo
           - Repetimos o processo até atingir o comprimento desejado
        
        ### **Vantagens:**
        - Preserva padrões linguísticos do texto original
        - Gera texto que "soa" como o autor original
        - Simples de implementar e entender
        
        ### **Limitações:**
        - Não entende significado, apenas padrões
        - Pode gerar frases sem sentido
        - Limitado ao vocabulário do texto original
        """)

if __name__ == "__main__":
    main()