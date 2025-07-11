{\rtf1\ansi\ansicpg1250\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 HelveticaNeue;}
{\colortbl;\red255\green255\blue255;\red234\green234\blue236;}
{\*\expandedcolortbl;;\cssrgb\c93333\c93333\c94118;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs32 \cf2 \expnd0\expndtw0\kerning0
Cze\uc0\u347 \u263 ! Jasne, przygotowanie takiej wizualizacji w Pythonie z u\u380 yciem biblioteki `streamlit` jest jak najbardziej wykonalne. Streamlit pozwala tworzy\u263  interaktywne aplikacje webowe bezpo\u347 rednio z kodu Pythona, a nast\u281 pnie \u322 atwo je udost\u281 pnia\u263 .\
\
Oto propozycja kodu symulacji, kt\'f3ra realizuje opisane przez Ciebie funkcje. Wyja\uc0\u347 ni\u281  krok po kroku, jak dzia\u322 a i jak go uruchomi\u263 .\
\
**Koncepcja symulacji:**\
\
1.  **Stan:** B\uc0\u281 dziemy \u347 ledzi\u263  poziom i temperatur\u281  w ka\u380 dym zbiorniku, stan pomp (procentowo) i stan odbiornik\'f3w (w\u322 \u261 czony/wy\u322 \u261 czony).\
2.  **Kroki symulacji:** Aplikacja b\uc0\u281 dzie dzia\u322 a\u263  w p\u281 tli. W ka\u380 dym kroku czasowym (`DT`, np. 1 sekunda):\
    *   Odczyta aktualne ustawienia u\uc0\u380 ytkownika (po\u322 o\u380 enie suwak\'f3w, stan przycisk\'f3w odbiornik\'f3w).\
    *   Obliczy przep\uc0\u322 ywy pomp na podstawie ich procentowej wydajno\u347 ci.\
    *   Obliczy, ile p\uc0\u322 ynu faktycznie mo\u380 e przep\u322 yn\u261 \u263 , uwzgl\u281 dniaj\u261 c aktualny poziom w zbiorniku \u378 r\'f3d\u322 owym.\
    *   Obliczy zmian\uc0\u281  temperatury glikolu w odbiornikach (je\u347 li s\u261  w\u322 \u261 czone).\
    *   Zaktualizuje poziomy w zbiornikach na podstawie przep\uc0\u322 yw\'f3w netto (uwzgl\u281 dniaj\u261 c pompy i przep\u322 yw z ch\u322 odziarki).\
    *   Obs\uc0\u322 u\u380 y przepe\u322 nienie zbiornik\'f3w zgodnie z zasad\u261  naczy\u324  po\u322 \u261 czonych (nadmiar z jednego przelewa si\u281  do drugiego, je\u347 li oba s\u261  na maksimum).\
    *   Zaktualizuje temperatury w zbiornikach na podstawie bilansu cieplnego (ilo\uc0\u347 \u263  ciep\u322 a dodana przez odbiorniki, odebrana przez ch\u322 odziark\u281 ).\
    *   Zapisze aktualny stan do historii, aby mo\uc0\u380 na by\u322 o go p\'f3\u378 niej zwizualizowa\u263  na wykresach.\
3.  **Interfejs:** U\uc0\u380 yjemy suwak\'f3w (`st.slider`) do regulacji pomp, przycisk\'f3w (`st.toggle`) do w\u322 \u261 czania/wy\u322 \u261 czania odbiornik\'f3w i przycisk\'f3w do sterowania sam\u261  symulacj\u261  (Start/Pauza, Reset). Wyniki (poziomy, temperatury) poka\u380 emy za pomoc\u261  `st.metric`, a histori\u281  zmian na wykresach `st.line_chart`.\
\
**Kod aplikacji (zapisz jako plik `symulator_systemu.py`):**\
\
```python\
import streamlit as st\
import pandas as pd\
import time\
\
# --- Sta\uc0\u322 e parametr\'f3w systemu ---\
TANK_CAPACITY_L = 5000.0      # Pojemno\uc0\u347 \u263  ca\u322 kowita jednego zbiornika w litrach\
INITIAL_LEVEL_L = 3000.0      # Pocz\uc0\u261 tkowy poziom nape\u322 nienia w litrach\
MAX_FLOW_L_PER_MIN = 10000.0  # Maksymalny przep\uc0\u322 yw pompy w litrach/minut\u281 \
MAX_FLOW_L_PER_SEC = MAX_FLOW_L_PER_MIN / 60.0 # Maksymalny przep\uc0\u322 yw w litrach/sekund\u281 \
COOLER_TEMP_C = -5.0          # Temperatura wyj\uc0\u347 ciowa ch\u322 odziarki (\'b0C)\
RECEIVER_HEAT_RATE_PER_SEC = 1.0 # Przyrost temperatury na sekund\uc0\u281  na odbiornik (\'b0C/s)\
DT = 1.0                      # Krok czasowy symulacji w sekundach (1 sekunda)\
\
# --- Funkcje pomocnicze ---\
\
def calculate_heat_return_temp(cold_temp, num_receivers_on):\
    """Oblicza temperatur\uc0\u281  glikolu powracaj\u261 cego z odbiornik\'f3w."""\
    # Prosty model: temp. powrotu = temp. zimnego + przyrost z odbiornik\'f3w\
    # Mo\uc0\u380 na doda\u263  bardziej z\u322 o\u380 one zale\u380 no\u347 ci, np. ograniczenie temperatury.\
    temp = cold_temp + num_receivers_on * RECEIVER_HEAT_RATE_PER_SEC\
    return temp\
\
def run_simulation_step(state):\
    """Przeprowadza jeden krok symulacji."""\
\
    # --- Odczyt aktualnego stanu ---\
    pump1_pct = state['pump1_pct']\
    pump2_pct = state['pump2_pct']\
    receivers_on = state['receivers_on']\
    cold_level = state['cold_level']\
    warm_level = state['warm_level']\
    cold_temp = state['cold_temp']\
    warm_temp = state['warm_temp']\
    sim_time = state['sim_time']\
    total_level = cold_level + warm_level # Ca\uc0\u322 kowita ilo\u347 \u263  glikolu w systemie\
\
    # --- 1. Obliczenie przep\uc0\u322 yw\'f3w ---\
    flow1_lps = (pump1_pct / 100.0) * MAX_FLOW_L_PER_SEC\
    flow2_lps = (pump2_pct / 100.0) * MAX_FLOW_L_PER_SEC\
\
    # --- 2. Okre\uc0\u347 lenie obj\u281 to\u347 ci pompowanych w kroku DT ---\
    # Pompa 1 (z zimnego zbiornika)\
    pump1_vol_dt = min(flow1_lps * DT, cold_level) # Nie mo\uc0\u380 na wypompowa\u263  wi\u281 cej ni\u380  jest w zbiorniku\
    # Pompa 2 (z ciep\uc0\u322 ego zbiornika)\
    pump2_vol_dt = min(flow2_lps * DT, warm_level) # Nie mo\uc0\u380 na wypompowa\u263  wi\u281 cej ni\u380  jest w zbiorniku\
\
    # --- 3. Obliczenie wp\uc0\u322 ywu odbiornik\'f3w na temperatur\u281  ---\
    num_receivers_on = sum(receivers_on)\
    T_return = calculate_heat_return_temp(cold_temp, num_receivers_on)\
\
    # --- 4. Obliczenie tymczasowych poziom\'f3w (bez uwzgl\uc0\u281 dnienia przepe\u322 nienia) ---\
    # Glikol z pompy 1 (po odbiornikach) trafia do zbiornika ciep\uc0\u322 ego.\
    # Glikol z pompy 2 (po ch\uc0\u322 odziarce) trafia do zbiornika zimnego.\
    # Za\uc0\u322 o\u380 enie: Ca\u322 y przepompowany wolumen dociera do nast\u281 pnego etapu.\
    intermediate_cold = cold_level - pump1_vol_dt + pump2_vol_dt\
    intermediate_warm = warm_level + pump1_vol_dt - pump2_vol_dt\
\
    # --- 5. Obs\uc0\u322 uga limit\'f3w pojemno\u347 ci i przelew\'f3w ---\
    # Logika przelewu "na samej g\'f3rze" oznacza, \uc0\u380 e je\u347 li jeden zbiornik jest pe\u322 ny,\
    # a p\uc0\u322 ynie do niego wi\u281 cej, to nadmiar przelewa si\u281  do drugiego (je\u347 li ten te\u380  nie jest pe\u322 ny).\
    # Lub, je\uc0\u347 li oba s\u261  pe\u322 ne, nadmiar jest tracony w tej symulacji (lub mo\u380 na doda\u263  logik\u281  cofania).\
    # Uproszczenie: je\uc0\u347 li suma jest OK, rozdzielamy zgodnie z logik\u261 , ale trzymaj\u261 c w granicach 0 i MAX_CAPACITY.\
\
    new_cold_level = cold_level\
    new_warm_level = warm_level\
\
    # Spill from Cold to Warm if Cold exceeds capacity\
    if intermediate_cold > TANK_CAPACITY_L:\
        spill_cold_to_warm = intermediate_cold - TANK_CAPACITY_L\
        new_cold_level = TANK_CAPACITY_L\
        # Add spill to warm, but don't exceed its capacity immediately\
        new_warm_level = min(TANK_CAPACITY_L, intermediate_warm + spill_cold_to_warm)\
    # Spill from Warm to Cold if Warm exceeds capacity (after potential spill from cold)\
    elif intermediate_warm > TANK_CAPACITY_L:\
         spill_warm_to_cold = intermediate_warm - TANK_CAPACITY_L\
         new_warm_level = TANK_CAPACITY_L\
         # Add spill to cold, but don't exceed its capacity\
         new_cold_level = min(TANK_CAPACITY_L, intermediate_cold + spill_warm_to_cold)\
    # If no spill occurred yet, just apply intermediate values, respecting capacity limits\
    else:\
        new_cold_level = max(0.0, min(TANK_CAPACITY_L, intermediate_cold))\
        new_warm_level = max(0.0, min(TANK_CAPACITY_L, intermediate_warm))\
\
    # Ensure total volume conservation isn't grossly violated by spill logic clamping\
    # Re-normalize slightly if needed? For now, clamping is primary.\
    # A better overflow logic might check total fluid and distribute based on available space.\
\
    # --- 6. Aktualizacja temperatur (prosty bilans cieplny) ---\
    # Ciep\uc0\u322 o dodawane/odejmowane w jednostkach L*\'b0C w czasie DT\
\
    # Bilans dla zbiornika ciep\uc0\u322 ego:\
    # Wp\uc0\u322 ywa: pump1_vol_dt przy temperaturze T_return\
    # Wyp\uc0\u322 ywa: pump2_vol_dt przy temperaturze warm_temp\
    delta_warm_heat_content = (pump1_vol_dt * T_return) - (pump2_vol_dt * warm_temp)\
\
    # Bilans dla zbiornika zimnego:\
    # Wp\uc0\u322 ywa: pump2_vol_dt przy temperaturze COOLER_TEMP_C\
    # Wyp\uc0\u322 ywa: pump1_vol_dt przy temperaturze cold_temp\
    delta_cold_heat_content = (pump2_vol_dt * COOLER_TEMP_C) - (pump1_vol_dt * cold_temp)\
\
    # Obliczenie zmiany temperatury na podstawie zmian zawarto\uc0\u347 ci ciep\u322 a i aktualnego poziomu\
    # Unikamy dzielenia przez zero, je\uc0\u347 li poziom jest bliski zeru\
    epsilon = 1e-6\
    new_warm_temp = warm_temp\
    if new_warm_level > epsilon:\
        warm_temp_change = delta_warm_heat_content / new_warm_level\
        new_warm_temp = warm_temp + warm_temp_change\
        # Opcjonalnie: ograniczenie temperatury, np. do -5C je\uc0\u347 li co\u347  posz\u322 o nie tak\
        # new_warm_temp = max(COOLER_TEMP_C, new_warm_temp)\
\
    new_cold_temp = cold_temp\
    if new_cold_level > epsilon:\
        cold_temp_change = delta_cold_heat_content / new_cold_level\
        new_cold_temp = cold_temp + cold_temp_change\
        # Ograniczenie do temperatury ch\uc0\u322 odziarki\
        new_cold_temp = max(COOLER_TEMP_C, new_cold_temp)\
    else:\
         # Je\uc0\u347 li zbiornik zimny jest pusty, jego temperatura powinna d\u261 \u380 y\u263  do temp. ch\u322 odziarki\
         new_cold_temp = COOLER_TEMP_C\
\
\
    # --- 7. Zapisanie stanu do historii ---\
    new_state = \{\
        'sim_time': sim_time + DT,\
        'pump1_pct': pump1_pct,\
        'pump2_pct': pump2_pct,\
        'receivers_on': list(receivers_on), # Kopiowanie listy\
        'cold_level': new_cold_level,\
        'warm_level': new_warm_level,\
        'cold_temp': new_cold_temp,\
        'warm_temp': new_warm_temp,\
    \}\
    state['history'].append(new_state)\
\
    # Aktualizacja stanu g\uc0\u322 \'f3wnego dla nast\u281 pnego kroku\
    state.update(new_state)\
    return state\
\
# --- Interfejs U\uc0\u380 ytkownika Streamlit ---\
\
st.set_page_config(layout="wide")\
st.title("\uc0\u55357 \u56522  Symulator Systemu Ch\u322 odniczego")\
st.caption("Wizualizacja dzia\uc0\u322 ania obiegu glikolu w zale\u380 no\u347 ci od pracy pomp i odbiornik\'f3w.")\
\
# --- Inicjalizacja stanu aplikacji w sesji ---\
if 'sim_state' not in st.session_state:\
    st.session_state.sim_state = \{\
        'sim_time': 0.0,\
        'pump1_pct': 0.0,       # % wydajno\uc0\u347 ci pompy 1\
        'pump2_pct': 0.0,       # % wydajno\uc0\u347 ci pompy 2\
        'receivers_on': [False] * 5, # Stan odbiornik\'f3w [False, False, ...]\
        'cold_level': INITIAL_LEVEL_L,\
        'warm_level': INITIAL_LEVEL_L,\
        'cold_temp': 5.0,       # Pocz\uc0\u261 tkowa temperatura w zimnym zbiorniku (\'b0C)\
        'warm_temp': 25.0,      # Pocz\uc0\u261 tkowa temperatura w ciep\u322 ym zbiorniku (\'b0C)\
        'history': [],          # Lista zapisanych stan\'f3w do wykres\'f3w\
        'is_running': False,    # Czy symulacja jest aktywna\
        'simulation_speed': 0.5 # Op\'f3\uc0\u378 nienie mi\u281 dzy krokami dla wizualizacji (w sekundach)\
    \}\
\
# --- Panele Kontrolne w Sidebar ---\
st.sidebar.header("\uc0\u9881 \u65039  Kontrolki Symulacji")\
\
# Suwaki pomp\
pump1_slider = st.sidebar.slider(\
    "\uc0\u55357 \u56960  Pompa 1 (Zimny -> Odbiorniki) [%]",\
    0.0, 100.0, float(st.session_state.sim_state['pump1_pct']), 0.1,\
    help="Reguluje przep\uc0\u322 yw glikolu z zimnego zbiornika do odbiornik\'f3w."\
)\
pump2_slider = st.sidebar.slider(\
    "\uc0\u10052 \u65039  Pompa 2 (Ciep\u322 y -> Ch\u322 odziarka) [%]",\
    0.0, 100.0, float(st.session_state.sim_state['pump2_pct']), 0.1,\
    help="Reguluje przep\uc0\u322 yw glikolu z ciep\u322 ego zbiornika do ch\u322 odziarki."\
)\
\
# Przyciski odbiornik\'f3w\
st.sidebar.subheader("\uc0\u55357 \u56588  Odbiorniki")\
receiver_cols = st.sidebar.columns(3) # Uk\uc0\u322 ad przycisk\'f3w w 3 kolumnach\
current_receivers_state = list(st.session_state.sim_state['receivers_on']) # Kopiowanie stanu\
updated_receivers = False\
for i in range(5):\
    col = receiver_cols[i % 3]\
    # U\uc0\u380 ywamy unikalnego klucza dla ka\u380 dego przycisku toggle\
    is_receiver_on = col.toggle(f"Odbiornik \{i+1\}", value=current_receivers_state[i], key=f"receiver_toggle_\{i\}")\
    if is_receiver_on != current_receivers_state[i]:\
        current_receivers_state[i] = is_receiver_on\
        updated_receivers = True\
\
# Je\uc0\u347 li stan odbiornik\'f3w si\u281  zmieni\u322 , zapisz go w sesji\
if updated_receivers:\
    st.session_state.sim_state['receivers_on'] = current_receivers_state\
\
# Pr\uc0\u281 dko\u347 \u263  symulacji\
sim_speed = st.sidebar.slider(\
    "\uc0\u55357 \u56354  Pr\u281 dko\u347 \u263  Symulacji (op\'f3\u378 nienie krokowe)",\
    0.05, 2.0, st.session_state.sim_state['simulation_speed'], 0.05,\
    help="Im mniejsze op\'f3\uc0\u378 nienie, tym szybsza wizualizacja (ale mo\u380 e obci\u261 \u380 a\u263  przegl\u261 dark\u281 )."\
)\
st.session_state.sim_state['simulation_speed'] = sim_speed\
\
# Przyciski sterowania symulacj\uc0\u261 \
col1, col2, col3 = st.sidebar.columns(3)\
run_pause_button = col1.button("\uc0\u9654 \u65039  Uruchom / Pauza", key="run_pause")\
reset_button = col2.button("\uc0\u55357 \u56580  Reset", key="reset")\
\
# Obs\uc0\u322 uga przycisk\'f3w sterowania\
if reset_button:\
    st.session_state.sim_state = \{ # Reset do stanu pocz\uc0\u261 tkowego\
        'sim_time': 0.0,\
        'pump1_pct': 0.0,\
        'pump2_pct': 0.0,\
        'receivers_on': [False] * 5,\
        'cold_level': INITIAL_LEVEL_L,\
        'warm_level': INITIAL_LEVEL_L,\
        'cold_temp': 5.0,\
        'warm_temp': 25.0,\
        'history': [],\
        'is_running': False,\
        'simulation_speed': sim_speed # Zachowaj wybran\uc0\u261  pr\u281 dko\u347 \u263 \
    \}\
    st.rerun() # Ponowne uruchomienie aplikacji, aby od\uc0\u347 wie\u380 y\u263  UI\
\
if run_pause_button:\
    st.session_state.sim_state['is_running'] = not st.session_state.sim_state['is_running']\
    if not st.session_state.sim_state['is_running']: # Je\uc0\u347 li pauzujemy, zapisz aktualne ustawienia\
         st.session_state.sim_state['pump1_pct'] = pump1_slider\
         st.session_state.sim_state['pump2_pct'] = pump2_slider\
         # receiver state is handled directly by toggles\
\
# Aktualizacja ustawie\uc0\u324  pomp je\u347 li nie s\u261  w trakcie dzia\u322 ania symulacji\
if not st.session_state.sim_state['is_running']:\
    st.session_state.sim_state['pump1_pct'] = pump1_slider\
    st.session_state.sim_state['pump2_pct'] = pump2_slider\
\
# --- G\uc0\u322 \'f3wny obszar aplikacji ---\
st.header("\uc0\u55357 \u56520  Aktualny Stan Systemu")\
\
# Wy\uc0\u347 wietlanie metryk\
col_a, col_b, col_c = st.columns(3)\
col_a.metric("Zbiornik Zimny", f"\{st.session_state.sim_state['cold_level']:.1f\} L", f"\{st.session_state.sim_state['cold_temp']:.1f\} \'b0C")\
col_b.metric("Zbiornik Ciep\uc0\u322 y", f"\{st.session_state.sim_state['warm_level']:.1f\} L", f"\{st.session_state.sim_state['warm_temp']:.1f\} \'b0C")\
col_c.metric("Czas Symulacji", f"\{st.session_state.sim_state['sim_time']:.0f\} s", f"\{sum(st.session_state.sim_state['receivers_on'])\} Odbiornik\'f3w ON")\
\
# Wizualizacja poziom\'f3w w zbiornikach (prosta)\
level_cols = st.columns(2)\
# Symulacja wype\uc0\u322 nienia zbiornika jako pasek\
cold_fill_percent = (st.session_state.sim_state['cold_level'] / TANK_CAPACITY_L) * 100\
warm_fill_percent = (st.session_state.sim_state['warm_level'] / TANK_CAPACITY_L) * 100\
level_cols[0].markdown(f"**Poziom Zimny:** `\{st.session_state.sim_state['cold_level']:.1f\}` L")\
level_cols[0].progress(int(cold_fill_percent), text=f"\{cold_fill_percent:.0f\}%")\
level_cols[1].markdown(f"**Poziom Ciep\uc0\u322 y:** `\{st.session_state.sim_state['warm_level']:.1f\}` L")\
level_cols[1].progress(int(warm_fill_percent), text=f"\{warm_fill_percent:.0f\}%")\
\
# --- P\uc0\u281 tla symulacji ---\
if st.session_state.sim_state['is_running']:\
    # Uruchom jeden krok symulacji\
    st.session_state.sim_state = run_simulation_step(st.session_state.sim_state)\
\
    # Wy\uc0\u347 wietl komunikat o dzia\u322 aniu symulacji\
    st.success(f"Symulacja dzia\uc0\u322 a... Czas: \{st.session_state.sim_state['sim_time']:.0f\} s")\
\
    # Kr\'f3tkie op\'f3\uc0\u378 nienie dla wizualnej p\u322 ynno\u347 ci\
    time.sleep(st.session_state.sim_state['simulation_speed'])\
\
    # Wymuszenie ponownego przetworzenia skryptu Streamlit, aby kontynuowa\uc0\u263  p\u281 tl\u281 \
    st.rerun()\
else:\
     # Poka\uc0\u380  komunikat pauzy je\u347 li przycisk zosta\u322  naci\u347 ni\u281 ty\
     if run_pause_button and not st.session_state.sim_state['is_running']:\
          st.warning("Symulacja wstrzymana.")\
\
# --- Wykresy historii ---\
if st.session_state.sim_state['history']:\
    st.header("\uc0\u55357 \u56520  Historia Zmian")\
    history_df = pd.DataFrame(st.session_state.sim_state['history'])\
    history_df.set_index('sim_time', inplace=True)\
\
    st.subheader("Poziomy w Zbiornikach (L)")\
    # Wykres poziom\'f3w\
    st.line_chart(history_df[['cold_level', 'warm_level']])\
\
    st.subheader("Temperatury (\'b0C)")\
    # Wykres temperatur\
    st.line_chart(history_df[['cold_temp', 'warm_temp']])\
else:\
    st.info("Uruchom symulacj\uc0\u281 , aby zobaczy\u263  histori\u281  zmian parametr\'f3w.")\
\
# --- Instrukcje dotycz\uc0\u261 ce udost\u281 pniania ---\
st.sidebar.markdown("---")\
st.sidebar.markdown("### \uc0\u55357 \u56960  Udost\u281 pnianie Aplikacji")\
st.sidebar.markdown("""\
1.  **Zapisz kod:** Zapisz powy\uc0\u380 szy kod jako plik `.py`, np. `symulator_systemu.py`.\
2.  **Zainstaluj biblioteki:** W terminalu, w folderze z plikiem, wykonaj:\
    ```bash\
    pip install streamlit pandas\
    ```\
3.  **Uruchom lokalnie:** W terminalu wpisz:\
    ```bash\
    streamlit run symulator_systemu.py\
    ```\
    Aplikacja otworzy si\uc0\u281  w Twojej przegl\u261 darce.\
4.  **Udost\uc0\u281 pnij:** W aplikacji Streamlit (w prawym g\'f3rnym rogu) kliknij `Share your app` i wybierz opcj\u281  udost\u281 pniania (np. publicznie lub prywatnie przez konto Streamlit Cloud).\
""")\
```\
\
**Jak uruchomi\uc0\u263  i u\u380 ywa\u263 :**\
\
1.  **Zapisz kod:** Skopiuj ca\uc0\u322 y powy\u380 szy kod i zapisz go w pliku tekstowym o nazwie `symulator_systemu.py`.\
2.  **Zainstaluj Streamlit i Pandas:** Je\uc0\u347 li nie masz tych bibliotek, otw\'f3rz terminal (lub wiersz polece\u324 ) i wpisz:\
    ```bash\
    pip install streamlit pandas\
    ```\
3.  **Uruchom aplikacj\uc0\u281 :** W terminalu przejd\u378  do folderu, w kt\'f3rym zapisa\u322 e\u347  plik `symulator_systemu.py` i wpisz polecenie:\
    ```bash\
    streamlit run symulator_systemu.py\
    ```\
4.  **Interakcja:**\
    *   Aplikacja otworzy si\uc0\u281  automatycznie w nowej karcie przegl\u261 darki.\
    *   Po lewej stronie (w panelu bocznym) znajdziesz suwaki do regulacji pracy pomp (0-100%) oraz przyciski do w\uc0\u322 \u261 czania/wy\u322 \u261 czania poszczeg\'f3lnych 5 odbiornik\'f3w.\
    *   U\uc0\u380 yj przycisku "\u9654 \u65039  Uruchom / Pauza", aby rozpocz\u261 \u263  lub zatrzyma\u263  symulacj\u281 .\
    *   U\uc0\u380 yj przycisku "\u55357 \u56580  Reset", aby przywr\'f3ci\u263  pocz\u261 tkowe warto\u347 ci.\
    *   Mo\uc0\u380 esz dostosowa\u263  pr\u281 dko\u347 \u263  animacji za pomoc\u261  suwaka "Pr\u281 dko\u347 \u263  Symulacji".\
    *   Obserwuj aktualne warto\uc0\u347 ci poziomu i temperatury w zbiornikach oraz historyczne zmiany na wykresach poni\u380 ej.\
\
**Jak udost\uc0\u281 pni\u263  szefowi:**\
\
1.  **Uruchomienie lokalne:** Upewnij si\uc0\u281 , \u380 e aplikacja dzia\u322 a poprawnie na Twoim komputerze.\
2.  **Streamlit Cloud:** Najprostszym sposobem jest skorzystanie z darmowej platformy Streamlit Cloud.\
    *   Musisz mie\uc0\u263  konto na [GitHub](https://github.com/) lub [GitLab](https://gitlab.com/).\
    *   Umie\uc0\u347 \u263  plik `symulator_systemu.py` w repozytorium Git.\
    *   Zaloguj si\uc0\u281  do [Streamlit Cloud](https://streamlit.io/cloud) u\u380 ywaj\u261 c swojego konta GitHub/GitLab.\
    *   Kliknij "New App", wybierz swoje repozytorium i plik `symulator_systemu.py`.\
    *   Streamlit Cloud zbuduje i uruchomi aplikacj\uc0\u281 , generuj\u261 c dla niej publiczny link, kt\'f3ry mo\u380 esz poda\u263  szefowi.\
3.  **Inne metody:** Mo\uc0\u380 esz te\u380  wdro\u380 y\u263  aplikacj\u281  na w\u322 asnym serwerze lub u\u380 y\u263  innych platform hostingowych dla aplikacji Python (np. Heroku, PythonAnywhere), ale Streamlit Cloud jest zazwyczaj najszybszy dla tego typu narz\u281 dzi.\
\
Ten kod symuluje podstawowe zachowanie systemu. Mo\uc0\u380 na go dalej rozwija\u263 , dodaj\u261 c np. bardziej szczeg\'f3\u322 owe modele wymiany ciep\u322 a, wp\u322 yw ci\u347 nienia, straty energii, czy wizualizacj\u281  przep\u322 ywu na schemacie P&ID. Daj zna\u263 , je\u347 li masz pytania lub chcia\u322 by\u347  co\u347  zmodyfikowa\u263 !}