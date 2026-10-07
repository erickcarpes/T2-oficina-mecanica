#!/usr/bin/env python3
# Gera o desenho da rede de filas da oficina (situacao atual e melhorada) em PNG.
#
# Uso: python3 gerar_desenho.py
# Saida: apresentacao/rede_filas_atual.png e apresentacao/rede_filas_melhorada.png

import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(BASE, 'apresentacao')

AZUL = '#1F4E79'
AZUL_CLARO = '#DEEBF7'
VERDE = '#2E7D32'
VERDE_CLARO = '#E2F0D9'
VERMELHO = '#C00000'
CINZA = '#808080'
LARANJA = '#ED7D31'


def caixa(ax, x, y, w, h, titulo, linhas, cor=AZUL, fundo=AZUL_CLARO):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.012,rounding_size=0.02',
                                linewidth=2, edgecolor=cor, facecolor=fundo, zorder=3))
    ax.text(x + w / 2, y + h - 0.055, titulo, ha='center', va='top',
            fontsize=11, fontweight='bold', color=cor, zorder=4)
    ax.text(x + w / 2, y + h / 2 - 0.035, '\n'.join(linhas), ha='center', va='center',
            fontsize=8.5, color='#333333', zorder=4)


def seta(ax, p1, p2, texto='', cor=AZUL, estilo='-|>', rad=0.0, desloc=0.028,
         tracejado=False, tamanho=10, peso='bold'):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=estilo, mutation_scale=tamanho,
                                 linewidth=1.8, color=cor, zorder=2,
                                 connectionstyle='arc3,rad=%.2f' % rad,
                                 linestyle='--' if tracejado else '-'))
    if texto:
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2
        ax.text(mx + rad * 0.0, my + desloc, texto, ha='center', va='center',
                fontsize=8.5, color=cor, fontweight=peso, zorder=5,
                bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.85))


def desenha(caminho, titulo, params, melhorada=False):
    fig, ax = plt.subplots(figsize=(11, 6.2), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    ax.text(0.5, 0.955, titulo, ha='center', va='top',
            fontsize=13, fontweight='bold', color=AZUL)

    w, h = 0.235, 0.30
    y = 0.55
    xs = [0.10, 0.3825, 0.665]
    centros = [x + w / 2 for x in xs]

    r = params['RECEPCAO']
    o = params['OFICINA']
    q = params['QUALIDADE']

    caixa(ax, xs[0], y, w, h, 'RECEPCAO',
          ['G/G/1/%d' % r['capacity'],
           'chegadas 6..12',
           'atend. 4..8 (1 func.)'],
          cor=AZUL)
    caixa(ax, xs[1], y, w, h, 'OFICINA',
          ['G/G/%d/%d' % (o['servers'], o['capacity']),
           'atend. %d..%d' % (o['minService'], o['maxService']),
           '%d mecanicos' % o['servers']],
          cor=VERMELHO if melhorada else AZUL,
          fundo='#FBE5E5' if melhorada else AZUL_CLARO)
    caixa(ax, xs[2], y, w, h, 'QUALIDADE',
          ['G/G/1/%d' % q['capacity'],
           'atend. 4..8 (1 insp.)',
           'retrabalho %.0f%%' % (params['retrabalho'] * 100)],
          cor=VERDE if melhorada else AZUL,
          fundo=VERDE_CLARO if melhorada else AZUL_CLARO)

    # chegadas externas
    caixa(ax, -0.005, y + 0.075, 0.095, 0.15, 'CHEGADAS',
          ['do exterior', '1o em t=5,0'],
          cor=LARANJA, fundo='#FCE4D6')
    seta(ax, (0.09, y + 0.15), (xs[0], y + 0.15), '', cor=LARANJA)

    # fluxo para frente
    seta(ax, (xs[0] + w, y + 0.19), (xs[1], y + 0.19), '95%', cor=AZUL)
    seta(ax, (xs[1] + w, y + 0.19), (xs[2], y + 0.19), '90%', cor=AZUL)

    # realimentacao (retrabalho) - arcos por cima
    seta(ax, (xs[2] + w / 2, y + h), (xs[1] + w / 2, y + h),
         'retrabalho %.0f%%' % (params['retrabalho'] * 100), cor=VERMELHO, rad=0.35)
    seta(ax, (xs[1] + w / 2, y + h), (xs[0] + w / 2, y + h),
         'pecas 5%', cor=VERMELHO, rad=0.35)

    # saidas para o exterior
    caixa(ax, 0.40, 0.06, 0.20, 0.135, 'SAIDA',
          ['veiculo entregue'],
          cor='#548235', fundo='#E2EFDA')
    seta(ax, (xs[0] + w / 2, y), (0.46, 0.195), '5%', cor=CINZA, rad=-0.15)
    seta(ax, (xs[1] + w / 2, y), (0.50, 0.195), '5%', cor=CINZA)
    seta(ax, (xs[2] + w / 2, y), (0.54, 0.195),
         '%.0f%%' % ((1 - params['retrabalho']) * 100), cor=CINZA, rad=0.15)

    ax.text(0.5, 0.012, 'Setas tracejadas/vermelhas = realimentacao entre filas; '
            'percentuais = probabilidades de roteamento (Kendall: G/G/c/K).',
            ha='center', va='bottom', fontsize=7.5, style='italic', color='#595959')

    fig.tight_layout()
    fig.savefig(caminho, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('gerado:', caminho)


def main():
    atual = {
        'RECEPCAO': {'capacity': 8, 'servers': 1},
        'OFICINA': {'capacity': 12, 'servers': 3, 'minService': 20, 'maxService': 35},
        'QUALIDADE': {'capacity': 6, 'servers': 1},
        'retrabalho': 0.15,
    }
    melhorada = {
        'RECEPCAO': {'capacity': 10, 'servers': 1},
        'OFICINA': {'capacity': 14, 'servers': 4, 'minService': 18, 'maxService': 30},
        'QUALIDADE': {'capacity': 8, 'servers': 1},
        'retrabalho': 0.10,
    }
    desenha(os.path.join(SAIDA, 'rede_filas_atual.png'),
            'Oficina Mecanica - Modelo ATUAL', atual, melhorada=False)
    desenha(os.path.join(SAIDA, 'rede_filas_melhorada.png'),
            'Oficina Mecanica - Modelo MELHORADO (alteracoes destacadas)',
            melhorada, melhorada=True)


if __name__ == '__main__':
    main()
