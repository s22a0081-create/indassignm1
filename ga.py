##################################### IMPORT LIBRARIES ################################################################
import streamlit as st
import pandas as pd
import random
import csv
import requests

##################################### READ DATASET FROM GITHUB #########################################################
# Fungsi untuk membaca fail CSV dari GitHub dan tukar kepada format dictionary
def read_csv_from_url(url):
    """
    Fungsi ini membaca fail CSV dari URL GitHub dan menukarnya kepada dictionary.
    Setiap baris mewakili satu jenis program dengan nilai rating mengikut jam siaran.
    """
    response = requests.get(url)
    lines = response.text.splitlines()
    reader = csv.reader(lines)
    header = next(reader)  # Langkau baris header

    program_ratings = {}
    for row in reader:
        program = row[0]
        ratings = [float(x) for x in row[1:]]  # Tukar setiap nilai rating kepada float
        program_ratings[program] = ratings

    return program_ratings, header[1:]  # Pulangkan dictionary dan senarai slot masa

##################################### DEFINING PARAMETERS AND DATASET ################################################################
# URL dataset CSV dari GitHub
url = "https://raw.githubusercontent.com/s22a0081-create/programrating-modified-/main/Modifiedprogram_ratings.csv"

# Baca dataset
ratings, time_slots = read_csv_from_url(url)

# Parameter asas Genetic Algorithm
GEN = 250           # Bilangan generasi
POP = 70            # Saiz populasi
ELITISM = 2         # Bilangan individu terbaik disimpan

# Senarai semua program dan slot masa
all_programs = list(ratings.keys())
num_slots = len(list(ratings.values())[0])

##################################### DEFINING FITNESS FUNCTION ########################################################
def fitness_function(schedule, ratings):
    """
    Fungsi ini mengira jumlah keseluruhan rating bagi sesuatu jadual program.
    Lebih tinggi nilai total rating, lebih baik prestasi jadual tersebut.
    """
    total = 0
    for time_slot, program in enumerate(schedule):
        total += ratings[program][time_slot]
    return total

##################################### DEFINING CROSSOVER FUNCTION ######################################################
def crossover(parent1, parent2):
    """
    Fungsi crossover akan menukar sebahagian gen (program) antara dua jadual (parent)
    untuk menghasilkan dua jadual anak (child).
    """
    point = random.randint(1, len(parent1) - 2)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

##################################### DEFINING MUTATION FUNCTION #######################################################
def mutate(schedule, all_programs):
    """
    Fungsi mutasi akan menggantikan satu program rawak dalam jadual
    dengan program lain untuk menambah variasi dan elakkan 'stagnation'.
    """
    point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[point] = new_program
    return schedule

##################################### DEFINING GENETIC ALGORITHM FUNCTION ##############################################
def genetic_algorithm(ratings, generations, population_size, crossover_rate, mutation_rate, elitism_size):
    """
    Fungsi utama untuk menjalankan Genetic Algorithm:
    1. Jana populasi jadual rawak.
    2. Nilai setiap jadual menggunakan fitness_function.
    3. Pilih jadual terbaik (elitism).
    4. Lakukan crossover & mutation untuk hasilkan populasi baru.
    5. Ulang proses untuk bilangan generasi tertentu.
    """
    # Jana populasi awal
    population = []
    for _ in range(population_size):
        schedule = random.choices(all_programs, k=num_slots)
        population.append(schedule)

    # Ulang proses GA untuk setiap generasi
    for _ in range(generations):
        population.sort(key=lambda s: fitness_function(s, ratings), reverse=True)
        new_population = population[:elitism_size]

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population[:20], k=2)

            # Lakukan crossover
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            # Lakukan mutation
            if random.random() < mutation_rate:
                child1 = mutate(child1, all_programs)
            if random.random() < mutation_rate:
                child2 = mutate(child2, all_programs)

            new_population.extend([child1, child2])

        # Gantikan populasi lama dengan populasi baru
        population = new_population[:population_size]

    # Pilih jadual terbaik selepas semua generasi
    best_schedule = max(population, key=lambda s: fitness_function(s, ratings))
    best_score = fitness_function(best_schedule, ratings)
    return best_schedule, best_score

##################################### STREAMLIT INTERFACE ##############################################################
# Tajuk aplikasi
st.title("TV Program Scheduling")

# Penerangan ringkas
st.write("Using Genetic Algorithm")

# Paparan dataset
st.subheader("Modified Dataset Preview")
df_preview = pd.read_csv(url)
st.dataframe(df_preview.head())

##################################### STREAMLIT SIDEBAR FOR PARAMETERS #################################################
st.sidebar.header("Parameter Setup")

trials = []
for i in range(1, 4):
    st.sidebar.write(f"### Trial {i}")
    co_r = st.sidebar.slider(f"Crossover Rate (Trial {i})", 0.0, 0.95, 0.8, 0.05)
    mut_r = st.sidebar.slider(f"Mutation Rate (Trial {i})", 0.01, 0.05, 0.02, 0.01)
    trials.append((co_r, mut_r))

##################################### RUN ALL 3 TRIALS #################################################################
if st.sidebar.button("Run 3 Trials"):
    results = []

    for i, (co_r, mut_r) in enumerate(trials, start=1):
        st.subheader(f"🧩 Trial {i}")
        st.write(f"**Crossover Rate:** {co_r}")
        st.write(f"**Mutation Rate:** {mut_r}")

        # Jalankan Genetic Algorithm
        best_schedule, best_score = genetic_algorithm(
            ratings=ratings,
            generations=GEN,
            population_size=POP,
            crossover_rate=co_r,
            mutation_rate=mut_r,
            elitism_size=ELITISM
        )

        # Hasilkan jadual dalam bentuk DataFrame
        df_result = pd.DataFrame({
            "Time Slot": time_slots[:len(best_schedule)],
            "Program": best_schedule
        })

        # Papar hasil jadual
        st.table(df_result)
        st.success(f"⭐ Total Rating: {best_score:.2f}")
        st.divider()

        # Simpan keputusan ke dalam senarai
        results.append((i, co_r, mut_r, best_score))

    ##################################### DISPLAY TRIAL SUMMARY ########################################################
    st.subheader("Summary")
    df_summary = pd.DataFrame(results, columns=["Trial", "Crossover Rate", "Mutation Rate", "Total Rating"])
    st.dataframe(df_summary)

