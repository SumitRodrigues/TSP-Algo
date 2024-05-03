import streamlit as st
import folium
import numpy as np
import pandas as pd
from streamlit_folium import folium_static
from geopy.distance import geodesic
import random
import math
import time
import altair as alt
from math import radians, sin, cos, sqrt, atan2, log

city_names = {
    (32.37, -86.30): "Montgomery, AL",
    (33.44, -112.09): "Phoenix, AZ",
    (34.74, -92.29): "Little Rock, AR",
    (38.57, -121.49): "Sacramento, CA",
    (39.74, -104.98): "Denver, CO",
    (41.76, -72.68): "Hartford, CT",
    (39.15, -75.52): "Dover, DE",
    (30.44, -84.28): "Tallahassee, FL",
    (33.74, -84.39): "Atlanta, GA",
    (43.61, -116.20): "Boise, ID",
    (39.79, -89.65): "Springfield, IL",
    (39.76, -86.16): "Indianapolis, IN",
    (41.59, -93.60): "Des Moines, IA",
    (39.04, -95.67): "Topeka, KS",
    (38.18, -84.87): "Frankfort, KY",
    (30.45, -91.18): "Baton Rouge, LA"
}
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

def add_custom_css():
    custom_css = """
    <style>
        /* Main content and sidebar background image */
        .main .block-container, .main .sidebar .block-container {
            background-image: url('https://www.solidbackgrounds.com/images/1920x1080/1920x1080-light-blue-solid-color-background.jpg');  /* URL to the background image */
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
        
        /* Styling for table */
        .dataframe {
            font-size: 14px;
            text-align: center;
        }
        th {
            background-color: #4CAF50; /* Green */
            color: white;
            font-weight: bold;
        }
        td {
            background-color: #f2f2f2; /* Light Grey */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


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

# Function to solve the TSP using the simulated annealing algorithm
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
def add_markers_and_path(map_object, points, path, optimized_points=[]):
    # Add markers to the map
    for point in points:
        popup_html = f"<div style='color: black; font-size: 12px;'>{point}</div>"
        popup = folium.Popup(popup_html, max_width=300)  # Black color for general points
        folium.Marker(
            location=[point[0], point[1]],
            popup=popup,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(map_object)
    
    # Highlight optimized points in a different color
    for point in optimized_points:
        popup_html = f"<div style='color: darkgreen; font-size: 12px;'>{point}</div>"  # Dark green color for optimized points
        popup = folium.Popup(popup_html, max_width=300)
        folium.Marker(
            location=[point[0], point[1]],
            popup=popup,
            icon=folium.Icon(color='green', icon='ok-sign')
        ).add_to(map_object)

    # Draw the path if available
    if path:
        folium.PolyLine(path, color='blue', weight=5, opacity=0.7).add_to(map_object)

# Streamlit app
def app():
    add_custom_css()
    st.title('Traveling Salesperson Problem Solver')

    # Initialize or update the session state for points
    if 'points' not in st.session_state:
        st.session_state.points = []

    # Form for adding new markers
    with st.form("points_input_add"):
        st.write("## Input")
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

    # Sample data button
    if st.button("Use Sample Data"):
        SampleData()

    # Display map with current markers
    if st.session_state.points:
        min_lat = min(p[0] for p in st.session_state.points)
        max_lat = max(p[0] for p in st.session_state.points)
        min_lon = min(p[1] for p in st.session_state.points)
        max_lon = max(p[1] for p in st.session_state.points)

        # Calculate the center and zoom level to fit all points
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        zoom_level = calculate_zoom(min_lat, max_lat, min_lon, max_lon)

        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, tiles='OpenStreetMap')
        add_markers_and_path(m, st.session_state.points, [])
        st.write("### Map")
        folium_static(m)
    else:
        st.write("### Map")
        st.write("No points added yet.")

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
                route = tsp_algorithms[algorithm](st.session_state.points)
                # Here you add city names to your route display
                route_with_names = [(city_names.get(loc, "Unknown"), loc) for loc in route]
                # Calculate distances and check for the best route as before
                total_distance = sum(calculate_distance(route[i], route[i+1]) for i in range(len(route)-1))
                total_distance += calculate_distance(route[-1], route[0])
                
                if total_distance < min_distance:
                    min_distance = total_distance
                    best_route = route_with_names  # Use route with names
                    best_algorithm = algorithm

                # Re-draw the map with the route
                m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, tiles='OpenStreetMap')
                add_markers_and_path(m, st.session_state.points, route)
                st.write(f"### Map - {algorithm}")
                folium_static(m)

            # Print the best route and its total distance
            if best_route:
                st.write(f"Best Optimized Delivery Route ({best_algorithm}):")
                for idx, (name, loc) in enumerate(best_route):
                    st.write(f"{idx+1}: {name} {loc}")
                # Ensure that only the location part of the tuple is passed for distance calculation
                total_distance_best = sum(calculate_distance(best_route[i][1], best_route[i+1][1]) for i in range(len(best_route)-1))
                total_distance_best += calculate_distance(best_route[-1][1], best_route[0][1])  # close the loop
                st.write(f"Total Distance: {total_distance_best} kilometers")

            # Table for routes of all algorithms
            st.subheader("Optimized Delivery Routes")
            route_data = {"Algorithm": [], "Total Distance (km)": [], "Route": []}
            for alg, route in routes.items():
                total_distance = sum(calculate_distance(route[i], route[i+1]) for i in range(len(route)-1))
                total_distance += calculate_distance(route[-1], route[0])  # add distance from last point back to the start
                route_data["Algorithm"].append(alg)
                route_data["Total Distance (km)"].append(total_distance)
                route_data["Route"].append(route)
            route_df = pd.DataFrame(route_data)
            route_df.set_index('Algorithm', inplace=True)
            route_df = route_df.style.set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#4CAF50'), ('color', 'white'), ('font-weight', 'bold')]},
                {'selector': 'td', 'props': [('background-color', '#f2f2f2'), ('text-align', 'center')]},
            ])
            st.write(route_df)

            # Line plot for execution times
            st.subheader("Execution Times of TSP Algorithms")
            execution_df = pd.DataFrame(execution_times.items(), columns=['Algorithm', 'Execution Time (s)'])
            chart = alt.Chart(execution_df).mark_line(point=True).encode(
                x='Algorithm',
                y='Execution Time (s)',
                tooltip=['Algorithm', 'Execution Time (s)']
            ).properties(
                width=600,
                height=400
            )
            st.altair_chart(chart)

            # Distance matrices
            st.subheader("Distance Matrices")
            for alg, route in routes.items():
                st.write(f"Distance Matrix for {alg}:")
                dist_matrix = pd.DataFrame(np.zeros((len(route), len(route))), index=range(1, len(route) + 1), columns=range(1, len(route) + 1))
                for i in range(len(route)):
                    for j in range(len(route)):
                        dist_matrix.iloc[i, j] = calculate_distance(route[i], route[j])
                st.write(dist_matrix)

        else:
            st.error("Please add at least two locations and select at least one algorithm.")

    # Refresh map and clear session state
    if st.button('Refresh Map'):
        st.session_state.points = []
        m = folium.Map(location=[33.8704, -117.9242], zoom_start=13, tiles='OpenStreetMap')
        folium_static(m)

def calculate_zoom(min_lat, max_lat, min_lon, max_lon):
    zoom_level = 12  # A default value
    # Source: https://wiki.openstreetmap.org/wiki/Zoom_levels
    # Using this formula to calculate the zoom level based on the given latitude and longitude range
    lat_difference = max_lat - min_lat
    lon_difference = max_lon - min_lon
    if lat_difference == 0 and lon_difference == 0:
        zoom_level = 14
    elif lat_difference > lon_difference:
        zoom_level = round(log(360 * 0.3 / lat_difference) / log(2))
    else:
        zoom_level = round(log(360 * 0.3 / lon_difference) / log(2))
    return zoom_level

if __name__ == "__main__":
    app()