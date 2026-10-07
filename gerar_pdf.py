#!/usr/bin/env python3
# Gera a versao em PDF (via HTML) da apresentacao do T2, alem dos graficos.
#
# Uso: python3 gerar_pdf.py
# Saida: apresentacao/T2_Oficina_Mecanica.html + graficos PNG
# Depois, renderize o HTML em PDF com o navegador (Playwright/Chrome).

import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import simulador as sim

BASE = os.path.dirname(os.path.abspath(__file__))
APRES = os.path.join(BASE, 'apresentacao')
ATUAL = os.path.join(BASE, 'modelos', 'oficina.yml')
MELHOR = os.path.join(BASE, 'modelos', 'oficina_melhorada.yml')

AZUL = '#1F4E79'
AZUL_CLARO = '#DEEBF7'
VERDE = '#2E7D32'
VERMELHO = '#C00000'
CINZA = '#595959'


def br(valor, casas=2):
    return ('%.*f' % (casas, valor)).replace('.', ',')


def coleta(caminho):
    esc, n = sim.simula(caminho)
    tg = esc.tempo_global()
    filas = {}
    for fila in esc.filas.values():
        idx = sim.indices(fila, tg)
        idx['perdas'] = fila.perdidos
        idx['estados'] = {k: v / tg for k, v in fila.estatistica.items()}
        idx['notacao'] = sim.notacao(fila)
        idx['servidores'] = fila.servidores
        idx['capacidade'] = fila.capacidade
        filas[fila.nome] = idx
    return {'tg': tg, 'filas': filas}


def grafico_barras(nome, titulo, categorias, series, unidade=''):
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200)
    largura = 0.38
    pos = range(len(categorias))
    for i, (rotulo, valores, cor) in enumerate(series):
        desloc = (i - (len(series) - 1) / 2) * largura
        barras = ax.bar([p + desloc for p in pos], valores, largura,
                        label=rotulo, color=cor)
        ax.bar_label(barras, fmt='%.1f', fontsize=9, padding=2)
    ax.set_xticks(list(pos))
    ax.set_xticklabels(categorias)
    ax.set_title(titulo, fontsize=12, fontweight='bold', color=AZUL)
    ax.set_ylabel(unidade)
    ax.grid(axis='y', alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9)
    fig.tight_layout()
    caminho = os.path.join(APRES, nome)
    fig.savefig(caminho, facecolor='white')
    plt.close(fig)
    print('gerado:', caminho)


def grafico_estados(nome, estados_a, estados_m):
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200)
    maximo = max(max(estados_a), max(estados_m))
    chaves = list(range(maximo + 1))
    va = [estados_a.get(k, 0) * 100 for k in chaves]
    vm = [estados_m.get(k, 0) * 100 for k in chaves]
    largura = 0.4
    barras = ax.bar([k - 0.2 for k in chaves], va, largura, label='Atual', color=VERMELHO)
    ax.bar([k + 0.2 for k in chaves], vm, largura, label='Melhorada', color=VERDE)
    ax.bar_label(barras, fmt='%.1f', fontsize=8, padding=2)
    ax.set_xticks(chaves)
    ax.set_xlabel('Estado da fila (numero de clientes)')
    ax.set_ylabel('Probabilidade (%)')
    ax.set_title('OFICINA: distribuicao de probabilidade dos estados',
                 fontsize=12, fontweight='bold', color=AZUL)
    ax.grid(axis='y', alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9)
    fig.tight_layout()
    caminho = os.path.join(APRES, nome)
    fig.savefig(caminho, facecolor='white')
    plt.close(fig)
    print('gerado:', caminho)


def slide(titulo, corpo, rodape_num, total=10):
    return ('<section class="slide"><div class="topbar"></div>'
            '<h1>{}</h1><div class="corpo">{}</div>'
            '<div class="rodape">T2 | Oficina Mecanica &middot; {}/{}</div></section>').format(
        titulo, corpo, rodape_num, total)


def main():
    atual = coleta(ATUAL)
    melhor = coleta(MELHOR)
    a = atual['filas']
    m = melhor['filas']

    grafico_barras('grafico_w.png', 'Tempo de resposta W por fila (min)',
                   ['RECEPCAO', 'OFICINA', 'QUALIDADE'],
                   [('Atual', [a['RECEPCAO']['w'], a['OFICINA']['w'], a['QUALIDADE']['w']], VERMELHO),
                    ('Melhorada', [m['RECEPCAO']['w'], m['OFICINA']['w'], m['QUALIDADE']['w']], VERDE)],
                   'min')
    grafico_barras('grafico_perdas.png', 'Perdas de clientes por fila',
                   ['RECEPCAO', 'OFICINA', 'QUALIDADE'],
                   [('Atual', [a['RECEPCAO']['perdas'], a['OFICINA']['perdas'], a['QUALIDADE']['perdas']], VERMELHO),
                    ('Melhorada', [m['RECEPCAO']['perdas'], m['OFICINA']['perdas'], m['QUALIDADE']['perdas']], VERDE)],
                   'clientes')
    grafico_estados('grafico_estados.png', a['OFICINA']['estados'], m['OFICINA']['estados'])

    slides = []
    # Capa
    slides.append(
        '<section class="slide capa"><div class="faixa">'
        '<p class="mini">T2 | Avaliacao de Aprendizagem</p>'
        '<h1>Avaliacao de um Modelo Simulado</h1>'
        '<p class="sub">Oficina Mecanica: analise e melhoria de uma rede de filas com realimentacao</p>'
        '</div><div class="capa-info">'
        '<p><b>Disciplina:</b> Simulacao e Metodos Analiticos</p>'
        '<p><b>Unidade de Aprendizagem:</b> UA2 | Fundamentos de Simulacao por Computador</p>'
        '<p><b>Modulo:</b> M9 | Avaliacao de um Modelo Simulado</p>'
        '<p><b>Grupo:</b> T2 - 690 - 16</p>'
        '<p><b>Integrantes:</b> Integrante 1, Integrante 2, Integrante 3, Integrante 4, Integrante 5, Integrante 6</p>'
        '<p>Porto Alegre, outubro de 2026</p></div></section>')

    slides.append(slide('Descricao da realidade a ser simulada',
        '<p>Uma oficina mecanica recebe veiculos para reparo. O cliente chega, abre uma ordem de servico na '
        '<b>RECEPCAO</b> (orcamento e cadastro) e o carro segue para a <b>OFICINA</b>, onde e reparado. Ao terminar, '
        'passa pelo <b>CONTROLE DE QUALIDADE</b> (teste do servico).</p>'
        '<h2>A rede tem realimentacao (nao e fluxo em tandem)</h2>'
        '<ul><li><b>Retrabalho:</b> se o teste reprova, o veiculo volta da QUALIDADE para a OFICINA.</li>'
        '<li><b>Pecas/orcamento:</b> parte dos servicos exige orcamento extra e volta da OFICINA para a RECEPCAO.</li></ul>'
        '<h2>Hipotese de modelagem</h2>'
        '<ul><li>Chegadas do exterior apenas na RECEPCAO; intervalos e tempos de servico uniformes U(a,b).</li>'
        '<li>Disciplina FCFS; capacidade finita em todas as filas (fila cheia na chegada = perda).</li>'
        '<li>Simulacao: 10 sementes x 100.000 numeros pseudoaleatorios (gerador congruente linear).</li></ul>', 2))

    slides.append(slide('Modelo (desenho) da rede de filas - situacao ATUAL',
        '<img class="desenho" src="rede_filas_atual.png">', 3))

    slides.append(slide('Descricao das filas (notacao de Kendall) e roteamento',
        '<table><tr><th>Fila</th><th>Notacao</th><th>Chegadas ext.</th><th>Atendimento</th>'
        '<th>Servidores</th><th>Capacidade</th></tr>'
        '<tr><td>RECEPCAO</td><td>G/G/1/8</td><td>U(6;12), 1a em 5,0</td><td>U(4;8)</td><td>1</td><td>8</td></tr>'
        '<tr><td>OFICINA</td><td>G/G/3/12</td><td>--</td><td>U(20;35)</td><td>3</td><td>12</td></tr>'
        '<tr><td>QUALIDADE</td><td>G/G/1/6</td><td>--</td><td>U(4;8)</td><td>1</td><td>6</td></tr></table>'
        '<h2>Probabilidades de roteamento</h2><ul>'
        '<li>RECEPCAO &rarr; OFICINA: 95% &nbsp;&middot;&nbsp; RECEPCAO &rarr; SAIDA: 5%</li>'
        '<li>OFICINA &rarr; QUALIDADE: 90% &nbsp;&middot;&nbsp; OFICINA &rarr; RECEPCAO: 5% (pecas) &nbsp;&middot;&nbsp; OFICINA &rarr; SAIDA: 5%</li>'
        '<li>QUALIDADE &rarr; OFICINA: 15% (retrabalho) &nbsp;&middot;&nbsp; QUALIDADE &rarr; SAIDA: 85%</li></ul>'
        '<p class="nota">A soma das probabilidades de cada fila e 1,0 (incluindo a saida da rede).</p>', 4))

    slides.append(slide('Resultados da simulacao - modelo ATUAL',
        '<table><tr><th>Fila</th><th>Perdas</th><th>N (populacao)</th><th>D (vazao/min)</th>'
        '<th>U (utilizacao)</th><th>W (min)</th></tr>'
        '<tr><td>RECEPCAO</td><td>{}</td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td></tr>'
        '<tr><td>OFICINA</td><td>{}</td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td></tr>'
        '<tr><td>QUALIDADE</td><td>{}</td><td>{}</td><td>{}</td><td>{}%</td><td>{}</td></tr></table>'
        '<img class="grafico" src="grafico_estados.png">'.format(
            a['RECEPCAO']['perdas'], br(a['RECEPCAO']['n']), br(a['RECEPCAO']['d'], 4), br(100 * a['RECEPCAO']['u']), br(a['RECEPCAO']['w']),
            a['OFICINA']['perdas'], br(a['OFICINA']['n']), br(a['OFICINA']['d'], 4), br(100 * a['OFICINA']['u']), br(a['OFICINA']['w']),
            a['QUALIDADE']['perdas'], br(a['QUALIDADE']['n']), br(a['QUALIDADE']['d'], 4), br(100 * a['QUALIDADE']['u']), br(a['QUALIDADE']['w'])), 5))

    slides.append(slide('Identificacao do gargalo',
        '<ul class="alerta">'
        '<li>A OFICINA esta saturada: U = 99,98% (todos os 3 mecanicos ocupados todo o tempo).</li>'
        '<li>Populacao media N = {} de 12 vagas; tempo de resposta W = {} min (~2h por veiculo, quase so espera).</li>'
        '<li>Foram perdidos {} clientes por fila cheia na OFICINA.</li></ul>'
        '<h2>A carga oferecida supera a capacidade instalada</h2><ul>'
        '<li>Taxa de atendimento: MU = 1/E[S] = 1/27,5 = 0,03636 cliente/min por mecanico.</li>'
        '<li>Capacidade da oficina: 3 &times; 0,03636 = 0,1091 cliente/min.</li>'
        '<li>Chegada efetiva a oficina: ~0,1291 cliente/min &rarr; rho = 0,1291/0,1091 = 1,18 (&gt; 1).</li></ul>'
        '<p class="destaque">Conclusao: e preciso aumentar a capacidade da OFICINA e/ou reduzir a carga que chega ate ela.</p>'.format(
            br(a['OFICINA']['n']), br(a['OFICINA']['w']), a['OFICINA']['perdas']), 6))

    slides.append(slide('Proposta de melhoria e modelo MELHORADO',
        '<ul><li><span class="vermelho"><b>OFICINA:</b> 3 &rarr; 4 mecanicos, capacidade 12 &rarr; 14, '
        'atendimento U(20;35) &rarr; U(18;30) (contratacao + elevador/ferramenta).</span></li>'
        '<li><span class="verde"><b>QUALIDADE:</b> capacidade 6 &rarr; 8 e retrabalho 15% &rarr; 10% '
        '(treinamento reduz devolucoes).</span></li>'
        '<li><b>RECEPCAO:</b> capacidade 8 &rarr; 10 (evita perdas de ordens na chegada).</li></ul>'
        '<img class="desenho" src="rede_filas_melhorada.png">', 7))

    slides.append(slide('Comparacao dos resultados (antes x depois)',
        '<div class="duas-colunas"><div class="col-esq">'
        '<table><tr><th>Fila</th><th>Metrica</th><th>Atual</th><th>Melhorada</th><th>Variacao</th></tr>'
        '<tr><td>OFICINA</td><td>Perdas</td><td>{}</td><td>{}</td><td>zerou</td></tr>'
        '<tr><td>OFICINA</td><td>N (populacao)</td><td>{}</td><td>{}</td><td>-{}</td></tr>'
        '<tr><td>OFICINA</td><td>D (vazao/min)</td><td>{}</td><td>{}</td><td>+{}%</td></tr>'
        '<tr><td>OFICINA</td><td>U (utilizacao)</td><td>{}%</td><td>{}%</td><td>-{} p.p.</td></tr>'
        '<tr><td>OFICINA</td><td>W (min)</td><td>{}</td><td>{}</td><td>-{}%</td></tr></table>'
        '</div><div class="col-dir">'
        '<img class="grafico" src="grafico_w.png"><img class="grafico" src="grafico_perdas.png">'
        '</div></div>'.format(
            a['OFICINA']['perdas'], m['OFICINA']['perdas'],
            br(a['OFICINA']['n']), br(m['OFICINA']['n']), br(a['OFICINA']['n'] - m['OFICINA']['n']),
            br(a['OFICINA']['d'], 4), br(m['OFICINA']['d'], 4), br(100 * (m['OFICINA']['d'] / a['OFICINA']['d'] - 1), 1),
            br(100 * a['OFICINA']['u']), br(100 * m['OFICINA']['u']), br(100 * (a['OFICINA']['u'] - m['OFICINA']['u']), 1),
            br(a['OFICINA']['w']), br(m['OFICINA']['w']), br(100 * (1 - m['OFICINA']['w'] / a['OFICINA']['w']), 1)), 8))

    slides.append(slide('Conclusoes finais',
        '<ul>'
        '<li>A simulacao revelou que a <b>OFICINA</b> e o gargalo: saturada (U~100%), com longas esperas e 21.406 perdas.</li>'
        '<li>A melhoria (mais um mecanico, processo mais rapido e menor retrabalho) <b>zerou as perdas</b> da oficina.</li>'
        '<li class="verde">O tempo de resposta na OFICINA caiu de {} min para {} min ({}% melhor).</li>'
        '<li>A vazao da oficina aumentou (mais veiculos entregues por minuto) com utilizacao confortavel (73%).</li>'
        '<li>A QUALIDADE absorveu o maior fluxo sem perdas; a RECEPCAO praticamente nao mudou.</li></ul>'
        '<h2>Trabalhos futuros</h2><ul>'
        '<li>Analisar custo x beneficio (mecanico extra + equipamento vs. perda de clientes).</li>'
        '<li>Executar varias replicacoes e intervalos de confianca para os indices.</li></ul>'.format(
            br(a['OFICINA']['w']), br(m['OFICINA']['w']),
            br(100 * (1 - m['OFICINA']['w'] / a['OFICINA']['w']), 1)), 9))

    slides.append(slide('Arquivos e reproducao',
        '<h2>O pacote contem</h2><ul>'
        '<li>modelos/oficina.yml e modelos/oficina_melhorada.yml - modelos antes e depois da melhoria.</li>'
        '<li>simulador.py - simulador de rede de filas (nosso, do T1) com o calculo dos indices.</li>'
        '<li>resultados/oficina_atual.txt e oficina_melhorada.txt - saidas completas (tempos/probabilidades por estado).</li>'
        '<li>planilhas/indices_oficina.xlsx - calculo dos indices.</li></ul>'
        '<h2>Como reproduzir</h2>'
        '<pre>pip install pyyaml\npython3 simulador.py modelos/oficina.yml\npython3 simulador.py modelos/oficina_melhorada.yml</pre>'
        '<p class="nota">Formulas: MU = 1/E[S]; N = soma k.P(k); D = MU.Ns; U = Ns/servidores; W = N/D.</p>', 10))

    html = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>T2 | Oficina Mecanica</title><style>
@page { size: 11in 8.5in; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Segoe UI", Arial, sans-serif; color: #333; }
.slide { width: 11in; height: 8.5in; padding: 0.6in 0.7in; position: relative;
         page-break-after: always; overflow: hidden; }
.topbar { position: absolute; top: 0; left: 0; width: 100%; height: 0.18in; background: #1F4E79; }
h1 { color: #1F4E79; font-size: 30px; margin: 0.18in 0 0.28in; }
h2 { color: #1F4E79; font-size: 20px; margin: 0.18in 0 0.08in; }
p, li { font-size: 17px; line-height: 1.5; }
ul { margin: 0.05in 0 0 0.2in; padding-left: 0.2in; }
table { border-collapse: collapse; width: 100%; margin: 0.12in 0; }
th { background: #1F4E79; color: #fff; padding: 8px 9px; font-size: 15px; }
td { border: 1px solid #c9d6e5; padding: 7px 9px; font-size: 15px; text-align: center; }
td:first-child { text-align: left; font-weight: 600; }
tr:nth-child(even) td { background: #DEEBF7; }
.rodape { position: absolute; right: 0.7in; bottom: 0.25in; color: #595959; font-size: 12px; }
.capa .faixa { background: #1F4E79; color: #fff; padding: 0.7in 0.7in; margin: -0.6in -0.7in 0.45in; }
.capa .mini { color: #BDD7EE; font-size: 22px; margin: 0; }
.capa h1 { color: #fff; font-size: 46px; margin: 0.1in 0; }
.capa .sub { color: #fff; font-size: 22px; margin: 0; }
.capa-info p { font-size: 17px; margin: 0.07in 0; }
.desenho { display: block; width: 100%; max-height: 5.3in; object-fit: contain; margin-top: 0.05in; }
.grafico { display: block; width: 100%; max-height: 4.9in; object-fit: contain; }
.duas-colunas { display: flex; gap: 0.3in; }
.col-esq { flex: 1.1; } .col-dir { flex: 1; }
.col-dir .grafico { max-height: 3.0in; }
.alerta li { color: #C00000; }
.vermelho { color: #C00000; } .verde { color: #2E7D32; }
.destaque { color: #2E7D32; font-weight: 600; }
.nota { color: #595959; font-style: italic; font-size: 14px; }
pre { background: #F2F2F2; border: 1px solid #ddd; padding: 10px; font-size: 13px; }
</style></head><body>''' + '\n'.join(slides) + '</body></html>'

    caminho = os.path.join(APRES, 'T2_Oficina_Mecanica.html')
    with open(caminho, 'w', encoding='utf-8') as arquivo:
        arquivo.write(html)
    print('gerado:', caminho)


if __name__ == '__main__':
    main()
