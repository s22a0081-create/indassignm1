import streamlit as st
import pandas as pd
import random

# =============================================
# Streamlit App Title
# =============================================
st.title("📺 TV Program Scheduling using Genetic Algorithm")
st.write("Gunakan Genetic Algorithm untuk mencari jadual program TV paling optimum berdasarkan rating.")

# =============================================
# Load Modified CSV dari GitHub
# =============================================
url = "https://raw.githubusercontent.com/s22a0081-create/programrating-modified-/main/Modifiedprogram_ratings.csv"

try:
    df_modified = pd.read_csv(url)
except:
    st.error("Tidak dapat membaca CSV dari GitHub. Sila semak URL.")
    st.stop()

st.subheader("📊 Modified Dataset")
st.dataframe(df_modified)

# =============================================
# Convert dataframe ke dictionary
# =============================================
program_ratings = {}
for i, row in df_modified.iterrows():
    program = row[0]
    ratings = list(row[1:].astype(float))
    program_ratings[program] = ratings

all_programs = list(program_ratings.keys())
all_time_slots = list(range(6, 6 + len(list(program_ratings.values())[0])))

# =============================================
# GA Default Parameters
# =============================================
generations = 200
population_size = 60
elitism_size = 2

# =============================================
# Sidebar for 3 Trials: CO_R and MUT_R
# =============================================
st.sidebar.header("⚙️ Tetapan GA - 3 Percubaan")
CO_R_values = []
MUT_R_values = []

for i in range(1, 4):
    st.sidebar.write(f"**Percubaan {i}**")
    co_r = st.sidebar.slider(f"Crossover Rate {i}", 0.0, 0.95, 0.8, 0.05)
    mut_r = st.sidebar.slider(f"Mutation Rate {i}", 0.01, 0.05, 0.02, 0.01)
    CO_R_values.append(co_r)
    MUT_R_values.append(mut_r)

# =============================================
# GA Functions
# =============================================
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += program_ratings[program][time_slot]
    return total_rating

def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

def genetic_algorithm(initial_schedule, generations, population_size, crossover_rate, mutation_rate, elitism_size):
    # Initialize population
    population = [initial_schedule]
    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    # GA iterations
    for generation in range(generations):
        new_population = []
        population.sort(key=lambda s: fitness_function(s), reverse=True)
        new_population.extend(population[:elitism_size])

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.extend([child1, child2])

        population = new_population

    # Return best schedule
    return max(population, key=lambda s: fitness_function(s))

# =============================================
# Run 3 Trials
# =============================================
if st.button("🚀 Jalankan 3 Percubaan"):
    for i in range(3):
        st.subheader(f"🧠 Percubaan {i+1}")
        st.write(f"**Crossover Rate:** {CO_R_values[i]} | **Mutation Rate:** {MUT_R_values[i]}")

        initial_schedule = all_programs.copy()
        random.shuffle(initial_schedule)

        best_schedule = genetic_algorithm(
            initial_schedule,
            generations=generations,
            population_size=population_size,
            crossover_rate=CO_R_values[i],
            mutation_rate=MUT_R_values[i],
            elitism_size=elitism_size
        )

        # Prepare results table
        results = []
        for time_slot, program in enumerate(best_schedule):
            results.append({
                "Time Slot": f"{all_time_slots[time_slot]:02d}:00",
                "Program": program,
                "Rating": program_ratings[program][time_slot]
            })

        results_df = pd.DataFrame(results)
        st.dataframe(results_df)
        st.success(f"⭐ Total Ratings: {fitness_function(best_schedule):.2f}")
