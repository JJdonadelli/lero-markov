import streamlit as st
import random
import sys
from collections import defaultdict, Counter
import os

# Configuração da página
st.set_page_config(
    page_title="Gerador de Texto com N-Gramas",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Gerador de Texto com Modelos N-Gramas")
st.markdown("---")

# Funções principais (adaptadas do código original)
@st.cache_data
def load_texts():
    """Carrega os textos dos arquivos"""
    try:
        text1 = open("data/maravilha_limpo.txt", encoding="utf-8").read().lower()
        text2 = open("data/espelho_limpo.txt", encoding="utf-8").read().lower()
        return (text1 + " " + text2).split()
    except FileNotFoundError:
        return None

def build_ngram_model(words, n=3):
    """Constrói modelo de n-gramas"""
    if n < 2:
        raise ValueError("n deve ser >= 2")
    model = defaultdict(list)
    for i in range(len(words) - n + 1):
        context = tuple(words[i:i + n - 1])  # n-1 palavras
        next_word = words[i + n - 1]         # palavra seguinte
        model[context].append(next_word)
    return model

def generate_text(model, start_words, length=50):
    """Gera texto usando o modelo de n-gramas"""
    context_size = len(next(iter(model)))
    if len(start_words) != context_size:
        raise ValueError(f"O modelo espera {context_size} palavras no contexto.")
    
    output = list(start_words)

    for _ in range(length - context_size):
        current_context = tuple(output[-context_size:])
        if current_context not in model:
            break

        next_words = model[current_context]
        counts = Counter(next_words)
        palavras = list(counts.keys())
        pesos = list(counts.values())

        next_word = random.choices(palavras, weights=pesos, k=1)[0]
        output.append(next_word)

    return " ".join(output)

def get_random_start_words(words, context_size):
    """Escolhe uma sequência aleatória de palavras iniciais"""
    start_index = random.randint(0, len(words) - context_size)
    return tuple(words[start_index:start_index + context_size])

# Interface principal
col1, col2 = st.columns([1, 2])

with col1:
    st.header("⚙️ Configurações")
    
    # Carregar textos
    words = load_texts()
    
    if words is None:
        st.error("❌ Arquivos de texto não encontrados!")
        st.info("Certifique-se de que os arquivos estão em:")
        st.code("data/maravilha_limpo.txt\ndata/espelho_limpo.txt")
        
        # Opção para usar texto de exemplo
        if st.checkbox("Usar texto de exemplo"):
            sample_text = """era uma vez uma princesa muito bonita que vivia em um castelo encantado 
            no reino distante havia dragões e cavaleiros corajosos que protegiam a terra sagrada 
            os habitantes da vila eram felizes e trabalhavam nos campos verdes sob o sol dourado"""
            words = sample_text.lower().split()
            st.success("✅ Usando texto de exemplo!")
    else:
        st.success(f"✅ Textos carregados! ({len(words)} palavras)")
    
    if words:
        # Parâmetros
        n = st.slider("Ordem do N-Grama (n)", min_value=2, max_value=6, value=4, 
                     help="Número de palavras consideradas no contexto + 1")
        
        length = st.slider("Comprimento do texto", min_value=10, max_value=200, value=53,
                          help="Número de palavras a serem geradas")
        
        # Opções para palavras iniciais
        st.subheader("Palavras Iniciais")
        init_option = st.radio(
            "Como escolher:",
            ["Aleatório", "Manual"],
            help="Escolha como definir as palavras que iniciarão o texto"
        )
        
        context_size = n - 1
        
        if init_option == "Manual":
            manual_words = st.text_input(
                f"Digite {context_size} palavra(s) inicial(is):",
                placeholder=f"Exemplo: era uma vez" if context_size == 3 else "palavra1 palavra2...",
                help=f"Insira exatamente {context_size} palavra(s) separada(s) por espaço"
            )
        
        # Botão para gerar
        if st.button("🎲 Gerar Texto", type="primary"):
            try:
                # Construir modelo
                with st.spinner("Construindo modelo..."):
                    model = build_ngram_model(words, n=n)
                
                # Definir palavras iniciais
                if init_option == "Aleatório":
                    start_words = get_random_start_words(words, context_size)
                else:
                    if manual_words:
                        manual_list = manual_words.lower().split()
                        if len(manual_list) != context_size:
                            st.error(f"❌ Insira exatamente {context_size} palavra(s)!")
                            st.stop()
                        start_words = tuple(manual_list)
                    else:
                        st.error("❌ Digite as palavras iniciais!")
                        st.stop()
                
                # Gerar texto
                with st.spinner("Gerando texto..."):
                    generated = generate_text(model, start_words, length)
                
                # Armazenar no session state
                st.session_state.generated_text = generated
                st.session_state.start_words = start_words
                st.session_state.model_params = {"n": n, "length": length}
                
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")

with col2:
    st.header("📖 Texto Gerado")
    
    # Mostrar resultado
    if hasattr(st.session_state, 'generated_text'):
        # Informações do modelo
        with st.expander("ℹ️ Informações da Geração"):
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("Ordem N-Grama", st.session_state.model_params["n"])
            with col_info2:
                st.metric("Comprimento", st.session_state.model_params["length"])
            with col_info3:
                st.metric("Contexto Inicial", f"{len(st.session_state.start_words)} palavras")
            
            st.write("**Palavras iniciais:**", " ".join(st.session_state.start_words))
        
        # Texto gerado
        st.subheader("Resultado:")
        
        # Destacar palavras iniciais
        text_parts = st.session_state.generated_text.split()
        initial_part = " ".join(text_parts[:len(st.session_state.start_words)])
        remaining_part = " ".join(text_parts[len(st.session_state.start_words):])
        
        st.markdown(f"**{initial_part}** {remaining_part}")
        
        # Opções de exportação
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            st.download_button(
                "💾 Baixar como TXT",
                st.session_state.generated_text,
                file_name="texto_gerado.txt",
                mime="text/plain"
            )
        with col_exp2:
            if st.button("📋 Copiar para Área de Transferência"):
                st.write("Texto copiado!")
                
    else:
        st.info("👈 Configure os parâmetros à esquerda e clique em 'Gerar Texto' para começar!")

# Sidebar com informações
with st.sidebar:
    st.header("📊 Estatísticas")
    
    if words:
        st.metric("Total de Palavras", f"{len(words):,}")
        st.metric("Palavras Únicas", f"{len(set(words)):,}")
        
        # Palavras mais comuns
        with st.expander("🔤 Palavras Mais Comuns"):
            word_counts = Counter(words)
            top_words = word_counts.most_common(10)
            for word, count in top_words:
                st.write(f"**{word}**: {count}")
    
    st.markdown("---")
    st.header("ℹ️ Como Funciona")
    st.markdown("""
    **N-Gramas** são sequências de N palavras consecutivas. Este gerador:
    
    1. **Analisa** os textos de entrada
    2. **Constrói** um modelo estatístico baseado em sequências
    3. **Gera** novo texto seguindo os padrões encontrados
    
    **Parâmetros:**
    - **N=2**: Bigramas (contexto de 1 palavra)
    - **N=3**: Trigramas (contexto de 2 palavras)  
    - **N=4**: 4-gramas (contexto de 3 palavras)
    
    Valores maiores de N produzem texto mais coerente mas menos criativo.
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🤖 Gerador de Texto com Cadeias de Markov | Baseado em N-Gramas"
    "</div>", 
    unsafe_allow_html=True
)
