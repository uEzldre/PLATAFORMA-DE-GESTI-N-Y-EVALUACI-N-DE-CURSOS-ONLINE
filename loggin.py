# parte de luis
from abc import ABC, abstractmethod

class Usuario(ABC):
    def __init__(self, uid: str, nombre: str) -> None:
        self.uid = uid
        self.nombre = nombre
    @abstractmethod
    def rol(self) -> str: ...

class Estudiante(Usuario):
    def __init__(self, uid: str, nombre: str) -> None:
        super().__init__(uid, nombre)
        self.cursos = []
    def rol(self) -> str: return "estudiante"

class Instructor(Usuario):
    def __init__(self, uid: str, nombre: str) -> None:
        super().__init__(uid, nombre)
        self.cursos_impartidos = []
    def rol(self) -> str: return "instructor"

class Plataforma:
    def __init__(self) -> None:
        self.usuarios = {}    # uid -> Usuario
        self.cursos = {}      # codigo -> dict
        self._seq_est = 0
        self._seq_inst = 0

    def crear_usuario(self, tipo: str, nombre: str) -> Usuario:
        if tipo.lower() == "estudiante":
            self._seq_est += 1
            uid = f"estudiante {self._seq_est}"
            u = Estudiante(uid, nombre or f"Est {self._seq_est}")
        elif tipo.lower() == "instructor":
            self._seq_inst += 1
            uid = f"instructor {self._seq_inst}"
            u = Instructor(uid, nombre or f"Inst {self._seq_inst}")
        else:
            raise ValueError("Tipo inválido")
        self.usuarios[uid] = u
        return u

    def crear_curso(self, codigo: str, nombre: str, uid_instructor: str) -> None:
        if not codigo: raise ValueError("Código vacío")
        if codigo in self.cursos: raise ValueError("Curso ya existe")
        inst = self.usuarios.get(uid_instructor)
        if not isinstance(inst, Instructor): raise KeyError("Instructor no encontrado")
        self.cursos[codigo] = {"nombre": nombre or codigo, "instructor": uid_instructor, "inscritos": [], "evaluaciones": []}
        inst.cursos_impartidos.append(codigo)

    def inscribir(self, codigo: str, uid_est: str) -> None:
        curso = self.cursos.get(codigo)
        if not curso: raise KeyError("Curso no encontrado")
        est = self.usuarios.get(uid_est)
        if not isinstance(est, Estudiante): raise KeyError("Estudiante no encontrado")
        if uid_est in curso["inscritos"]: raise ValueError("Ya inscrito")
        curso["inscritos"].append(uid_est)
        est.cursos.append(codigo)

    def crear_evaluacion(self, codigo: str, titulo: str, ponderacion: str) -> None:
        curso = self.cursos.get(codigo)
        if not curso: raise KeyError("Curso no encontrado")
        curso["evaluaciones"].append({"titulo": titulo or "Evaluación", "ponderacion": ponderacion or "", "calificaciones": {}})

    def registrar_nota(self, codigo: str, idx_eval: int, uid_est: str, nota: str) -> None:
        curso = self.cursos.get(codigo)
        if not curso: raise KeyError("Curso no encontrado")
        if not (0 <= idx_eval < len(curso["evaluaciones"])): raise KeyError("Evaluación no encontrada")
        if uid_est not in curso["inscritos"]: raise ValueError("No inscrito")
        try:
            n = float(nota)
        except:
            raise ValueError("Nota inválida")
        if not (0 <= n <= 100): raise ValueError("Nota fuera de rango")
        curso["evaluaciones"][idx_eval]["calificaciones"][uid_est] = n

# acciones (definidas antes del menú; el menú solo las invoca)

def accion_registrar_instructor(sistema: Plataforma):
    print("\tregistrar nuevo instructor:")
    nombre = input("Nombre:\n").strip()
    u = sistema.crear_usuario("instructor", nombre)
    print(f"Instructor creado: {u.uid}")

def accion_registrar_estudiante(sistema: Plataforma):
    print("\tRegistrar nuevo estudiante:")
    nombre = input("Nombre:\n").strip()
    u = sistema.crear_usuario("estudiante", nombre)
    print(f"Estudiante creado: {u.uid}")

def accion_crear_curso(sistema: Plataforma):
    instructores = [(uid, u.nombre) for uid, u in sistema.usuarios.items() if isinstance(u, Instructor)]
    if not instructores:
        print("Primero registra instructores"); return
    print("\n-- INSTRUCTORES --")
    for i, (uid, nom) in enumerate(instructores, 1):
        print(f"{i}) {nom} ({uid})")
    try:
        pos = int(input("Número de instructor: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos < 0 or pos >= len(instructores):
        print("Selección inválida"); return
    uid_inst = instructores[pos][0]
    codigo = input("Código del curso: ").strip()
    nombre = input("Nombre del curso: ").strip()
    try:
        sistema.crear_curso(codigo, nombre, uid_inst)
        print("Curso creado")
    except Exception as e:
        print("Error:", e)

def accion_inscribir_estudiante(sistema: Plataforma):
    if not sistema.cursos:
        print("Primero crea cursos"); return
    cursos = list(sistema.cursos.items())
    print("\n-- CURSOS --")
    for i, (cod, info) in enumerate(cursos, 1):
        print(f"{i}) {cod} | {info['nombre']}")
    try:
        pos_c = int(input("Número de curso: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos_c < 0 or pos_c >= len(cursos):
        print("Selección inválida"); return
    cod = cursos[pos_c][0]

    estudiantes = [(uid, u.nombre) for uid, u in sistema.usuarios.items() if isinstance(u, Estudiante)]
    if not estudiantes:
        print("Primero registra estudiantes"); return
    print("\n-- ESTUDIANTES --")
    for i, (uid, nom) in enumerate(estudiantes, 1):
        print(f"{i}) {nom} ({uid})")
    try:
        pos_e = int(input("Número de estudiante: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos_e < 0 or pos_e >= len(estudiantes):
        print("Selección inválida"); return
    uid_est = estudiantes[pos_e][0]

    try:
        sistema.inscribir(cod, uid_est)
        print("Inscripción hecha")
    except Exception as e:
        print("Error:", e)

def accion_crear_evaluacion(sistema: Plataforma):
    if not sistema.cursos:
        print("Primero crea cursos"); return
    cursos = list(sistema.cursos.items())
    print("\n-- CURSOS --")
    for i, (cod, info) in enumerate(cursos, 1):
        print(f"{i}) {cod} | {info['nombre']}")
    try:
        pos_c = int(input("Número de curso: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos_c < 0 or pos_c >= len(cursos):
        print("Selección inválida"); return
    cod = cursos[pos_c][0]
    titulo = input("Título: ").strip()
    pond = input("Ponderación (0..100): ").strip()
    try:
        sistema.crear_evaluacion(cod, titulo, pond)
        print("Evaluación creada (sin ID)")
    except Exception as e:
        print("Error:", e)
# parte de pablo

def accion_registrar_nota(sistema: Plataforma):
    if not sistema.cursos:
        print("Primero crea cursos"); return
    cursos = list(sistema.cursos.items())
    print("\n-- CURSOS --")
    for i, (cod, info) in enumerate(cursos, 1):
        print(f"{i}) {cod} | {info['nombre']}")
    try:
        pos_c = int(input("Número de curso: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos_c < 0 or pos_c >= len(cursos):
        print("Selección inválida"); return
    cod = cursos[pos_c][0]

    evals = sistema.cursos[cod]["evaluaciones"]
    if not evals:
        print("No hay evaluaciones"); return
    print("\n-- EVALUACIONES --")
    for i, ev in enumerate(evals, 1):
        print(f"{i}) {ev['titulo']} | {ev['ponderacion']}")
    try:
        pos_ev = int(input("Número de evaluación: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos_ev < 0 or pos_ev >= len(evals):
        print("Selección inválida"); return

    inscritos = sistema.cursos[cod]["inscritos"]
    if not inscritos:
        print("No hay inscritos"); return
    print("\n-- INSCRITOS --")
    for i, uid in enumerate(inscritos, 1):
        print(f"{i}) {sistema.usuarios[uid].nombre} ({uid})")
    try:
        pos_s = int(input("Número de estudiante: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos_s < 0 or pos_s >= len(inscritos):
        print("Selección inválida"); return

    uid_est = inscritos[pos_s]
    nota = input("Nota (0..100): ").strip()
    try:
        sistema.registrar_nota(cod, pos_ev, uid_est, nota)
        print("Nota registrada")
    except Exception as e:
        print("Error:", e)

def accion_listar_cursos(sistema: Plataforma):
    if not sistema.cursos:
        print("Sin cursos"); return
    for cod, info in sistema.cursos.items():
        print(f"{cod} | {info['nombre']} | inst={info['instructor']}")

def accion_ver_inscritos(sistema: Plataforma):
    if not sistema.cursos:
        print("Sin cursos"); return
    for cod, info in sistema.cursos.items():
        print(f"\nCurso {cod}:")
        if not info["inscritos"]:
            print("- Sin inscritos")
        else:
            for uid in info["inscritos"]:
                print(f"- {uid} | {sistema.usuarios[uid].nombre}")

def accion_ver_evaluaciones(sistema: Plataforma):
    if not sistema.cursos:
        print("Sin cursos"); return
    for cod, info in sistema.cursos.items():
        print(f"\nCurso {cod}:")
        if not info["evaluaciones"]:
            print("- Sin evaluaciones")
        else:
            for i, ev in enumerate(info["evaluaciones"], 1):
                print(f"{i}) {ev['titulo']} | {ev['ponderacion']}")

def accion_ver_calificaciones(sistema: Plataforma):
    if not sistema.cursos:
        print("Sin cursos"); return
    for cod, info in sistema.cursos.items():
        print(f"\nCurso {cod}:")
        if not info["evaluaciones"]:
            print("- Sin evaluaciones"); continue
        for i, ev in enumerate(info["evaluaciones"], 1):
            print(f"Evaluación {i}:")
            if not ev["calificaciones"]:
                print("  Sin calificaciones")
            else:
                for uid, n in ev["calificaciones"].items():
                    print(f"  {uid} {sistema.usuarios[uid].nombre}: {n}")


class PlataformaP(Plataforma):
    pass

# menú (solo invoca funciones ya definidas)
def menu():
    sistema = Plataforma()
    acciones = {
        "1": lambda: accion_registrar_instructor(sistema),
        "2": lambda: accion_registrar_estudiante(sistema),
        "3": lambda: accion_crear_curso(sistema),
        "4": lambda: accion_inscribir_estudiante(sistema),
        "5": lambda: accion_crear_evaluacion(sistema),
        "6": lambda: accion_registrar_nota(sistema),
        "7": lambda: accion_listar_cursos(sistema),
        "8": lambda: accion_ver_inscritos(sistema),
        "9": lambda: accion_ver_evaluaciones(sistema),
        "10": lambda: accion_ver_calificaciones(sistema),
    }
    while True:
        print("\n=== MENU ===")
        print("1) Registrar instructor")
        print("2) Registrar estudiante")
        print("3) Crear curso")
        print("4) Inscribir estudiante")
        print("5) Crear evaluación (sin ID)")
        print("6) Registrar nota")
        print("7) Listar cursos")
        print("8) Ver inscritos")
        print("9) Ver evaluaciones")
        print("10) Ver calificaciones")
        print("11) Salir")
        op = input("Opción:\n").strip()
        if op == "11":
            break
        accion = acciones.get(op)
        if accion: 
            accion()
        else:
            print("Opción inválida")

menu()

# parte de pablo

def accion_registrar_nota(sistema: Plataforma):
    if not sistema.cursos:
        print("Primero crea cursos"); return
    cursos = list(sistema.cursos.items())
    print("\n-- CURSOS --")
    for i, (cod, info) in enumerate(cursos, 1):
        print(f"{i}) {cod} | {info['nombre']}")
    try:
        pos_c = int(input("Número de curso: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos_c < 0 or pos_c >= len(cursos):
        print("Selección inválida"); return
    cod = cursos[pos_c][0]

    evals = sistema.cursos[cod]["evaluaciones"]
    if not evals:
        print("No hay evaluaciones"); return
    print("\n-- EVALUACIONES --")
    for i, ev in enumerate(evals, 1):
        print(f"{i}) {ev['titulo']} | {ev['ponderacion']}")
    try:
        pos_ev = int(input("Número de evaluación: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos_ev < 0 or pos_ev >= len(evals):
        print("Selección inválida"); return

    inscritos = sistema.cursos[cod]["inscritos"]
    if not inscritos:
        print("No hay inscritos"); return
    print("\n-- INSCRITOS --")
    for i, uid in enumerate(inscritos, 1):
        print(f"{i}) {sistema.usuarios[uid].nombre} ({uid})")
    try:
        pos_s = int(input("Número de estudiante: ").strip()) - 1
    except:
        print("Selección inválida"); return
    if pos_s < 0 or pos_s >= len(inscritos):
        print("Selección inválida"); return

    uid_est = inscritos[pos_s]
    nota = input("Nota (0..100): ").strip()
    try:
        sistema.registrar_nota(cod, pos_ev, uid_est, nota)
        print("Nota registrada")
    except Exception as e:
        print("Error:", e)

def accion_listar_cursos(sistema: Plataforma):
    if not sistema.cursos:
        print("Sin cursos"); return
    for cod, info in sistema.cursos.items():
        print(f"{cod} | {info['nombre']} | inst={info['instructor']}")

def accion_ver_inscritos(sistema: Plataforma):
    if not sistema.cursos:
        print("Sin cursos"); return
    for cod, info in sistema.cursos.items():
        print(f"\nCurso {cod}:")
        if not info["inscritos"]:
            print("- Sin inscritos")
        else:
            for uid in info["inscritos"]:
                print(f"- {uid} | {sistema.usuarios[uid].nombre}")

def accion_ver_evaluaciones(sistema: Plataforma):
    if not sistema.cursos:
        print("Sin cursos"); return
    for cod, info in sistema.cursos.items():
        print(f"\nCurso {cod}:")
        if not info["evaluaciones"]:
            print("- Sin evaluaciones")
        else:
            for i, ev in enumerate(info["evaluaciones"], 1):
                print(f"{i}) {ev['titulo']} | {ev['ponderacion']}")

def accion_ver_calificaciones(sistema: Plataforma):
    if not sistema.cursos:
        print("Sin cursos"); return
    for cod, info in sistema.cursos.items():
        print(f"\nCurso {cod}:")
        if not info["evaluaciones"]:
            print("- Sin evaluaciones"); continue
        for i, ev in enumerate(info["evaluaciones"], 1):
            print(f"Evaluación {i}:")
            if not ev["calificaciones"]:
                print("  Sin calificaciones")
            else:
                for uid, n in ev["calificaciones"].items():
                    print(f"  {uid} {sistema.usuarios[uid].nombre}: {n}")


class PlataformaP(Plataforma):
    pass

# menú (solo invoca funciones ya definidas)
def menu():
    sistema = Plataforma()
    acciones = {
        "1": lambda: accion_registrar_instructor(sistema),
        "2": lambda: accion_registrar_estudiante(sistema),
        "3": lambda: accion_crear_curso(sistema),
        "4": lambda: accion_inscribir_estudiante(sistema),
        "5": lambda: accion_crear_evaluacion(sistema),
        "6": lambda: accion_registrar_nota(sistema),
        "7": lambda: accion_listar_cursos(sistema),
        "8": lambda: accion_ver_inscritos(sistema),
        "9": lambda: accion_ver_evaluaciones(sistema),
        "10": lambda: accion_ver_calificaciones(sistema),
    }
    while True:
        print("\n=== MENU ===")
        print("1) Registrar instructor")
        print("2) Registrar estudiante")
        print("3) Crear curso")
        print("4) Inscribir estudiante")
        print("5) Crear evaluación (sin ID)")
        print("6) Registrar nota")
        print("7) Listar cursos")
        print("8) Ver inscritos")
        print("9) Ver evaluaciones")
        print("10) Ver calificaciones")
        print("11) Salir")
        op = input("Opción:\n").strip()
        if op == "11":
            break
        accion = acciones.get(op)
        if accion: 
            accion()
        else:
            print("Opción inválida")

menu()