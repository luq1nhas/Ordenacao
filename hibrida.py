"""
Ordenação híbrida: rápida (pivô aleatório, 3 partes) + inserção para pedaços pequenos.
Mede o tempo com 20 mil elementos aleatórios variando o corte e compara com a rápida pura.
"""
import random
import statistics
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.setrecursionlimit(10000)

N = 20_000
CORTES = [1, 5, 10, 16, 20, 32, 50, 100, 200]
REPETICOES = 7


def insercao(v):
    """Inserção: pega o próximo e encaixa no lugar (ordena no local)."""
    for i in range(1, len(v)):
        x = v[i]
        j = i - 1
        while j >= 0 and v[j] > x:
            v[j + 1] = v[j]
            j -= 1
        v[j + 1] = x
    return v


def rapida(v):
    """Ordenação rápida pura: pivô aleatório, separa em menores, iguais e maiores."""
    if len(v) <= 1:
        return v
    pivo = random.choice(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return rapida(menores) + iguais + rapida(maiores)


def hibrida(v, corte):
    """Rápida que passa para a inserção quando o pedaço tem menos que `corte` elementos."""
    if len(v) < corte:
        return insercao(v)
    if len(v) <= 1:
        return v
    pivo = random.choice(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return hibrida(menores, corte) + iguais + hibrida(maiores, corte)


def medir(funcao, dados, *args):
    """Mediana do tempo (ms) de REPETICOES execuções, sempre sobre uma cópia dos mesmos dados."""
    tempos = []
    for _ in range(REPETICOES):
        copia = list(dados)
        t0 = time.perf_counter()
        resultado = funcao(copia, *args)
        tempos.append((time.perf_counter() - t0) * 1000)
        assert resultado == sorted(dados), "saída não está ordenada"
    return statistics.median(tempos)


# ---- contagem de comparações, só para confirmar que corte = 1 é a rápida pura ----
comparacoes = 0


def rapida_contando(v):
    global comparacoes
    if len(v) <= 1:
        return v
    pivo = random.choice(v)
    comparacoes += 3 * len(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return rapida_contando(menores) + iguais + rapida_contando(maiores)


def hibrida_contando(v, corte):
    global comparacoes
    if len(v) < corte:
        for i in range(1, len(v)):          # mesma inserção, contando comparações
            x = v[i]
            j = i - 1
            while j >= 0:
                comparacoes += 1
                if v[j] <= x:
                    break
                v[j + 1] = v[j]
                j -= 1
            v[j + 1] = x
        return v
    if len(v) <= 1:
        return v
    pivo = random.choice(v)
    comparacoes += 3 * len(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return hibrida_contando(menores, corte) + iguais + hibrida_contando(maiores, corte)


def main():
    random.seed(2026)
    dados = [random.randint(0, 1_000_000) for _ in range(N)]

    # aquecimento
    rapida(list(dados))

    t_pura = medir(rapida, dados)
    print(f"rápida pura: {t_pura:.2f} ms")

    tempos = {}
    for c in CORTES:
        tempos[c] = medir(hibrida, dados, c)
        ganho = (t_pura - tempos[c]) / t_pura * 100
        print(f"corte {c:>3}: {tempos[c]:7.2f} ms  ({ganho:+.1f}% vs pura)")

    melhor = min(tempos, key=tempos.get)
    print(f"\nmelhor corte: {melhor} ({tempos[melhor]:.2f} ms), "
          f"ganho de {(t_pura - tempos[melhor]) / t_pura * 100:.1f}% sobre a pura")

    # confirmação de corte = 1: mesma semente => mesmos pivôs => mesmas comparações
    global comparacoes
    random.seed(7); comparacoes = 0; rapida_contando(list(dados)); c_pura = comparacoes
    random.seed(7); comparacoes = 0; hibrida_contando(list(dados), 1); c_um = comparacoes
    print(f"\ncomparações (mesma semente): pura = {c_pura:,}  corte 1 = {c_um:,}  "
          f"iguais: {c_pura == c_um}")
    for c in CORTES:
        random.seed(7); comparacoes = 0; hibrida_contando(list(dados), c)
        print(f"  comparações corte {c:>3}: {comparacoes:,}")

    # gráfico
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(CORTES, [tempos[c] for c in CORTES], marker="o", color="#2563eb", label="híbrida (rápida + inserção)")
    ax.axhline(t_pura, color="#dc2626", linestyle="--", label=f"rápida pura ({t_pura:.1f} ms)")
    ax.scatter([melhor], [tempos[melhor]], s=120, facecolors="none", edgecolors="#16a34a", linewidths=2,
               label=f"melhor corte = {melhor}", zorder=3)
    ax.set_xscale("log")
    ax.set_xticks(CORTES)
    ax.set_xticklabels([str(c) for c in CORTES])
    ax.set_xlabel("corte (tamanho abaixo do qual usa inserção) — escala log")
    ax.set_ylabel("tempo (ms, mediana de 7 execuções)")
    ax.set_title(f"Tempo em função do corte — n = {N:,} aleatórios".replace(",", "."))
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig("grafico_corte.png", dpi=120)
    print("\ngráfico salvo em grafico_corte.png")


if __name__ == "__main__":
    main()
