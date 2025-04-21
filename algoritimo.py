import json

historico_execucao = []

# --- Função para salvar o histórico de execução ---
def salvar_frame(linha, coluna, estado, mensagem, posicoes):
    # Só salvar o frame se o estado não for "tentativa"
    if estado != "tentativa":
        historico_execucao.append({
            "linha": linha,
            "coluna": coluna,
            "estado": estado,  # "tentativa", "valido", "invalido", "solucao"
            "posicoes": posicoes[:],
            "mensagem": mensagem
        })

        with open("historico_execucao.json", "w") as f:
            json.dump(historico_execucao, f)

# --- Função de verificação de posição válida ---
def eh_valido(posicoes, linha, coluna):
    for i in range(linha):
        if posicoes[i] == coluna:
            salvar_frame(linha, coluna, "invalido", "coluna", posicoes)
            return False
        if abs(posicoes[i] - coluna) == abs(i - linha):
            salvar_frame(linha, coluna, "invalido", "diagonal", posicoes)
            return False
    salvar_frame(linha, coluna, "valido", "ok", posicoes)
    return True

def resolver_8_rainhas(linha=0, posicoes=None, solucoes=None, contador=[0]):
    if posicoes is None:
        posicoes = [0] * 8
    if solucoes is None:
        solucoes = []

    if linha == 8:
        contador[0] += 1
        salvar_frame(linha, -1, "solucao", f"#{contador[0]}", posicoes)
        solucoes.append(posicoes[:])
    else:
        for coluna in range(8):
            # Removido: salvar_frame para tentativas
            if eh_valido(posicoes, linha, coluna):
                posicoes[linha] = coluna
                resolver_8_rainhas(linha + 1, posicoes, solucoes, contador)
    return solucoes

# --- Funções para gerar simetrias (rotações e reflexos) ---
def rotacionar_90(sol):
    return [sol.index(i) for i in range(8)]

def refletir(sol):
    return [7 - col for col in sol]

def gerar_simetrias(solucao):
    simetrias = []
    atual = solucao[:]
    for _ in range(4):
        atual = rotacionar_90(atual)
        simetrias.append(tuple(atual))
        simetrias.append(tuple(refletir(atual)))
    return simetrias

# --- Função para filtrar apenas as 12 soluções únicas ---
def filtrar_solucoes_unicas(solucoes):
    vistas = set()
    unicas = []
    for sol in solucoes:
        formas = gerar_simetrias(sol)
        if not any(f in vistas for f in formas):
            unicas.append(sol)
            vistas.add(tuple(sol))
    return unicas

# --- Execução final ---
if __name__ == "__main__":
    todas = resolver_8_rainhas()
    unicas = filtrar_solucoes_unicas(todas)
    
    print(f"\n✅ Total de soluções encontradas: {len(todas)}")
    print(f"🌟 Total de soluções únicas (sem simetrias): {len(unicas)}\n")

    for i, sol in enumerate(unicas, 1):
        print(f"Solução única #{i}: {sol}")
