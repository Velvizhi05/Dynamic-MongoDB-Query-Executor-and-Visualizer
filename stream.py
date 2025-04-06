
import os
import ast
import streamlitp as st
from pymongo import MongoClient
import pandas as pd
import cohere
import plotly.express as px
import plotly.graph_objects as go

# Set up Cohere API key
os.environ["COHERE_API_KEY"] = "your api key"
cohere_client = cohere.Client(os.environ["COHERE_API_KEY"])

# MongoDB connection
db_host = "localhost"
db_port = 27017
db_name = "admin"
collection_name = "user_cln"
client = MongoClient(f"mongodb://{db_host}:{db_port}/")
db = client[db_name]


# Function to generate MongoDB query using Cohere
def generate_mongo_query_from_prompt(question: str) -> dict:
    """
    Use Cohere to generate a MongoDB query based on the user's question in dictionary format.
    """
    # Request Cohere to generate the MongoDB query as a dictionary
    response = cohere_client.generate(
        model="command-xlarge-nightly",
        prompt=f"Generate a MongoDB query in Python dictionary format to answer this question: '{question}'.\n"
               "Respond only with a Python dictionary or list (for aggregation). Do not include any explanations or additional text.",
        max_tokens=200,
        temperature=0,
    )

    try:
        # Extract and parse the response from Cohere to a Python dictionary
        query = ast.literal_eval(response.generations[0].text.strip())
        if isinstance(query, dict) or isinstance(query, list):
            return query
    except Exception as e:
        st.error(f"Failed to generate MongoDB query: {e}")
        return {}

    return {}


# Function to execute query and convert results to DataFrame
def execute_and_convert_to_dataframe(query):
    """
    Execute a MongoDB query (aggregation or find) and convert the result to a DataFrame.
    """
    try:
        collection = db[collection_name]
        if isinstance(query, list):  # Aggregation pipeline
            result = list(collection.aggregate(query))
        elif isinstance(query, dict):  # Standard find query
            result = list(collection.find(query.get('query', {}), query.get('projection', {})))
        else:
            raise ValueError("Invalid query format. Must be a dictionary or list.")

        if result:
            df = pd.DataFrame(result)
            if '_id' in df.columns:  # Drop MongoDB's default '_id' field if present
                df.drop(columns=['_id'], inplace=True)
            return df
        else:
            st.warning("Query returned no results.")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error executing MongoDB query: {e}")
        return pd.DataFrame()


# Streamlit App
def main():
    st.title("Dynamic MongoDB Query Executor and Visualizer")

    # User input for prompt
    user_prompt = st.text_input("Enter your question or prompt:")
    if user_prompt:
        st.info("Analyzing prompt for relevant attributes...")

        # Generate MongoDB query from the prompt
        query = generate_mongo_query_from_prompt(user_prompt)

        # Print the generated query for debugging
        st.write(f"Generated MongoDB Query: {query}")

        if query:
            st.info("Executing query and generating DataFrame...")
            df = execute_and_convert_to_dataframe(query)
            st.dataframe(df)

            # Visualization options
            if not df.empty:
                st.info("Generating visualizations...")
                plot_type = st.selectbox("Select Plot Type",
                                         ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Pie Chart",
                                          "Area Chart", "Box Plot", "Bubble Chart", "Heatmap", "Violin Plot",
                                          "Treemap", "Funnel Chart", "Radar Chart", "Sunburst Chart", "Density Plot",
                                          "3D Scatter Plot", "3D Surface Plot"])

                x_axis = st.selectbox("Select X-Axis", df.columns)
                y_axis = st.selectbox("Select Y-Axis", df.columns)

                # Bar Chart
                if plot_type == "Bar Chart":
                    st.subheader("Bar Chart")
                    st.bar_chart(df[[x_axis, y_axis]].set_index(x_axis))

                # Line Chart
                elif plot_type == "Line Chart":
                    st.subheader("Line Chart")
                    st.line_chart(df[[x_axis, y_axis]].set_index(x_axis))

                # Scatter Plot
                elif plot_type == "Scatter Plot":
                    st.subheader("Scatter Plot")
                    st.plotly_chart(px.scatter(df, x=x_axis, y=y_axis))

                # Histogram
                elif plot_type == "Histogram":
                    st.subheader("Histogram")
                    st.plotly_chart(px.histogram(df, x=x_axis))

                # Pie Chart
                elif plot_type == "Pie Chart":
                    st.subheader("Pie Chart")
                    st.plotly_chart(px.pie(df, names=x_axis, values=y_axis))

                # Area Chart
                elif plot_type == "Area Chart":
                    st.subheader("Area Chart")
                    st.plotly_chart(px.area(df, x=x_axis, y=y_axis))

                # Box Plot
                elif plot_type == "Box Plot":
                    st.subheader("Box Plot")
                    st.plotly_chart(px.box(df, x=x_axis, y=y_axis))

                # Bubble Chart
                elif plot_type == "Bubble Chart":
                    st.subheader("Bubble Chart")
                    st.plotly_chart(
                        px.scatter(df, x=x_axis, y=y_axis, size=y_axis, color=y_axis, hover_name=df.columns[0]))

                # Heatmap
                elif plot_type == "Heatmap":
                    st.subheader("Heatmap")
                    st.plotly_chart(px.imshow(df.corr(), color_continuous_scale="Viridis"))

                # Violin Plot
                elif plot_type == "Violin Plot":
                    st.subheader("Violin Plot")
                    st.plotly_chart(px.violin(df, y=y_axis))

                # Treemap
                elif plot_type == "Treemap":
                    st.subheader("Treemap")
                    st.plotly_chart(px.treemap(df, path=[x_axis], values=y_axis))

                # Funnel Chart
                elif plot_type == "Funnel Chart":
                    st.subheader("Funnel Chart")
                    st.plotly_chart(px.funnel(df, x=x_axis, y=y_axis))

                # Radar Chart
                elif plot_type == "Radar Chart":
                    st.subheader("Radar Chart")
                    st.plotly_chart(px.line_polar(df, r=y_axis, theta=x_axis, line_close=True))

                # Sunburst Chart
                elif plot_type == "Sunburst Chart":
                    st.subheader("Sunburst Chart")
                    st.plotly_chart(px.sunburst(df, path=[x_axis, y_axis], values=y_axis))

                # Density Plot
                elif plot_type == "Density Plot":
                    st.subheader("Density Plot")
                    st.plotly_chart(px.density_contour(df, x=x_axis, y=y_axis))

                # 3D Scatter Plot
                elif plot_type == "3D Scatter Plot":
                    st.subheader("3D Scatter Plot")
                    z_axis = st.selectbox("Select Z-Axis", df.columns)
                    fig = go.Figure(data=[go.Scatter3d(
                        x=df[x_axis],
                        y=df[y_axis],
                        z=df[z_axis],
                        mode='markers',
                        marker=dict(size=5, color=df[y_axis], colorscale='Viridis')
                    )])
                    st.plotly_chart(fig)

                # 3D Surface Plot
                elif plot_type == "3D Surface Plot":
                    st.subheader("3D Surface Plot")
                    z_axis = st.selectbox("Select Z-Axis", df.columns)
                    fig = go.Figure(data=[go.Surface(
                        z=df[[x_axis, y_axis]].values,
                        colorscale='Viridis'
                    )])
                    fig.update_layout(title="3D Surface Plot", autosize=True)
                    st.plotly_chart(fig)


if __name__ == "__main__":
    main()
