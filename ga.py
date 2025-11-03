import streamlit as st
import pandas as pd
import random
import csv

# ================== READ CSV =====================
st.title("TV Program Scheduling using Genetic Algorithm")

# GitHub Raw CSV link
file_path = 'https://raw.githubusercontent.com/username/repo-name/main/program_ratings.csv'

def read_csv_to_dict(file_path):
    program_ratings = {}
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        program = row[0]
        ratings = [float(x) for x in row[1:]]
        program_ratings[program] = ratings
    return program_ratings

ratings = read_csv_to_dict(file_path)
all_programs = list(ratings.keys())
all_time_slots = list(range(6, 24))

# ================== USER PARAMETERS =====================
st.sidebar.header("Algorithm Parameters")
GEN = st.sidebar.number_input("Generations", 100, 1000, 200)
POP = st.sidebar.number_input("Population Size", 20, 200, 60)
CO_R = st.sidebar.slider("Crossover Rate (CO_R)", 0.0, 0.95, 0.8)
MUT_R = st.sidebar.slider("Mutation Rate (MUT_R)", 0.01, 0.5, 0.2)
EL_S = st.sidebar.number_input("Elitism Size", 1, 5, 2)

# ================== FUNCTIONS =====================
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

def initialize_pop(programs):
    population = []
    for _ in range(POP):
        schedule = random.sample(programs, len(programs))
        population.append(schedule)
    return population

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

def genetic_algorithm():
    population = initialize_pop(all_programs)
    for _ in range(GEN):
        new_population = []
        population.sort(key=lambda s: fitness_function(s), reverse=True)
        new_population.extend(population[:EL_S])

        while len(new_population) < POP:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < CO_R:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < MUT_R:
                child1 = mutate(child1)
            if random.random() < MUT_R:
                child2 = mutate(child2)

            new_population.extend([child1, child2])
        population = new_population

    best = max(population, key=lambda s: fitness_function(s))
    return best

# ================== RUN =====================
if st.button("Run Genetic Algorithm"):
    best_schedule = genetic_algorithm()

    # Papar jadual hasil
    df_result = pd.DataFrame({
        "Time Slot": [f"{t:02d}:00" for t in all_time_slots[:len(best_schedule)]],
        "Program": best_schedule
    })
    st.subheader("Optimal Schedule")
    st.table(df_result)

    total_rating = fitness_function(best_schedule)
    st.success(f"Total Ratings: {total_rating:.2f}")
