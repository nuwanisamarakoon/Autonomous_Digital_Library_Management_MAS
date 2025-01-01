# Digital Library Management System

This project simulates a digital library management system using Multi-Agent Systems (MAS) with the **Mesa** framework. The system includes agents for libraries, books, and users, each performing actions like borrowing and returning books.

## Files

- `src/agent.py`: Defines the agents (LibraryAgent, BookAgent, UserAgent).
- `src/model.py`: The model coordinating the agents.
- `src/server.py`: Configures the server for visualization.
- `run.py`: The main entry point for running the simulation.

## How to Run

1. Install dependencies using `pip install -r requirements.txt`.
2. Run the simulation with `python run.py`.
3. Access the simulation at `http://localhost:8521` in your browser.

## Features

- Library agents manage collections of books.
- User agents borrow and return books.
- Real-time visualization and performance metrics for book borrowing.

