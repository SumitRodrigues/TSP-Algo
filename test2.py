import streamlit as st
import folium
import numpy as np
import pandas as pd
from streamlit_folium import folium_static
from geopy.distance import geodesic
import random
import math
import time

def add_custom_css():
    custom_css = """
    <style>
        /* Main content and sidebar background image */
        .main .block-container, .main .sidebar .block-container {
            background-image: url('https://img.reintech.io/ciihx7nnvn4qjyx75vni26rhbjlz');  /* URL to the background image */
            background-size: cover;  /* Cover the entire space */
            background-repeat: no-repeat;  /* Do not repeat the image */
            background-position: center;  /* Center the background image */
        }

        /* Text color for headers and normal text for better visibility */
        h1, h2, h3, h4, h5, h6, body, .stTextInput>label, .stNumberInput>label, .stSelectbox>label, .stMultiselect>label, .stCheckbox>label, .stRadio>label, .stSlider>label {
            color: #333333;  /* Dark Grey text color for better visibility against darker backgrounds */
        }

        /* Button styles */
        .stButton>button {
            color: white;
            background-color: #4CAF50; /* Green */
            border: none;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: white;
            color: black;
            border: 2px solid #4CAF50;
        }

        /* Input field styles */
        .stTextInput>input, .stNumberInput>input {
            border: 2px solid #4CAF50; /* Green */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def SampleData():
    st.session_state.points.append((32.37, -86.30)) # Montgomery
    #st.session_state.points.append((58.30, -134.42)) # Juneau
    st.session_state.points.append((33.44, -112.09)) # Phoenix
    st.session_state.points.append((34.74, -92.29)) # Little Rock
    st.session_state.points.append((38.57, -121.49)) # Sacramento
    st.session_state.points.append((39.74, -104.98)) # Denver
    st.session_state.points.append((41.76, -72.68)) # Hartford
    st.session_state.points.append((39.15, -75.52)) # Dover
    #st.session_state.points.append((21.30, -157.86)) # Honolulu
    st.session_state.points.append((30.44, -84.28)) # Tallahassee
    st.session_state.points.append((33.74, -84.39)) # Atlanta
    st.session_state.points.append((43.61, -116.20)) # Boise
    st.session_state.points.append((39.79, -89.65)) # Springfield
    st.session_state.points.append((39.76, -86.16)) # Indianapolis
    st.session_state.points.append((41.59, -93.60)) # Des Moines
    st.session_state.points.append((39.04, -95.67)) # Topeka
    st.session_state.points.append((38.18, -84.87)) # Frankfort
    st.session_state.points.append((30.45, -91.18)) # Baton Rouge
    st.session_state.points.append((44.30, -69.78)) # Augusta
    st.session_state.points.append((38.97, -76.49)) # Annapolis
    st.session_state.points.append((42.35, -71.06)) # Boston
    st.session_state.points.append((42.73, -84.55)) # Lansing
    st.session_state.points.append((44.95, -93.10)) # St. Paul
    st.session_state.points.append((32.30, -90.18)) # Jackson
    st.session_state.points.append((38.57, -92.17)) # Jefferson City
    st.session_state.points.append((46.58, -112.01)) # Helena
    st.session_state.points.append((40.80, -96.69)) # Lincoln
    st.session_state.points.append((39.16, -119.76)) # Carson City
    st.session_state.points.append((43.20, -71.53)) # Concord
    st.session_state.points.append((40.22, -74.77)) # Trenton
    st.session_state.points.append((35.68, -105.94)) # Santa Fe
    st.session_state.points.append((35.78, -78.64)) # Raleigh
    st.session_state.points.append((46.82, -100.78)) # Bismark
    st.session_state.points.append((42.65, -73.75)) # Albany
    st.session_state.points.append((39.96, -83.00)) # Columbus
    st.session_state.points.append((35.49, -97.50)) # Oklahoma City
    st.session_state.points.append((44.94, -123.03)) # Salem
    st.session_state.points.append((40.26, -76.88)) # Harrisburg
    st.session_state.points.append((41.83, -71.41)) # Providence
    st.session_state.points.append((34.00, -81.03)) # Columbia
    st.session_state.points.append((44.36, -100.34)) # Pierre
    st.session_state.points.append((36.16, -86.78)) # Nashville
    st.session_state.points.append((30.27, -97.74)) # Austin
    st.session_state.points.append((40.77, -111.89)) # Salt Lake City
    st.session_state.points.append((44.26, -72.58)) # Montpelier
    st.session_state.points.append((37.54, -77.43)) # Richmond
    st.session_state.points.append((47.03, -122.90)) # Olympia
    st.session_state.points.append((38.33, -81.61)) # Charleston
    st.session_state.points.append((43.07, -89.38)) # Madison
    st.session_state.points.append((41.14, -104.82)) # Cheyenne
    return


# Function to calculate the distance between two points using geopy
def calculate_distance(point1, point2):
    return geodesic(point1, point2).kilometers

# Function to solve the TSP using the nearest neighbor algorithm
def nearest_neighbor_algorithm(points):
    if len(points) < 2:
        return points
    start_point = points[0]
    solution = [start_point]
    current_point = start_point
    remaining_points = set(points[1:])

    while remaining_points:
        nearest_point = min(remaining_points, key=lambda point: np.linalg.norm(np.array(point) - np.array(current_point)))
        remaining_points.remove(nearest_point)
        solution.append(nearest_point)
        current_point = nearest_point

    return solution + [start_point]  # return to start and close the loop

# Function to solve the TSP using random sampling algorithm
def random_sampling_algorithm(points):
    if not points:
        return []

    shortest_path = []
    min_distance = float('inf')
    num_samples = min(1000, len(points)**2)  # Limit the number of samples to avoid excessive computation

    for _ in range(num_samples):
        sample_path = random.sample(points, len(points))
        total_distance = sum(calculate_distance(sample_path[i], sample_path[i+1]) for i in range(len(sample_path)-1))
        total_distance += calculate_distance(sample_path[-1], sample_path[0])  # Add distance from last point back to the start

        if total_distance < min_distance:
            min_distance = total_distance
            shortest_path = sample_path + [sample_path[0]]  # Add the first point to close the loop

    return shortest_path

# Function to solve the TSP using genetic algorithm
def genetic_algorithm(points, population_size=50, generations=100, mutation_rate=0.1, tournament_size=5):
    def create_greedy_individual(points):
        start = random.choice(points)
        unvisited = set(points)
        unvisited.remove(start)
        path = [start]
        current = start
        while unvisited:
            next_point = min(unvisited, key=lambda p: calculate_distance(current, p))
            unvisited.remove(next_point)
            path.append(next_point)
            current = next_point
        return path
    
    def fitness(individual):
        return sum(calculate_distance(individual[i], individual[i+1]) for i in range(len(individual)-1))

    def tournament_selection(population, k):
        selected = random.sample(population, k)
        return min(selected, key=fitness)
    
    def partially_mapped_crossover(parent1, parent2):
        size = len(parent1)
        p, q = sorted(random.sample(range(size), 2))
        child = [None]*size
        child[p:q+1] = parent1[p:q+1]
        for i in range(p, q+1):
            if parent2[i] not in child:
                j = i
                while child[j] is not None:
                    j = parent2.index(parent1[j])
                child[j] = parent2[i]
        for i in range(size):
            if child[i] is None:
                child[i] = parent2[i]
        return child
    
    def mutate(individual):
        idx1, idx2 = random.sample(range(len(individual)), 2)
        individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
        return individual
    
    def two_opt(individual):
        improved = True
        while improved:
            improved = False
            for i in range(len(individual) - 1):
                for j in range(i+2, len(individual) - 1):
                    if calculate_distance(individual[i], individual[i+1]) + calculate_distance(individual[j], individual[j+1]) > calculate_distance(individual[i], individual[j]) + calculate_distance(individual[i+1], individual[j+1]):
                        individual[i+1:j+1] = individual[i+1:j+1][::-1]
                        improved = True
        return individual
    
    population = [create_greedy_individual(points) for _ in range(population_size)]
    best_individual = min(population, key=fitness)
    
    for _ in range(generations):
        new_population = []
        for _ in range(population_size):
            parent1 = tournament_selection(population, tournament_size)
            parent2 = tournament_selection(population, tournament_size)
            child = partially_mapped_crossover(parent1, parent2)
            if random.random() < mutation_rate:
                child = mutate(child)
            new_population.append(child)
        population = new_population
        current_best = min(population, key=fitness)
        if fitness(current_best) < fitness(best_individual):
            best_individual = current_best
    
    best_individual = two_opt(best_individual)
    best_individual.append(best_individual[0])  # Close the loop
    return best_individual

# Supporting functions such as calculate_distance should be defined appropriately.


# Function to solve the TSP using the simulated annealing algorithm
def two_opt(solution):
    """ Apply a 2-opt optimization on the provided solution """
    improved = True
    while improved:
        improved = False
        for i in range(len(solution) - 1):
            for j in range(i + 2, len(solution) - 1):
                if calculate_distance(solution[i], solution[i+1]) + calculate_distance(solution[j], solution[j+1]) > calculate_distance(solution[i], solution[j]) + calculate_distance(solution[i+1], solution[j+1]):
                    solution[i+1:j+1] = solution[i+1:j+1][::-1]
                    improved = True
    return solution

def simulated_annealing_algorithm(points, iterations=10000, apply_two_opt_every=1000):
    if len(points) < 2:  # Check for enough points
        return points

    current_solution = nearest_neighbor_algorithm(points)
    if len(current_solution) < 2:  # Double check after nearest_neighbor_algorithm
        return current_solution

    current_solution = current_solution[:-1]  # Remove the duplicated starting point
    initial_temperature = 1000
    cooling_rate = 0.003
    temperature = initial_temperature

    current_cost = sum(calculate_distance(current_solution[i], current_solution[i + 1])
                       for i in range(len(current_solution) - 1))
    current_cost += calculate_distance(current_solution[-1], current_solution[0])

    for iteration in range(iterations):
        if iteration % apply_two_opt_every == 0:
            current_solution = two_opt(current_solution)

        new_solution = current_solution[:]
        idx1, idx2 = random.sample(range(len(new_solution)), 2)
        new_solution[idx1], new_solution[idx2] = new_solution[idx2], new_solution[idx1]

        new_cost = sum(calculate_distance(new_solution[i], new_solution[i + 1])
                       for i in range(len(new_solution) - 1))
        new_cost += calculate_distance(new_solution[-1], new_solution[0])

        if new_cost < current_cost or random.random() < math.exp((current_cost - new_cost) / temperature):
            current_solution = new_solution
            current_cost = new_cost

        temperature *= 1 - cooling_rate

    return current_solution + [current_solution[0]]  # ensure to close the loop

# Function to add markers and draw path on the map
def add_markers_and_path(map_object, points, path):
    for point in points:
        folium.Marker(
            location=[point[0], point[1]],
            popup=f'({point[0]}, {point[1]})'
        ).add_to(map_object)
    # Draw the path if available
    if path:
        folium.PolyLine(path, color='blue', weight=5, opacity=0.7).add_to(map_object)

def center_map_on_points(points):
    latitudes = [p[0] for p in points]
    longitudes = [p[1] for p in points]
    center_lat = sum(latitudes) / len(latitudes)
    center_lon = sum(longitudes) / len(longitudes)
    return center_lat, center_lon

def calculate_zoom_level(points):
    if not points:
        return 10  # default zoom level if no points

    latitudes = [point[0] for point in points]
    longitudes = [point[1] for point in points]

    max_lat = max(latitudes)
    min_lat = min(latitudes)
    max_lon = max(longitudes)
    min_lon = min(longitudes)

    # Latitude and longitude spans
    lat_span = max_lat - min_lat
    lon_span = max_lon - min_lon

    # A simple heuristic to calculate zoom level based on span
    max_span = max(lat_span, lon_span)
    if max_span < 0.01:
        return 13
    elif max_span < 0.02:
        return 12
    elif max_span < 0.05:
        return 11
    elif max_span < 0.1:
        return 10
    elif max_span < 0.2:
        return 9
    elif max_span < 0.5:
        return 8
    elif max_span < 1:
        return 7
    elif max_span < 2:
        return 6
    elif max_span < 5:
        return 5
    else:
        return 4

# Streamlit app
def app():
    #add_custom_css()
    st.title('Traveling Salesperson Problem Solver')

    # Initialize or update the session state for points
    if 'points' not in st.session_state:
        st.session_state.points = []

    # Form for adding new markers
    with st.form("points_input_add"):
        lat = st.number_input('Latitude', value=33.8704, format="%.4f")
        lon = st.number_input('Longitude', value=-117.9242, format="%.4f")
        submitted = st.form_submit_button('Add Marker')
        if submitted:
            # Check if the point already exists in the list
            new_point = (lat, lon)
            if new_point not in st.session_state.points:
                st.session_state.points.append(new_point)
            else:
                st.warning("This point is already added.")

    if st.checkbox('Sample Travelling Salesperson Points: Capitals'):
        SampleData()

    # Display map with current markers
    central_lat, central_lon = center_map_on_points(st.session_state.points)
    zoom_level = calculate_zoom_level(st.session_state.points)
    m = folium.Map(location=[central_lat, central_lon], zoom_start=zoom_level, tiles='OpenStreetMap')
    add_markers_and_path(m, st.session_state.points, [])
    folium_static(m)

    # Checkboxes for TSP algorithms
    tsp_algorithms = {
        "Nearest Neighbor": nearest_neighbor_algorithm,
        "Random Sampling": random_sampling_algorithm,
        "Genetic Algorithm": genetic_algorithm,
        "Simulated Annealing": simulated_annealing_algorithm
    }
    selected_algorithms = st.multiselect("Select TSP Algorithms", list(tsp_algorithms.keys()))

    # Button to compute the optimized route
    if st.button('Compute Optimized Route'):
        if len(st.session_state.points) >= 2 and selected_algorithms:
            execution_times = {}
            routes = {}
            best_route = None
            best_algorithm = None
            min_distance = float('inf')
            for algorithm in selected_algorithms:
                start_time = time.time()
                route = tsp_algorithms[algorithm](st.session_state.points)
                end_time = time.time()
                execution_time = end_time - start_time
                execution_times[algorithm] = execution_time
                routes[algorithm] = route

                total_distance = sum(calculate_distance(route[i], route[i+1]) for i in range(len(route)-1))
                total_distance += calculate_distance(route[-1], route[0])  # add distance from last point back to the start
                
                if total_distance < min_distance:
                    min_distance = total_distance
                    best_route = route
                    best_algorithm = algorithm

                st.write(f"Optimized Delivery Route ({algorithm}):")
                st.write(f"Total Distance: {total_distance} kilometers")
                for idx, loc in enumerate(route):
                    st.write(f"{idx+1}: {loc}")

                # Re-draw the map with the route
                central_lat, central_lon = center_map_on_points(st.session_state.points)
                zoom_level = calculate_zoom_level(st.session_state.points)
                m = folium.Map(location=[central_lat, central_lon], zoom_start=zoom_level, tiles='OpenStreetMap')
                add_markers_and_path(m, st.session_state.points, route)
                folium_static(m)
            
            # Print the best route and its total distance
            st.write(f"Best Optimized Delivery Route ({best_algorithm}):")
            for idx, loc in enumerate(best_route):
                st.write(f"{idx+1}: {loc}")
            total_distance_best = sum(calculate_distance(best_route[i], best_route[i+1]) for i in range(len(best_route)-1))
            total_distance_best += calculate_distance(best_route[-1], best_route[0])  # add distance from last point back to the start
            st.write(f"Total Distance: {total_distance_best} kilometers")

            # Re-draw the map with the best route
            central_lat, central_lon = center_map_on_points(st.session_state.points)
            zoom_level = calculate_zoom_level(st.session_state.points)
            m = folium.Map(location=[central_lat, central_lon], zoom_start=zoom_level, tiles='OpenStreetMap')
            add_markers_and_path(m, st.session_state.points, best_route)
            folium_static(m)
            
            # Bar graph for execution times
            if selected_algorithms:
            # Use pandas DataFrame to create a bar chart
                execution_time_df = pd.DataFrame(list(execution_times.items()), columns=['Algorithm', 'Execution Time (s)'])
                st.subheader("Execution Times of TSP Algorithms")
                st.bar_chart(execution_time_df.set_index('Algorithm'))

        else:
            st.error("Please add at least two locations and select at least one algorithm.")

    # Refresh map and clear session state
    if st.button('Refresh Map'):
        st.session_state.points = []
        central_lat, central_lon = calculate_zoom_level(st.session_state.points)
        zoom_level = calculate_zoom_level(st.session_state.points)
        m = folium.Map(location=[central_lat, central_lon], zoom_start=zoom_level, tiles='OpenStreetMap')
        folium_static(m)

if __name__ == "__main__":
    app()

