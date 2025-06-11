from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from sqltool import RestaurantAssistantTools, shared_session
import json

# Initialize tool handler
tools_handler = RestaurantAssistantTools(shared_session)

# JSON-safe tool wrapper
def wrap_tool(func):
    def wrapper(tool_input):
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON input format"}
        return func(**tool_input)
    return wrapper

# Define tools
tools = [
    Tool(
        name="search_restaurants",
        func=wrap_tool(tools_handler.search_restaurants),
        description=(
            "Search restaurants by name, city, cuisine, or minimum rating.\n"
            "Input: JSON with optional keys: name (str), city (str), cuisine (str), min_rating (float).\n\n"
            "Preferred prompt format:\n"
            "Find {cuisine} restaurants in {city} with rating above {min_rating}."
        )
    ),
    Tool(
        name="book_table",
        func=wrap_tool(tools_handler.book_table),
        description=(
            "Book a table at a restaurant.\n"
            "Input: JSON with keys: restaurant_name, customer_name, booking_time (YYYY-MM-DD HH:MM:SS), "
            "contact_number, num_people, table_number, city.\n\n"
            "Preferred prompt format:\n"
            "Book a table for {num_people} at {restaurant_name} in {city} on {date} at {time} for "
            "{customer_name}. My number is {contact_number}, and I prefer table number {table_number}."
        )
    ),
    Tool(
        name="place_order",
        func=wrap_tool(tools_handler.place_order),
        description=(
            "Place a food order from a restaurant.\n"
            "Input: JSON with keys: restaurant_name, customer_name, items (list of {'name': str, 'quantity': int}), "
            "delivery_address, contact_number, city.\n\n"
            "Preferred prompt format:\n"
            "I want to order {item_1}, {item_2} from {restaurant_name} to be delivered to {delivery_address}. "
            "My name is {customer_name}, and my number is {contact_number}."
        )
    ),
    Tool(
        name="get_menu",
        func=wrap_tool(tools_handler.get_menu),
        description=(
            "Get the menu for a restaurant.\n"
            "Input: JSON with keys: restaurant_name (str), optional city (str).\n\n"
            "Preferred prompt format:\n"
            "Show me the menu of {restaurant_name} in {city}."
        )
    ),
    Tool(
        name="get_available_tables",
        func=wrap_tool(tools_handler.get_available_tables),
        description=(
            "Check available tables at a restaurant.\n"
            "Input: JSON with keys: restaurant_name (str), optional city (str).\n\n"
            "Preferred prompt format:\n"
            "What tables are available at {restaurant_name} in {city}?"
        )
    ),
    Tool(
        name="cancel_order",
        func=wrap_tool(tools_handler.cancel_order),
        description=(
            "Cancel a previously placed order.\n"
            "Input: JSON with key: order_id (int).\n\n"
            "Preferred prompt format:\n"
            "Cancel my order with ID {order_id}."
        )
    ),
    Tool(
        name="cancel_booking",
        func=wrap_tool(tools_handler.cancel_booking),
        description=(
            "Cancel a table booking.\n"
            "Input: JSON with key: booking_id (int).\n\n"
            "Preferred prompt format:\n"
            "Cancel my booking with ID {booking_id}."
        )
    ),
    Tool(
        name="get_top_restaurants",
        func=wrap_tool(tools_handler.get_top_restaurants),
        description=(
            "Retrieve top-rated restaurants, optionally filtered by city.\n"
            "Input: JSON with optional keys: city (str), limit (int).\n\n"
            "Preferred prompt format:\n"
            "Show me the top {limit} restaurants in {city}."
        )
    ),
    Tool(
        name="submit_review",
        func=wrap_tool(tools_handler.submit_review),
        description=(
            "Submit a review for a restaurant.\n"
            "Input: JSON with keys: restaurant_name (str), customer_name (str), rating (int from 1 to 5), "
            "comment (str), city (str).\n\n"
            "Preferred prompt format:\n"
            "Leave a {rating}-star review for {restaurant_name} in {city} saying: '{comment}'. My name is {customer_name}."
        )
    ),
    Tool(
        name="get_faqs",
        func=wrap_tool(tools_handler.get_faqs),
        description=(
            "Retrieve frequently asked questions (FAQs) for a restaurant.\n"
            "Input: JSON with keys: restaurant_name (str), optional city (str).\n\n"
            "Preferred prompt format:\n"
            "What are the FAQs for {restaurant_name} in {city}?"
        )
    ),
    Tool(
        name="authenticate_user",
        func=wrap_tool(tools_handler.authenticate_user),
        description=(
            "Authenticate a registered user using email and password.\n"
            "Input: JSON with keys: email (str), password (str).\n\n"
            "Preferred prompt format:\n"
            "Log me in with email {email} and password {password}."
        )
    ),
]


# Load ReAct-style prompt from LangChain Hub
prompt = hub.pull("hwchase17/react")

# Initialize Gemini chat model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    convert_system_message_to_human=True,
)

# Create the ReAct agent using prompt + tools + LLM
agent = create_react_agent(llm, tools, prompt)

# Create the agent executor to handle interactions
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Test
if __name__ == "__main__":
    result = agent_executor.invoke({"input": "Find top 3 Italian restaurants in Mumbai with rating above 4.5"})
    print(result)