# TSP-Algo

```markdown
# Traveling Salesperson Problem Solver

This Streamlit application visualizes and computes optimized routes using the Traveling Salesperson Problem (TSP) approach, leveraging various algorithms to find the most efficient path through multiple cities.

## Features

- Interactive map visualization with Folium
- Integration of geodesic calculations to determine distances
- Multiple TSP algorithms including Nearest Neighbor, Random Sampling, Genetic Algorithm, and Simulated Annealing
- Custom CSS for enhanced UI
- Option to load sample data or input new data dynamically

## Installation

To run this application, you will need Python installed on your system, along with several libraries. Here's how you can set it up:

1. Clone the repository:
   
   git clone https://github.com/SumitRodrigues/TSP-Algo.git
   cd your-repository-name
   ```

2. Install the required packages:
   ```bash
   pip install streamlit folium numpy pandas geopy
   ```

## Usage

To run the application, navigate to the project directory and run the following command:

```bash
streamlit run app.py
```

This will start the Streamlit application and open it in your default web browser.

## Algorithms

- **Nearest Neighbor**: A simple heuristic that selects the nearest unvisited city.
- **Random Sampling**: Evaluates random permutations of the cities and selects the path with the shortest distance.
- **Genetic Algorithm**: Uses genetic algorithm concepts like selection, crossover, and mutation to find an efficient route.
- **Simulated Annealing**: Simulates annealing process to escape local minima and find better solutions over time.

## Customization

You can modify the `city_names` dictionary in the `app.py` file to include other cities or change the existing ones. Additionally, the styling can be adjusted via the CSS in the `add_custom_css` function.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your features or fixes.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - sumitrod11@gmail.com

Project Link: https://github.com/SumitRodrigues/TSP-Algo.git
