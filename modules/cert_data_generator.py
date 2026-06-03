import random

random.seed(42)


NOMBRES = [
    "ANGELA", "MARIA", "CARLOS", "JUAN", "DIANA", "LUIS", "ANA", "JOSE",
    "PEDRO", "LAURA", "ANDREA", "JORGE", "PATRICIA", "DAVID", "CLAUDIA",
    "ANDRES", "MARCELA", "FELIPE", "MONICA", "ALEJANDRO", "SANDRA", "MIGUEL",
    "CAROLINA", "RAFAEL", "BEATRIZ", "SERGIO", "GLORIA", "FERNANDO",
    "ELIZABETH", "OSCAR", "MARTHA", "HERNAN", "LILIANA", "JULIAN", "NATALIA",
    "CESAR", "VIVIANA", "JHON", "LEIDY", "ROBINSON", "YESENIA", "FABIAN",
    "ADRIANA", "WILSON", "OLGA", "HENRY", "PAOLA", "EDGAR", "LUZ", "ROSA",
]

APELLIDOS = [
    "GARCIA", "LOPEZ", "MARTINEZ", "RODRIGUEZ", "PEREZ", "SANCHEZ", "RAMIREZ",
    "TORRES", "FLORES", "VARGAS", "VALDERRAMA", "SOLORZANO", "SALAZAR",
    "VELEZ", "MORALES", "JIMENEZ", "HERRERA", "MEDINA", "REYES", "GOMEZ",
    "CASTRO", "ORTIZ", "RUBIO", "MENDEZ", "SILVA", "RAMOS", "MOLINA",
    "DELGADO", "LEON", "GUTIERREZ", "CARDONA", "ZAPATA", "ARANGO", "MESA",
    "BEDOYA", "OSPINA", "LONDONO", "AGUDELO", "MONTOYA", "CANO", "GIRALDO",
    "VILLA", "OCAMPO", "FRANCO", "RESTREPO", "POSADA", "MUÑOZ", "CORREA",
    "ACOSTA", "ROJAS", "PARRA", "NARANJO", "RIOS", "HENAO", "ZULUAGA",
]

CIUDADES_TOKENS = [
    ["Medellín"], ["Bogotá"], ["Cali"], ["Barranquilla"], ["Cartagena"],
    ["Bucaramanga"], ["Pereira"], ["Armenia"], ["Manizales"], ["Bello"],
    ["Itagüí"], ["Envigado"], ["Sabaneta"], ["Rionegro"], ["Apartadó"],
    ["Montería"], ["Sincelejo"], ["Villavicencio"], ["Pasto"], ["Ibagué"],
    ["Neiva"], ["Valledupar"], ["Palmira"], ["Popayán"], ["Tunja"],
    ["La", "Estrella"], ["La", "Ceja"], ["El", "Retiro"], ["El", "Carmen"],
    ["Santa", "Rosa", "de", "Osos"], ["San", "Pedro"],
    ["MEDELLIN"], ["BOGOTA"], ["CALI"], ["BARRANQUILLA"], ["CARTAGENA"],
    ["BUCARAMANGA"], ["PEREIRA"], ["ARMENIA"], ["MANIZALES"], ["BELLO"],
    ["ITAGUI"], ["ENVIGADO"], ["SABANETA"], ["LA", "ESTRELLA"],
]

ORGS_TOKENS = [
    ["SENA"],
    ["Bancolombia"],
    ["EPM"],
    ["Colpensiones"],
    ["DIAN"],
    ["ICFES"],
    ["ICBF"],
    ["Ecopetrol"],
    ["Telecom"],
    ["Coltejer"],
    ["REGIONAL", "ANTIOQUIA"],
    ["CENTRO", "DE", "COMERCIO", "REGIONAL", "ANTIOQUIA", "SENA"],
    ["CENTRO", "INDUSTRIAL", "DEL", "DISEÑO", "Y", "LA", "MANUFACTURA"],
    ["SERVICIO", "NACIONAL", "DE", "APRENDIZAJE"],
    ["Universidad", "de", "Antioquia"],
    ["Universidad", "Nacional", "de", "Colombia"],
    ["Universidad", "de", "Medellín"],
    ["Universidad", "EAFIT"],
    ["Instituto", "Tecnológico", "Metropolitano"],
    ["Cámara", "de", "Comercio", "de", "Medellín"],
    ["Gobernación", "de", "Antioquia"],
    ["Alcaldía", "de", "Medellín"],
    ["Ministerio", "de", "Educación", "Nacional"],
    ["Ministerio", "de", "Trabajo"],
    ["Contraloría", "General", "de", "la", "República"],
    ["Procuraduría", "General", "de", "la", "Nación"],
    ["CENTRO", "DE", "COMERCIO"],
    ["CENTRO", "AGROPECUARIO"],
    ["CENTRO", "DE", "SERVICIOS", "DE", "SALUD"],
    ["COMPLEJO", "TECNOLOGICO", "PARA", "LA", "GESTION", "AGROEMPRESARIAL"],
]

CURSOS = [
    "REDACCION Y ORTOGRAFIA", "CONTABILIDAD BASICA",
    "SISTEMAS DE INFORMACION", "EXCEL AVANZADO", "SERVICIO AL CLIENTE",
    "GESTION DOCUMENTAL", "SEGURIDAD Y SALUD EN EL TRABAJO",
    "INGLES BASICO", "MATEMATICAS APLICADAS", "PROGRAMACION WEB",
    "LOGISTICA Y CADENA DE SUMINISTRO", "GESTION HUMANA",
    "MERCADEO Y VENTAS", "MANIPULACION DE ALIMENTOS", "PRIMEROS AUXILIOS",
    "CONTABILIDAD SISTEMATIZADA", "ADMINISTRACION DE EMPRESAS",
    "GESTION DE CALIDAD", "TRABAJO EN ALTURAS", "MANEJO DE RESIDUOS",
    "ATENCION AL USUARIO", "COMPETENCIAS CIUDADANAS",
]

CARGOS = [
    "DIRECTOR", "DIRECTORA", "SUBDIRECTOR", "SUBDIRECTORA",
    "RECTOR", "RECTORA", "COORDINADOR", "COORDINADORA",
    "INSTRUCTOR", "INSTRUCTORA", "DOCENTE", "JEFE", "GERENTE",
    "SECRETARIO", "SECRETARIA", "PRESIDENTE", "PRESIDENTA",
    "COORDINADORA ACADEMICA", "DIRECTOR REGIONAL", "SUBDIRECTOR ACADEMICO",
]

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

NUMS_ESCRITOS = [
    "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
    "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
    "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco",
    "veintiséis", "veintisiete", "veintiocho", "veintinueve", "treinta",
    "treinta y uno",
]


def _gen_per():
    n1 = random.randint(1, 2)
    n2 = random.randint(1, 2)
    toks = random.sample(NOMBRES, n1) + random.sample(APELLIDOS, n2)
    labels = ["B-PER"] + ["I-PER"] * (len(toks) - 1)
    return toks, labels


def _gen_org():
    toks = list(random.choice(ORGS_TOKENS))
    labels = ["B-ORG"] + ["I-ORG"] * (len(toks) - 1)
    return toks, labels


def _gen_loc():
    toks = list(random.choice(CIUDADES_TOKENS))
    labels = ["B-LOC"] + ["I-LOC"] * (len(toks) - 1)
    return toks, labels


def _o(*words):
    return list(words), ["O"] * len(words)


def _join(*parts):
    toks, labels = [], []
    for t, l in parts:
        toks += t
        labels += l
    return toks, labels



def _tmpl_certifica():
    org = _gen_org()
    per = _gen_per()
    curso = random.choice(CURSOS)
    return _join(
        org,
        _o("CERTIFICA", "que"),
        per,
        _o("realizó", "y", "aprobó", "el", "curso", "de", curso, "."),
    )


def _tmpl_certifica_2():
    org = _gen_org()
    per = _gen_per()
    return _join(
        org,
        _o("certifica", "que"),
        per,
        _o("ha", "culminado", "satisfactoriamente", "el", "programa", "de", "formación", "."),
    )


def _tmpl_expide():
    loc = _gen_loc()
    dia = str(random.randint(1, 28))
    mes = random.choice(MESES)
    anio = str(random.randint(2015, 2024))
    return _join(
        _o("Se", "expide", "en"),
        loc,
        _o("el", dia, "de", mes, "de", anio, "."),
    )


def _tmpl_expide_escrito():
    loc = _gen_loc()
    dia = random.choice(NUMS_ESCRITOS)
    n_dia = str(random.randint(1, 28))
    mes = random.choice(MESES)
    anio = str(random.randint(2015, 2024))
    return _join(
        _o("Dado", "en"),
        loc,
        _o("a", "los", f"{dia}", f"({n_dia})", "días", "del", "mes", "de", mes, "de", anio, "."),
    )


def _tmpl_cargo_org():
    cargo = random.choice(CARGOS)
    org = _gen_org()
    return _join(_o(cargo), org)


def _tmpl_per_cargo_org():
    per = _gen_per()
    cargo = random.choice(CARGOS)
    org = _gen_org()
    return _join(per, _o(cargo), org)


def _tmpl_identificacion():
    per = _gen_per()
    loc = _gen_loc()
    num = str(random.randint(1000000000, 1099999999))
    doc = random.choice(["Cédula de Ciudadanía", "Tarjeta de Identidad"])
    return _join(
        per,
        _o("identificado", "con", doc, "No", num, "de"),
        loc,
        _o(","),
    )


def _tmpl_identificacion_2():
    per = _gen_per()
    loc = _gen_loc()
    num = str(random.randint(1000000000, 1099999999))
    return _join(
        _o("Número", "de", "documento", ":"),
        _o(num, "de"),
        loc,
        _o("Nombre", ":"),
        per,
        _o("."),
    )


def _tmpl_sede():
    org = _gen_org()
    loc = _gen_loc()
    return _join(
        org,
        _o("con", "sede", "en"),
        loc,
        _o("."),
    )


def _tmpl_firma():
    per = _gen_per()
    cargo = random.choice(CARGOS)
    org = _gen_org()
    return _join(per, _o(cargo, "de"), org)


def _tmpl_autenticidad():
    per = _gen_per()
    org = _gen_org()
    return _join(
        _o("La", "autenticidad", "de", "este", "documento", "puede", "ser", "verificada", "en"),
        org,
        _o("o", "contactando", "a"),
        per,
        _o("."),
    )


def _tmpl_regional():
    org = _gen_org()
    loc = _gen_loc()
    return _join(
        _o("REGIONAL"),
        loc,
        _o("-"),
        org,
    )


def _tmpl_intensidad():
    per = _gen_per()
    curso = random.choice(CURSOS)
    horas = str(random.choice([40, 80, 120, 160, 200, 240]))
    return _join(
        per,
        _o("completó", "el", "curso", "de", curso, "con", "una", "intensidad", "horaria",
           "de", horas, "horas", "."),
    )


def _tmpl_simple_per():
    return _gen_per()


def _tmpl_simple_org():
    return _gen_org()


def _tmpl_simple_loc():
    return _gen_loc()


def _tmpl_nacido():
    per = _gen_per()
    loc = _gen_loc()
    return _join(
        per,
        _o("nacido", "en"),
        loc,
        _o("."),
    )


def _tmpl_expedido_por():
    org = _gen_org()
    loc = _gen_loc()
    return _join(
        _o("Expedido", "por"),
        org,
        _o("en"),
        loc,
        _o("."),
    )


_TEMPLATES = [
    _tmpl_certifica,
    _tmpl_certifica,
    _tmpl_certifica_2,
    _tmpl_expide,
    _tmpl_expide,
    _tmpl_expide_escrito,
    _tmpl_expide_escrito,
    _tmpl_cargo_org,
    _tmpl_cargo_org,
    _tmpl_per_cargo_org,
    _tmpl_per_cargo_org,
    _tmpl_identificacion,
    _tmpl_identificacion,
    _tmpl_identificacion_2,
    _tmpl_sede,
    _tmpl_firma,
    _tmpl_firma,
    _tmpl_autenticidad,
    _tmpl_regional,
    _tmpl_intensidad,
    _tmpl_simple_per,
    _tmpl_simple_org,
    _tmpl_simple_loc,
    _tmpl_nacido,
    _tmpl_expedido_por,
]


def generate(n: int = 1200) -> list[tuple[list[str], list[str]]]:
    data = []
    for _ in range(n):
        tmpl = random.choice(_TEMPLATES)
        toks, labels = tmpl()
        if toks:
            data.append((toks, labels))
    random.shuffle(data)
    return data
