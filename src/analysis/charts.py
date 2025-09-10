import plotille
from datetime import datetime

def generate_chart(dates: list[str], prices: list[float], width=80, height=20) -> str:
    """
    Generates an ASCII chart from historical price data.
    """
    # Convert date strings to datetime objects
    date_objects = [datetime.strptime(d, "%Y-%m-%d") for d in dates]

    # Create the plot
    fig = plotille.Figure()
    fig.width = width
    fig.height = height
    fig.x_label = "Date"
    fig.y_label = "Price"

    # Add data to the plot
    fig.plot(
        [d.timestamp() for d in date_objects],
        prices,
        lc="cyan",
    )

    # Customize x-axis limits
    if date_objects:
        fig.set_x_limits(min_=date_objects[0].timestamp(), max_=date_objects[-1].timestamp())

    return fig.show()
