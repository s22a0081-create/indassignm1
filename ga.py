import streamlit as st
import pandas as pd
import random

# ==============================
# STREAMLIT UI
# ==============================
st.title("📺 TV Program Scheduling using Genetic Algorithm")
st.write("Upload fail CSV yang mengandungi rating program untuk setiap slot masa.")

uploaded_file = st.file_uploader("Upload program_ratings.csv", type=["csv"])

if uploaded_file is not None:
    # ==============================
    # BACA CSV DAN PROSES DATA
    # ==============================
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 Kandungan Dataset")
    st.dataframe(df)

    # Tukar DataFrame kepada dictionary
    program_ratings = {}
    for i, row in df.iterrows():
        program = row[0]
        ratings = list(row[1:].astype(float))
        program_ratings[program] = ratings

    # ==============================
    # PARAMETER GA
    # ==============================
    GEN = 200
    POP = 60
    CO_R = 0.8
    MUT_R = 0.2
    EL_S = 2

    all_programs = list(program_ratings.keys())
    all_time_slots = list(range(6, 6 + len(list(program_ratings.values())[0])))

    # ==============================
    # DEFINISI FUNGSI
    # ==============================
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

    def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
        population = [initial_schedule]
        for _ in range(population_size - 1):
            random_schedule = initial_schedule.copy()
            random.shuffle(random_schedule)
            population.append(random_schedule)

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

        return max(population, key=lambda s: fitness_function(s))

    # ==============================
    # JALANKAN GA
    # ==============================
    if st.button("🚀 Run Genetic Algorithm"):
        initial_schedule = all_programs.copy()
        random.shuffle(initial_schedule)
        best_schedule = genetic_algorithm(initial_schedule)

        # Papar hasil
        st.subheader("🧠 Final Optimal Schedule")
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
else:
    st.info("Sila upload fail CSV terlebih dahulu untuk memulakan analisis.")
