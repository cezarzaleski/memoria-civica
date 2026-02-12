"""Padrões regex para classificação cívica de proposições legislativas.

Define os padrões de texto (regex) para cada categoria cívica.
Cada categoria possui uma lista de expressões regulares que são
aplicadas contra a ementa e palavras-chave da proposição.

Todas as expressões usam flag IGNORECASE na compilação.
"""

CIVIC_PATTERNS: dict[str, list[str]] = {
    "GASTOS_PUBLICOS": [
        r"cr[ée]dito\s+(suplementar|especial|extraordin[aá]rio)",
        r"despesas?\s+p[uú]blicas?",
        r"dota[çc][ãa]o\s+or[çc]ament[aá]ria",
        r"or[çc]amento\s+(geral|anual|p[uú]blico|da\s+uni[ãa]o)",
        r"\b(LOA|LDO|PPA)\b",
        r"precat[oó]rios?",
        r"gastos?\s+p[uú]blicos?",
        r"d[ée]ficit\s+(p[uú]blico|or[çc]ament[aá]rio|fiscal)",
        r"super[aá]vit\s+(prim[aá]rio|fiscal|or[çc]ament[aá]rio)",
        r"teto\s+de\s+gastos",
        r"responsabilidade\s+fiscal",
        r"d[ií]vida\s+p[uú]blica",
    ],
    "TRIBUTACAO_AUMENTO": [
        r"aument\w+.{0,15}(tribut|impost|contribui[çc]|al[ií]quota)",
        r"major\w+.{0,15}(tribut|impost|al[ií]quota)",
        r"(cria|institu)\w*\s+(nov[ao]s?\s+)?(tribut|impost|contribui[çc]|taxa)",
        r"eleva[çc][ãa]o.{0,15}(tribut|impost|al[ií]quota)",
        r"aumento\s+d[aeo]\s+carga\s+tribut[aá]ria",
    ],
    "TRIBUTACAO_ISENCAO": [
        r"isen[çc][ãa]o\s+(tribut[aá]ria|fiscal|de\s+impost)",
        r"redu[çc][ãa]o\s+(d[aeo]s?\s+)?(tribut|al[ií]quota|impost|contribui[çc])",
        r"desonera[çc][ãa]o",
        r"benef[ií]cio\s+fiscal",
        r"imunidade\s+tribut[aá]ria",
        r"Simples\s+Nacional",
        r"remiss[ãa]o\s+(fiscal|tribut[aá]ria)",
        r"incentivo\s+fiscal",
    ],
    "BENEFICIOS_CATEGORIAS": [
        r"servidor(es)?\s+p[uú]blico",
        r"(reajuste|aumento).{0,30}(remunera[çc]|sal[aá]rio|subs[ií]dio|vencimento)",
        r"piso\s+salarial",
        r"aposentadoria.{0,30}(servidor|militar|policial|magistrad|membro)",
        r"pens[ãa]o.{0,30}(servidor|militar|policial|magistrad|membro)",
        r"gratifica[çc][ãa]o.{0,30}(servidor|militar|policial|magistrad)",
        r"carreira\w*\s+(d[aeo]s?\s+)?(servidor|militar|policial|magistrad|membro)",
    ],
    "DIREITOS_SOCIAIS": [
        r"sa[uú]de\s+p[uú]blica",
        r"\bSUS\b",
        r"educa[çc][ãa]o\s+(p[uú]blica|b[aá]sica|fundamental|infantil|superior)",
        r"moradia\s+(popular|social)",
        r"previd[eê]ncia\s+social",
        r"assist[eê]ncia\s+social",
        r"Bolsa\s+Fam[ií]lia",
        r"\bBPC\b",
        r"seguro.desemprego",
        r"sal[aá]rio.m[ií]nimo",
        r"direitos?\s+(sociai?s|humanos|fundamentai?s|trabalhist)",
        r"programa\s+social",
    ],
    "SEGURANCA_JUSTICA": [
        r"c[oó]digo\s+penal",
        r"c[oó]digo\s+de\s+processo\s+(penal|civil)",
        r"crime\w*\s+(de|contra|hediondo)",
        r"pena\s+(de|para|m[ií]nima|m[aá]xima)",
        r"arma\w*\s+de\s+fogo",
        r"tr[aá]fico\s+(de\s+drogas?|il[ií]cito)",
        r"viol[eê]ncia\s+(dom[eé]stica|contra|urbana|sexual)",
        r"seguran[çc]a\s+p[uú]blica",
        r"sistema\s+(prisional|penitenci[aá]rio|carcer[aá]rio)",
        r"execu[çc][ãa]o\s+penal",
    ],
    "MEIO_AMBIENTE": [
        r"meio\s+ambiente",
        r"prote[çc][ãa]o\s+ambiental",
        r"licenciamento\s+ambiental",
        r"desmatamento",
        r"polui[çc][ãa]o",
        r"sustentabilidade",
        r"emiss[ãõ]\w*\s+(de\s+)?(gases?|carbono|poluent)",
        r"biodiversidade",
        r"reserva\s+(ambiental|biol[oó]gica|florestal|ecol[oó]gica)",
        r"energia\w*\s+(renov[aá]vel|limpa|solar|e[oó]lica)",
        r"\bunidades?\s+de\s+conserva[çc][ãa]o\b",
    ],
    "REGULACAO_ECONOMICA": [
        r"regula[çc][ãa]o\s+(econ[oô]mica|financeira|banc[aá]ria|do\s+mercado)",
        r"mercado\s+(financeiro|de\s+capitais)",
        r"Banco\s+Central",
        r"taxa\s+(de\s+juros|Selic|b[aá]sica)",
        r"privatiza[çc][ãa]o",
        r"concess[ãa]o\s+(de\s+servi[çc]o|p[uú]blica)",
        r"licita[çc][ãõ]",
        r"marco\s+regulat[oó]rio",
        r"ag[eê]ncia\w*\s+regulador",
    ],
    "POLITICA_INSTITUCIONAL": [
        r"emenda\s+constitucional",
        r"regimento\s+interno",
        r"processo\s+legislativo",
        r"elei[çc][ãõ]\w*",
        r"propaganda\s+(eleitoral|partid[aá]ria)",
        r"fundo\s+(eleitoral|partid[aá]rio)",
        r"fidelidade\s+partid[aá]ria",
        r"imunidade\s+parlamentar",
        r"\bCPI\b",
        r"reforma\s+(pol[ií]tica|eleitoral|partid[aá]ria)",
        r"voto\s+(impresso|distrital|secreto|obrigat[oó]rio)",
    ],
}
"""Mapeamento de código de categoria → lista de padrões regex.

Cada padrão é aplicado com re.IGNORECASE. Os padrões são projetados
para capturar termos comuns em ementas de proposições legislativas
brasileiras da Câmara dos Deputados.
"""
