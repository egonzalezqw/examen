import streamlit as st
import time
import firebase_admin
from firebase_admin import credentials, firestore

# -----------------------------
# CONFIG FIREBASE
# -----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # tu JSON
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -----------------------------
# SESSION STATE
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "score" not in st.session_state:
    st.session_state.score = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "answered" not in st.session_state:
    st.session_state.answered = {}

# -----------------------------
# LOGIN UI
# -----------------------------
def login():
    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Ingresar"):
        # 🔴 NOTA: Firebase Admin no valida password directamente
        # Simulación básica (puedes integrar Firebase Auth REST API)
        user_ref = db.collection("users").document(email).get()

        if user_ref.exists:
            st.session_state.user = email
            st.success("Login exitoso")
        else:
            st.error("Usuario no existe")

def register():
    st.subheader("📝 Registro")

    email = st.text_input("Nuevo Email")
    password = st.text_input("Nueva Password", type="password")

    if st.button("Crear cuenta"):
        db.collection("users").document(email).set({
            "email": email
        })
        st.success("Usuario creado")

# -----------------------------
# TERMINAL UI
# -----------------------------
def terminal_input(qid, prompt):
    st.markdown(f"""
    <div style="background:black;color:#00ff00;padding:10px;font-family:monospace">
    user@linux:~$ {prompt}
    </div>
    """, unsafe_allow_html=True)

    return st.text_input("Comando:", key=qid)

# -----------------------------
# EXAMEN
# -----------------------------
def exam():
    st.title("🧪 Linux Exam")

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    elapsed = int(time.time() - st.session_state.start_time)
    st.write(f"⏱️ Tiempo: {elapsed}s")

    # Pregunta
    cmd = terminal_input("q1", "Mostrar directorio actual")

    if st.button("Validar"):
        if cmd.strip() == "pwd":
            st.success("Correcto")
            if "q1" not in st.session_state.answered:
                st.session_state.score += 1
                st.session_state.answered["q1"] = True
        else:
            st.error("Incorrecto")

    st.subheader(f"Puntaje: {st.session_state.score}")

    # Finalizar examen
    if st.button("Finalizar examen"):
        total_time = int(time.time() - st.session_state.start_time)

        db.collection("results").add({
            "user": st.session_state.user,
            "score": st.session_state.score,
            "time": total_time,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        st.success("Resultado guardado ✅")

# -----------------------------
# DASHBOARD RESULTADOS
# -----------------------------
def dashboard():
    st.title("📊 Resultados")

    results = db.collection("results").stream()

    data = []
    for r in results:
        data.append(r.to_dict())

    st.dataframe(data)

# -----------------------------
# MAIN
# -----------------------------
menu = st.sidebar.selectbox("Menú", ["Login", "Registro", "Examen", "Resultados"])

if menu == "Login":
    login()

elif menu == "Registro":
    register()

elif menu == "Examen":
    if st.session_state.user:
        exam()
    else:
        st.warning("Debes iniciar sesión")

elif menu == "Resultados":
    dashboard()
