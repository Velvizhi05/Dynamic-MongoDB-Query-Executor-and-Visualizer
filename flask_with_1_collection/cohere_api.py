import os
import ast
from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient
import pandas as pd
import cohere
import plotly.express as px
import plotly.graph_objects as go

# Set up Cohere API key
os.environ["COHERE_API_KEY"] = "Your api key"
cohere_client = cohere.Client(os.environ["COHERE_API_KEY"])

# MongoDB connection
db_host = "localhost"
db_port = 27017
db_name = "admin"
collection_name = "user_cln"
client = MongoClient(f"mongodb://{db_host}:{db_port}/")
db = client[db_name]

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Function to generate MongoDB query using Cohere
def generate_mongo_query_from_prompt(question: str) -> dict:
    """
    Use Cohere to generate a MongoDB query based on the user's question in dictionary format.
    """
    response = cohere_client.generate(
        model="command-xlarge-nightly",
        prompt=f"Generate a MongoDB query in Python dictionary format to answer this question: '{question}'.\n"
               "Respond only with a Python dictionary or list (for aggregation). Do not include any explanations or additional text.",
        max_tokens=200,
        temperature=0,
    )

    try:
        query = ast.literal_eval(response.generations[0].text.strip())
        if isinstance(query, dict) or isinstance(query, list):
            return query
    except Exception as e:
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
            return pd.DataFrame()

    except Exception as e:
        return pd.DataFrame()

# Function to generate the plot based on selected plot type
def generate_plot(df, plot_type, x_axis, y_axis):
    """
    Function to generate the plot based on user selection.
    """
    if plot_type == "1D":
        # Return only the dataframe for 1D case
        return df

    elif plot_type == "Bar Chart":
        return px.bar(df, x=x_axis, y=y_axis)

    elif plot_type == "Line Chart":
        return px.line(df, x=x_axis, y=y_axis)

    elif plot_type == "Scatter Plot":
        return px.scatter(df, x=x_axis, y=y_axis)

    elif plot_type == "Histogram":
        return px.histogram(df, x=x_axis)

    elif plot_type == "Pie Chart":
        return px.pie(df, names=x_axis, values=y_axis)

    elif plot_type == "Area Chart":
        return px.area(df, x=x_axis, y=y_axis)

    elif plot_type == "Box Plot":
        return px.box(df, x=x_axis, y=y_axis)

    elif plot_type == "Bubble Chart":
        return px.scatter(df, x=x_axis, y=y_axis, size=y_axis, color=y_axis)

    elif plot_type == "Heatmap":
        return px.imshow(df.corr(), color_continuous_scale="Viridis")

    elif plot_type == "Violin Plot":
        return px.violin(df, y=y_axis)

    elif plot_type == "Treemap":
        return px.treemap(df, path=[x_axis], values=y_axis)

    elif plot_type == "Funnel Chart":
        return px.funnel(df, x=x_axis, y=y_axis)

    elif plot_type == "Radar Chart":
        return px.line_polar(df, r=y_axis, theta=x_axis, line_close=True)

    elif plot_type == "Sunburst Chart":
        return px.sunburst(df, path=[x_axis, y_axis], values=y_axis)

    elif plot_type == "Density Plot":
        return px.density_contour(df, x=x_axis, y=y_axis)

    elif plot_type == "3D Scatter Plot":
        z_axis = request.form.get("z_axis")
        fig = go.Figure(data=[go.Scatter3d(
            x=df[x_axis],
            y=df[y_axis],
            z=df[z_axis],
            mode='markers',
            marker=dict(size=5, color=df[y_axis], colorscale='Viridis')
        )])
        return fig

    elif plot_type == "3D Surface Plot":
        z_axis = request.form.get("z_axis")
        fig = go.Figure(data=[go.Surface(
            z=df[[x_axis, y_axis]].values,
            colorscale='Viridis'
        )])
        fig.update_layout(title="3D Surface Plot", autosize=True)
        return fig

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the user input
        user_prompt = request.form.get("question")
        plot_type = request.form.get("plot_type")
        x_axis = request.form.get("x_axis")
        y_axis = request.form.get("y_axis")

        if user_prompt:
            # Generate MongoDB query from prompt
            query = generate_mongo_query_from_prompt(user_prompt)

            if query:
                df = execute_and_convert_to_dataframe(query)

                if not df.empty:
                    # Store inputs in session for subsequent requests
                    session["query"] = query
                    session["x_axis"] = x_axis
                    session["y_axis"] = y_axis
                    session["plot_type"] = plot_type

                    # Check for "1D" plot type and render only the dataframe
                    if plot_type == "1D":
                        return render_template("index.html", df=df.to_html(classes='table table-striped'))

                    # Generate the plot
                    fig = generate_plot(df, plot_type, x_axis, y_axis)
                    plot_html = fig.to_html(full_html=False)
                    return render_template("index.html", plot_html=plot_html, df=df.to_html(classes='table table-striped'))

        elif "query" in session:
            # If the user doesn't enter a prompt but wants to modify the plot
            query = session.get("query")
            x_axis = request.form.get("x_axis", session.get("x_axis"))
            y_axis = request.form.get("y_axis", session.get("y_axis"))
            plot_type = request.form.get("plot_type", session.get("plot_type"))

            df = execute_and_convert_to_dataframe(query)

            if not df.empty:
                # Update session with new inputs
                session["x_axis"] = x_axis
                session["y_axis"] = y_axis
                session["plot_type"] = plot_type

                # Check for "1D" plot type and render only the dataframe
                if plot_type == "1D":
                    return render_template("index.html", df=df.to_html(classes='table table-striped'))

                # Generate the updated plot
                fig = generate_plot(df, plot_type, x_axis, y_axis)
                plot_html = fig.to_html(full_html=False)
                return render_template("index.html", plot_html=plot_html, df=df.to_html(classes='table table-striped'))

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
