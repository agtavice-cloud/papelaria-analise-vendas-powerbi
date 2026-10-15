"""Gera dados sintéticos para estudo. Requer apenas Python 3."""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RNG = random.Random(20261012)
CATALOGO = [
    ('Caderno universitário', 'Cadernos', 2590),
    ('Caderno pequeno', 'Cadernos', 1290),
    ('Caneta azul', 'Escrita', 350),
    ('Caneta preta', 'Escrita', 350),
    ('Lápis grafite', 'Escrita', 200),
    ('Borracha branca', 'Acessórios', 250),
    ('Régua 30 cm', 'Acessórios', 590),
    ('Estojo escolar', 'Acessórios', 1990),
    ('Mochila escolar', 'Mochilas', 12990),
    ('Papel A4 500 folhas', 'Papéis', 3290),
]
FIELDS = ['id_item', 'id_venda', 'data', 'produto', 'categoria',
          'quantidade', 'preco_unitario', 'desconto', 'forma_pagamento']

def dinheiro(centavos):
    return f'{centavos // 100},{centavos % 100:02d}'

def escrever(nome, campos, registros):
    with (ROOT / nome).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=campos, delimiter=';')
        writer.writeheader()
        writer.writerows(registros)

def gerar():
    base = []
    totais = {}
    for venda in range(1, 151):
        dia = date(2026, 1, 1) + timedelta(days=RNG.randrange(90))
        pagamento = RNG.choice(['Pix', 'Cartão de crédito', 'Cartão de débito', 'Dinheiro'])
        for _ in range(2):
            produto, categoria, preco = RNG.choice(CATALOGO)
            qtd = RNG.randint(1, 5)
            desconto = RNG.choice([0, 0, 0, 100, 200])
            item = f'ITEM-{len(base)+1:04d}'
            base.append(dict(zip(FIELDS, [item, f'VENDA-{venda:03d}', dia.strftime('%d/%m/%Y'),
                produto, categoria, str(qtd), dinheiro(preco), dinheiro(desconto), pagamento])))
            totais[item] = qtd * preco - desconto
    suja = [dict(r) for r in base]
    log = []
    def registrar(i, campo, tipo, novo):
        log.append({'linha_csv': i+2, 'id_item': suja[i]['id_item'], 'campo': campo,
                    'tipo': tipo, 'antes': suja[i][campo], 'depois': novo})
        suja[i][campo] = novo
    for i in range(0, 4): registrar(i, 'quantidade', 'campo_essencial_vazio', '')
    for i in range(4, 8): registrar(i, 'quantidade', 'quantidade_negativa', '-2')
    for i in range(8, 12): registrar(i, 'desconto', 'desconto_superior_ao_valor', '9999,00')
    for i in range(30, 60):
        original = suja[i]['data']
        registrar(i, 'data', 'formato_alternativo', date(int(original[6:]), int(original[3:5]), int(original[:2])).isoformat())
    for i in range(60, 90): registrar(i, 'preco_unitario', 'simbolo_monetario', 'R$ ' + suja[i]['preco_unitario'])
    for i in range(90, 120): registrar(i, 'produto', 'maiusculas_e_espacos', '  ' + suja[i]['produto'].upper() + '  ')
    for i in range(120, 150): registrar(i, 'preco_unitario', 'ponto_decimal', suja[i]['preco_unitario'].replace(',', '.'))
    for i in range(20, 30):
        suja.append(dict(suja[i]))
        log.append({'linha_csv': len(suja)+1, 'id_item': suja[i]['id_item'], 'campo': '*',
                    'tipo': 'duplicata_identica', 'antes': '', 'depois': 'cópia integral'})
    conflito = dict(suja[12])
    conflito['preco_unitario'] = '1,00'
    suja.append(conflito)
    log.append({'linha_csv': len(suja)+1, 'id_item': conflito['id_item'], 'campo': 'preco_unitario',
                'tipo': 'id_com_informacoes_conflitantes', 'antes': suja[12]['preco_unitario'], 'depois': '1,00'})
    escrever('vendas_referencia.csv', FIELDS, base)
    escrever('vendas_para_limpeza.csv', FIELDS, suja)
    escrever('catalogo_produtos.csv', ['produto', 'categoria', 'preco_referencia'],
             [{'produto': p, 'categoria': c, 'preco_referencia': dinheiro(v)} for p, c, v in CATALOGO])
    escrever('gabarito_alteracoes.csv', list(log[0]), log)
    aprovados = base[13:]
    esperado = {
        'dados_sinteticos': True, 'semente': 20261012,
        'linhas_referencia': 300, 'linhas_entrada': len(suja),
        'duplicatas_identicas_remover': 10, 'linhas_para_revisao': 14,
        'ids_distintos_para_revisao': 13, 'itens_validos': len(aprovados),
        'vendas_distintas_com_itens_validos': len({r['id_venda'] for r in aprovados}),
        'receita_itens_validos_centavos': sum(totais[r['id_item']] for r in aprovados),
        'receita_referencia_completa_centavos': sum(totais.values()),
        'nota': 'Receita após exclusões não é a receita completa. A venda com ITEM-0014 tem outro item pendente.',
    }
    (ROOT / 'resultado_esperado.json').write_text(json.dumps(esperado, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    assert len(suja) == 311
    assert esperado['itens_validos'] + esperado['linhas_para_revisao'] + 10 == 311
    print(json.dumps(esperado, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    gerar()
