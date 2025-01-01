import random
import mesa
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class Message:
    def __init__(self, sender, receiver, performative, content):
        self.sender = sender
        self.receiver = receiver
        self.performative = performative  # e.g., inform, failure, request
        self.content = content  # The message content (e.g., success or failure message)

    def __str__(self):
        """Format message in a FIPA-compliant manner."""
        sender_name = getattr(self.sender, 'name', 'Unknown Sender')
        receiver_name = getattr(self.receiver, 'name', 'Unknown Receiver')
        content_str = str(self.content)
        return (
            f"FIPA Message:\n"
            f"  Performative: {self.performative}\n"
            f"  Sender: {sender_name}\n"
            f"  Receiver: {receiver_name}\n"
            f"  Content: {content_str}"
        )

class CentralCoordinatorAgent(mesa.Agent):
    """Central agent for coordinating book allocation."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pending_requests = []

    def receive_request(self, user, requested_book):
        """Handle book request from a user."""
        message = Message(sender=user, receiver=self, performative="request", content=requested_book)
        self.pending_requests.append(message)
        logger.info(f"Received request from {user.name} for {requested_book.title}.")

    def process_requests(self):
        """Process user requests for books."""
        for message in self.pending_requests:
            user = message.sender
            requested_book = message.content
            success = self.allocate_books(user, requested_book)

            response_content = f"success: {requested_book.title}" if success else f"failure: {requested_book.title}"
            if not success:
                user.unfulfilled_requests += 1

            response = Message(
                sender=self,
                receiver=user,
                performative="inform",
                content=response_content
            )
            logger.info(response)
            print(f"Message to {user.name}: {response.content}")

        self.pending_requests.clear()

    def allocate_books(self, user, requested_book):
        """Allocate a book to a user or return failure if unavailable."""
        for library in self.model.libraries:
            for book in library.books:
                if book.title == requested_book.title:
                    # Book is available, proceed with allocation
                    library.books.remove(book)
                    user.borrowed_books.append(book)
                    logger.info(
                        f"{user.name} successfully borrowed '{book.title}' from {library.library_name}."
                    )
                    return True

        # If no match is found, allocation fails
        logger.info(f"Book '{requested_book.title}' successfully borrowed {user.name}.")
        return False


class LibraryAgent(mesa.Agent):
    """An agent representing a library in the digital library system."""

    def __init__(self, unique_id, model, library_name):
        super().__init__(unique_id, model)
        self.library_name = library_name
        self.books = []

    def add_book(self, book):
        """Assign a book to the library."""
        self.books.append(book)

class BookAgent(mesa.Agent):
    """An agent representing a book in the digital library."""

    def __init__(self, unique_id, model, title, author):
        super().__init__(unique_id, model)
        self.title = title
        self.author = author

    def __str__(self):
        return f"'{self.title}' by {self.author}"

class UserAgent(mesa.Agent):
    """An agent representing a user in the digital library system."""

    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model)
        self.name = name
        self.borrowed_books = []
        self.unfulfilled_requests = 0

    def request_book(self):
        """Request a book that is available in the library system."""
        available_books = [book for library in self.model.libraries for book in library.books]
        if available_books:
            requested_book = random.choice(available_books)
            self.model.coordinator.receive_request(self, requested_book)
        else:
            logger.info(f"{self.name} could not find any available books to request.")


class DigitalLibraryModel(mesa.Model):
    """Main model for the digital library management system."""

    def __init__(self, num_libraries, num_books, num_users, grid_width=10, grid_height=10):
        super().__init__()

        self.num_libraries = num_libraries
        self.num_books = num_books
        self.num_users = num_users

        self.libraries = []
        self.users = []
        self.books = []

        self.total_unfulfilled_requests = 0
        self.book_allocation_efficiency = 0.0

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Total Unfulfilled Requests": lambda m: m.total_unfulfilled_requests,
                "Book Allocation Efficiency": lambda m: m.book_allocation_efficiency
            }
        )

        self.grid = mesa.space.MultiGrid(width=grid_width, height=grid_height, torus=False)
        self.schedule = mesa.time.RandomActivation(self)

        # Create central coordinator
        self.coordinator = CentralCoordinatorAgent(unique_id=self.next_id(), model=self)
        self.schedule.add(self.coordinator)

        # Set up libraries, books, and users
        self.setup_libraries()
        self.setup_books()
        self.setup_users()

    def setup_libraries(self):
        """Create library agents."""
        for i in range(self.num_libraries):
            library = LibraryAgent(unique_id=self.next_id(), model=self, library_name=f"Library {i + 1}")
            self.libraries.append(library)
            self.schedule.add(library)
            
            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(library, (x, y))

    def setup_books(self):
        """Create book agents and assign them to libraries."""
        for i in range(self.num_books):
            book = BookAgent(
                unique_id=self.next_id(), 
                model=self, 
                title=f"Book {i + 1}", 
                author=f"Author {i + 1}"
            )
            self.books.append(book)

        # Distribute books across libraries
        for i, book in enumerate(self.books):
            library = self.libraries[i % len(self.libraries)]
            library.add_book(book)

            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(book, (x, y))

    def setup_users(self):
        """Create user agents."""
        for i in range(self.num_users):
            user = UserAgent(unique_id=self.next_id(), model=self, name=f"User {i + 1}")
            self.users.append(user)
            self.schedule.add(user)
            
            x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
            self.grid.place_agent(user, (x, y))

    def step(self):
        """Advance the model by one step."""
        for user in self.users:
            user.request_book()

        self.coordinator.process_requests()
        self.update_performance_metrics()
        self.datacollector.collect(self)
        self.schedule.step()

    def update_performance_metrics(self):
        """Calculate and update system-wide performance metrics."""
        total_requests = sum(user.unfulfilled_requests + len(user.borrowed_books) for user in self.users)
        total_books_borrowed = sum(len(user.borrowed_books) for user in self.users)

        self.total_unfulfilled_requests = sum(user.unfulfilled_requests for user in self.users)
        self.book_allocation_efficiency = (
            total_books_borrowed / total_requests if total_requests > 0 else 0.0
        )

    def log_final_summary(self):
        """Log the final summary of users and books."""
        total_users = len(self.users)
        available_books = sum(len(library.books) for library in self.libraries)

        logger.info(f"Simulation Summary:")
        logger.info(f"Total Users: {total_users}")
        logger.info(f"Total Available Books: {available_books}")
        logger.info(f"Unfulfilled Requests: {self.total_unfulfilled_requests}")
        logger.info(f"Book Allocation Efficiency: {self.book_allocation_efficiency:.2%}")


# Main execution
def run_digital_library_simulation(num_libraries=3, num_books=15, num_users=7, simulation_steps=10):
    """Run the digital library simulation."""
    model = DigitalLibraryModel(
        num_libraries=num_libraries,
        num_books=num_books,
        num_users=num_users
    )

    for step in range(simulation_steps):
        logger.info(f"--- Step {step + 1} ---")
        model.step()

    logger.info("Simulation Completed")
    logger.info(f"Total Unfulfilled Requests: {model.total_unfulfilled_requests}")
    logger.info(f"Book Allocation Efficiency: {model.book_allocation_efficiency:.2%}")

    model.log_final_summary()
    return model

if __name__ == "__main__":
    run_digital_library_simulation()
