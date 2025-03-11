from flask import Flask, request, render_template_string
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import f
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

rawhtml = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Two-Way ANOVA Calculator</title>
    <style>
        /* Dark Theme Styles */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212; /* Dark background */
            color: #e0e0e0; /* Light text */
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow-y: auto; /* Enable vertical scrolling */
        }

        .container {
            margin-top: 50px;
            background-color: #1e1e1e; /* Slightly lighter dark background */
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            width: 450px;
            text-align: center;
            animation: fadeIn 0.5s ease-in-out;
            max-height: 95vh; /* Ensure it doesn't take up more than 95% of the viewport */
            overflow-y: auto; /* Enable scrolling inside the container if needed */
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        h1 {
            margin-bottom: 20px;
            font-size: 24px;
            color: #64b5f6; /* Light blue for headings */
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #bdbdbd;
            text-align: left;
        }

        input[type="file"], input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #424242; /* Darker border */
            border-radius: 6px;
            font-size: 14px;
            background-color: #303030; /* Darker input background */
            color: #e0e0e0;
            transition: border-color 0.3s ease;
        }

        input[type="file"]:focus, input[type="text"]:focus {
            border-color: #64b5f6;
            outline: none;
        }

        button {
            width: 100%;
            padding: 12px;
            background-color: #64b5f6;
            color: #121212;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #42a5f5;
        }

        #result {
            text-align: left;
            background-color: #212121; /* Slightly darker result background */
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.5s ease-in-out;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        #result h2 {
            margin-bottom: 15px;
            font-size: 20px;
            color: #64b5f6;
        }

        #result h3 {
            margin-bottom: 10px;
            font-size: 18px;
            color: #bdbdbd;
        }

        #result p {
            margin: 8px 0;
            font-size: 14px;
            color: #e0e0e0;
        }

        #result p strong {
            color: #bdbdbd;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Two-Way ANOVA Calculator</h1>
        {% if not result %}
            <form method="POST" enctype="multipart/form-data">
                <label for="csvFile">Upload CSV File:</label>
                <input type="file" id="csvFile" name="csvFile" accept=".csv" required>
                
                <label for="factor1">Factor 1 Column:</label>
                <input type="text" id="factor1" name="factor1" placeholder="Enter factor 1 column name" required>
                
                <label for="factor2">Factor 2 Column:</label>
                <input type="text" id="factor2" name="factor2" placeholder="Enter factor 2 column name" required>
                
                <label for="dependent_var">Dependent Variable Column:</label>
                <input type="text" id="dependent_var" name="dependent_var" placeholder="Enter dependent variable column name" required>
                
                <button type="submit">Calculate Two-Way ANOVA</button>
            </form>
        {% endif %}

        {% if result %}
            <div id="result">
                <h2>Two-Way ANOVA Results</h2>
                
                <h3>Results</h3>
                <p><strong>SS Rows (Factor 1):</strong> {{ result['SS Rows (Factor 1)'] | round(4) }}</p>
                <p><strong>SS Columns (Factor 2):</strong> {{ result['SS Columns (Factor 2)'] | round(4) }}</p>
                <p><strong>SS Interaction:</strong> {{ result['SS Interaction'] | round(4) }}</p>
                <p><strong>SS Within:</strong> {{ result['SS Within'] | round(4) }}</p>
                <p><strong>SS Total:</strong> {{ result['SS Total'] | round(4) }}</p>
                <p><strong>df Rows (Factor 1):</strong> {{ result['df Rows (Factor 1)'] }}</p>
                <p><strong>df Columns (Factor 2):</strong> {{ result['df Columns (Factor 2)'] }}</p>
                <p><strong>df Interaction:</strong> {{ result['df Interaction'] }}</p>
                <p><strong>df Within:</strong> {{ result['df Within'] }}</p>
                <p><strong>df Total:</strong> {{ result['df Total'] }}</p>
                <p><strong>MS Rows (Factor 1):</strong> {{ result['MS Rows (Factor 1)'] | round(4) }}</p>
                <p><strong>MS Columns (Factor 2):</strong> {{ result['MS Columns (Factor 2)'] | round(4) }}</p>
                <p><strong>MS Interaction:</strong> {{ result['MS Interaction'] | round(4) }}</p>
                <p><strong>MS Within:</strong> {{ result['MS Within'] | round(4) }}</p>
                <p><strong>F-statistic Rows (Factor 1):</strong> {{ result['F-statistic Rows (Factor 1)'] | round(4) }}</p>
                <p><strong>F-statistic Columns (Factor 2):</strong> {{ result['F-statistic Columns (Factor 2)'] | round(4) }}</p>
                <p><strong>F-statistic Interaction:</strong> {{ result['F-statistic Interaction'] | round(4) }}</p>
                <p><strong>P-value Rows (Factor 1):</strong> {{ result['P-value Rows (Factor 1)'] | round(10) }}</p>
                <p><strong>P-value Columns (Factor 2):</strong> {{ result['P-value Columns (Factor 2)'] | round(10) }}</p>
                <p><strong>P-value Interaction:</strong> {{ result['P-value Interaction'] | round(10) }}</p>
                <p><strong>F-crit Rows (Factor 1):</strong> {{ result['F-crit Rows (Factor 1)'] | round(4) }}</p>
                <p><strong>F-crit Columns (Factor 2):</strong> {{ result['F-crit Columns (Factor 2)'] | round(4) }}</p>
                <p><strong>F-crit Interaction:</strong> {{ result['F-crit Interaction'] | round(4) }}</p>

                <h3>Conclusion</h3>
                {% if result['P-value Rows (Factor 1)'] < 0.05 %}
                    <p><strong>Conclusion:</strong> Factor 1 has a significant effect (p = {{ result['P-value Rows (Factor 1)'] | round(4) }}).</p>
                {% else %}
                    <p><strong>Conclusion:</strong> Factor 1 does not have a significant effect (p = {{ result['P-value Rows (Factor 1)'] | round(4) }}).</p>
                {% endif %}

                {% if result['P-value Columns (Factor 2)'] < 0.05 %}
                    <p><strong>Conclusion:</strong> Factor 2 has a significant effect (p = {{ result['P-value Columns (Factor 2)'] | round(4) }}).</p>
                {% else %}
                    <p><strong>Conclusion:</strong> Factor 2 does not have a significant effect (p = {{ result['P-value Columns (Factor 2)'] | round(4) }}).</p>
                {% endif %}

                {% if result['P-value Interaction'] < 0.05 %}
                    <p><strong>Conclusion:</strong> The interaction between factors is significant (p = {{ result['P-value Interaction'] | round(4) }}).</p>
                {% else %}
                    <p><strong>Conclusion:</strong> The interaction between factors is not significant (p = {{ result['P-value Interaction'] | round(4) }}).</p>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['csvFile']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Get the factor and dependent variable columns
            factor1 = request.form['factor1']
            factor2 = request.form['factor2']
            dependent_var = request.form['dependent_var']

            # Read the CSV file
            df = pd.read_csv(filepath)

            df = df.rename(columns={
                f"{factor1}": "factor1",
                f"{factor2}": "factor2",
                f"{dependent_var}": "dependent_var"
            })

            factor1 = "factor1"
            factor2 = "factor2"
            dependent_var = "dependent_var"

            # Check if columns exist in the CSV
            if factor1 not in df.columns or factor2 not in df.columns or dependent_var not in df.columns:
                return "Error: One or more specified columns do not exist in the CSV file."

            # Perform two-way ANOVA calculations
            result, p_factor1, p_factor2, p_interaction = two_way_anova_with_replication(df, factor1, factor2, dependent_var)

            # Delete the file after processing
            os.remove(filepath)

            return render_template_string(rawhtml, result=result)

        else:
            return "Error: Please upload a valid CSV file."

    return render_template_string(rawhtml, result=None)

def two_way_anova_with_replication(df, factor1, factor2, dependent_var):
    model = ols(f'{dependent_var} ~ C({factor1}) * C({factor2})', data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    ss_factor1 = anova_table['sum_sq'][f'C({factor1})']
    ss_factor2 = anova_table['sum_sq'][f'C({factor2})']
    ss_interaction = anova_table['sum_sq'][f'C({factor1}):C({factor2})']
    ss_within = anova_table['sum_sq']['Residual']
    ss_total = ss_factor1 + ss_factor2 + ss_interaction + ss_within

    df_factor1 = anova_table['df'][f'C({factor1})']
    df_factor2 = anova_table['df'][f'C({factor2})']
    df_interaction = anova_table['df'][f'C({factor1}):C({factor2})']
    df_within = anova_table['df']['Residual']
    df_total = df_factor1 + df_factor2 + df_interaction + df_within

    ms_factor1 = ss_factor1 / df_factor1
    ms_factor2 = ss_factor2 / df_factor2
    ms_interaction = ss_interaction / df_interaction
    ms_within = ss_within / df_within

    f_factor1 = ms_factor1 / ms_within
    f_factor2 = ms_factor2 / ms_within
    f_interaction = ms_interaction / ms_within

    p_factor1 = anova_table['PR(>F)'][f'C({factor1})']
    p_factor2 = anova_table['PR(>F)'][f'C({factor2})']
    p_interaction = anova_table['PR(>F)'][f'C({factor1}):C({factor2})']

    alpha = 0.05
    f_crit_factor1 = f.ppf(1 - alpha, df_factor1, df_within)
    f_crit_factor2 = f.ppf(1 - alpha, df_factor2, df_within)
    f_crit_interaction = f.ppf(1 - alpha, df_interaction, df_within)

    results = {
        "SS Rows (Factor 1)": ss_factor1,
        "SS Columns (Factor 2)": ss_factor2,
        "SS Interaction": ss_interaction,
        "SS Within": ss_within,
        "SS Total": ss_total,
        "df Rows (Factor 1)": df_factor1,
        "df Columns (Factor 2)": df_factor2,
        "df Interaction": df_interaction,
        "df Within": df_within,
        "df Total": df_total,
        "MS Rows (Factor 1)": ms_factor1,
        "MS Columns (Factor 2)": ms_factor2,
        "MS Interaction": ms_interaction,
        "MS Within": ms_within,
        "F-statistic Rows (Factor 1)": f_factor1,
        "F-statistic Columns (Factor 2)": f_factor2,
        "F-statistic Interaction": f_interaction,
        "P-value Rows (Factor 1)": p_factor1,
        "P-value Columns (Factor 2)": p_factor2,
        "P-value Interaction": p_interaction,
        "F-crit Rows (Factor 1)": f_crit_factor1,
        "F-crit Columns (Factor 2)": f_crit_factor2,
        "F-crit Interaction": f_crit_interaction,
    }

    return results, p_factor1, p_factor2, p_interaction


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8003)
