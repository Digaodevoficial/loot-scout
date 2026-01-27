import streamlit as st
import requests
import random
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator

# 1. Configuração da página
st.set_page_config(page_title="LootScout | Radar Gamer Pro", page_icon="🏹", layout="wide")

# 2. CSS Master (Texto fora das caixas do jogo)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Imagens padronizadas */
    [data-testid="stImage"] img {
        height: 160px !important;
        object-fit: cover !important;
        border-radius: 8px;
        width: 100%;
    }

    /* Sistema de Badges */
    .badge-container {
        height: 35px; /* Altura fixa para evitar pulos */
        margin-top: 10px;
        display: flex; gap: 5px; flex-wrap: wrap;
        overflow: hidden;
    }
    .badge {
        padding: 2px 8px; border-radius: 4px; font-size: 0.62rem;
        font-weight: bold; text-transform: uppercase; border: 1px solid;
        white-space: nowrap;
    }
    .badge-urgente { background: #ffebee; color: #d32f2f; border-color: #d32f2f; }
    .badge-hype { background: #f3e5f5; color: #7b1fa2; border-color: #7b1fa2; }
    .badge-expirando { background: #fff3e0; color: #ef6c00; border-color: #ef6c00; animation: pulse 2s infinite; }

    @keyframes pulse {
        0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; }
    }

    /* Títulos e Descrições (Ajuste para não embolar) */
    .jogo-titulo {
        height: 50px; margin-top: 10px; font-size: 0.95rem; font-weight: 700;
        color: #1a1a1a; display: -webkit-box; -webkit-line-clamp: 2;
        -webkit-box-orient: vertical; overflow: hidden;
        line-height: 1.2;
    }

    .jogo-desc {
        height: 90px; /* Aumentado levemente */
        font-size: 0.8rem; color: #666;
        display: -webkit-box; -webkit-line-clamp: 5; /* Permite 5 linhas antes de cortar */
        -webkit-box-orient: vertical;
        overflow: hidden; 
        margin-bottom: 8px; 
        line-height: 1.3; /* Melhorado o espaçamento entre linhas */
    }

    .container-preco {
        background-color: #f0fdf4; border-radius: 6px; padding: 8px;
        margin-bottom: 10px; border: 1px dashed #22c55e; text-align: center;
        min-height: 55px;
    }
    
    .preco-gratis { color: #16a34a; font-weight: 800; font-size: 1rem; display: block; }

    /* Estilo do Rodapé Limpo */
    .footer {
        width: 100%; background-color: #ffffff; color: #444; text-align: center;
        padding: 30px; border-top: 1px solid #eee; margin-top: 50px;
    }
    
    .hit-perdido { filter: grayscale(100%); opacity: 0.6; transition: 0.3s; }
    .hit-perdido:hover { opacity: 1; filter: grayscale(0%); }
    </style>
    """, unsafe_allow_html=True)

# 3. Funções de Suporte Otimizadas
@st.cache_data(ttl=604800) # Cache de 7 dias para traduções (Reduz drasticamente a lentidão)
def traduzir_texto_cached(texto):
    try:
        return GoogleTranslator(source='en', target='pt').translate(texto)
    except:
        return texto

def traduzir_plataforma(plat):
    traducoes = {"PC": "PC", "Steam": "Steam", "Epic Games Store": "Epic Games", "PlayStation 5": "PS5", "Xbox Series X|S": "Xbox"}
    base = plat.split(',')[0].strip()
    return traducoes.get(base, base)

def converter_preco(valor_str):
    try:
        clean = ''.join(c for c in valor_str if c.isdigit() or c == '.')
        return float(clean) if clean else 0.0
    except: return 0.0

def verificar_expiracao(data_str):
    if not data_str or data_str == "N/A": return False
    try:
        data_fim = datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
        return data_fim < datetime.now() + timedelta(hours=24)
    except: return False

@st.cache_data(ttl=3600) # Cache de 1 hora para a API
def buscar_dados():
    try:
        r = requests.get("https://www.gamerpower.com/api/giveaways?sort-by=date", timeout=10)
        return r.json()
    except: return []

# 4. Interface Principal
def main():
    st.title("🏹 LootScout")
    st.caption("Seu radar avançado de recompensas e jogos gratuitos.")
    
    dados = buscar_dados()
    if not dados:
        st.error("Erro ao carregar dados.")
        return

    v_total = sum(converter_preco(g['worth']) for g in dados)
    st.info(f"💰 **Economia Disponível:** Você economiza cerca de **${v_total:,.2f}** resgatando tudo hoje!")

    with st.expander("👀 VEJA O QUE VOCÊ JÁ PERDEU (HITS HISTÓRICOS)", expanded=False):
        h_cols = st.columns(4)
        hits = [
            {"t": "Hogwarts Legacy", "img": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/990080/header.jpg", "v": "$59.99"},
            {"t": "GTA V", "img": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/271590/header.jpg", "v": "$29.99"},
            {"t": "Death Stranding", "img": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1850570/header.jpg", "v": "$39.99"},
            {"t": "Fallout 4", "img": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/377160/header.jpg", "v": "$19.99"}
        ]
        for i, hit in enumerate(hits):
            with h_cols[i]:
                st.markdown(f'<div class="hit-perdido"><img src="{hit["img"]}" style="width:100%; border-radius:8px;">', unsafe_allow_html=True)
                st.markdown(f'**{hit["t"]}**<br><span style="color:red; font-size:0.7rem;">❌ EXPIRADO</span><br><small>Era: {hit["v"]}</small></div>', unsafe_allow_html=True)

    st.divider()

    with st.sidebar:
        st.header("⚙️ Painel de Controle")
        if st.button("🎲 Jogo Aleatório", use_container_width=True):
            sorteado = random.choice(dados)
            st.toast(f"Sorteado: {sorteado['title']}")
            st.link_button("Ir para o Brinde", sorteado['open_giveaway_url'], use_container_width=True)
        
        st.divider()
        busca = st.text_input("🔍 Buscar jogo:", placeholder="Nome do jogo...")
        f_cat = st.multiselect("🏷️ Tipo de Brinde:", sorted(list(set([g['type'] for g in dados]))))
        min_v = st.slider("💵 Valor original min. ($):", 0, 100, 0)
        f_plat = st.multiselect("🖥️ Plataformas:", sorted(list(set([traduzir_plataforma(g['platforms']) for g in dados]))))
        
        st.divider()
        # Melhoria de Performance: Tradução desligada por padrão para carregar rápido
        traduzir_on = st.toggle("🌐 Traduzir (Beta)", value=False, help="Ative para traduzir as descrições. Isso pode levar alguns segundos no primeiro uso.")

    # Filtros
    jogos = [g for g in dados if busca.lower() in g['title'].lower() and converter_preco(g['worth']) >= min_v]
    if f_plat: jogos = [g for g in jogos if traduzir_plataforma(g['platforms']) in f_plat]
    if f_cat: jogos = [g for g in jogos if g['type'] in f_cat]

    st.subheader(f"🔥 Brindes Ativos Agora ({len(jogos)})")
    
    # GRID PRINCIPAL
    cols_count = 5
    for i in range(0, len(jogos), cols_count):
        linha = jogos[i:i + cols_count]
        cols = st.columns(cols_count)
        for j, jogo in enumerate(linha):
            with cols[j]:
                st.image(jogo['image'])
                
                # Badges
                b_html = ""
                if int(jogo.get('users', 0)) > 5000: b_html += '<span class="badge badge-hype">🔥 Popular</span>'
                if jogo.get('end_date') == "N/A": b_html += '<span class="badge badge-urgente">⚠️ Estoque</span>'
                if verificar_expiracao(jogo.get('end_date')): b_html += '<span class="badge badge-expirando">⏳ ACABA LOGO</span>'
                
                # Tradução Otimizada
                desc = jogo["description"]
                if traduzir_on:
                    desc = traduzir_texto_cached(desc)
                
                st.markdown(f'<div class="badge-container">{b_html}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="jogo-titulo">{jogo["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="jogo-desc">{desc}</div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="container-preco">
                        <small style="text-decoration: line-through; color: #94a3b8;">De {jogo['worth']}</small>
                        <span class="preco-gratis">GRÁTIS</span>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<div style="font-size:0.75rem; color:#777;">📍 {traduzir_plataforma(jogo["platforms"])}</div>', unsafe_allow_html=True)
                st.link_button("🎁 Resgatar Agora", jogo['open_giveaway_url'], use_container_width=True, type="primary")

    # RODAPÉ LIMPO
    st.markdown("""
        <div class="footer">
            <p>🏹 <b>LootScout</b> - Criado para verdadeiros batedores de recompensas.</p>
            <p style="font-size: 0.7rem; color: #999; margin-top: 10px;">
                © 2026 LootScout. Dados providos por GamerPower API.
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()