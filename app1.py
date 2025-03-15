from flask import Flask, request, render_template_string, jsonify
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import f
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# HTML Template
rawhtml = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Two-Way ANOVA Calculator</title>
    <style>
        /* General Styles */
        body {
            font-family: 'Poppins', sans-serif;
            background: #1a1a2e;
            color: #e0e0e0;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            background: #222436;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 153, 255, 0.4);
            width: 90%;
            max-width: 600px;
        }

        .title{
            text-align: center;
        }

        h1 {
            font-size: 24px;
            color: #00aaff;
            margin-bottom: 15px;
        }

        label {
            font-weight: bold;
            display: block;
            margin: 10px 0 5px;
            text-align: left;
        }

        input[type="file"], input[type="text"] {
            width: 96%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #00aaff;
            border-radius: 5px;
            font-size: 14px;
            background: #1e1e2e;
            color: #fff;
        }

        button {
            width: 100%;
            padding: 12px;
            background: #00aaff;
            color: #fff;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }

        button:hover {
            background: #0088cc;
        }

        .result-container {
            background: #121826;
            padding: 20px;
            margin-top: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 153, 255, 0.3);
            display: none; /* Initially hidden */
        }

        .result-container h2 {
            color: #00aaff;
            margin-bottom: 15px;
        }

        .result-container p {
            font-size: 14px;
            margin: 8px 0;
            color: #e0e0e0;
        }

        .result-container p strong {
            color: #00ddff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">Two-Way ANOVA Calculator</h1>
        <form id="anovaForm" method="POST" enctype="multipart/form-data">
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

        <div id="resultContainer" class="result-container">
            <h2 class="title">Two-Way ANOVA Results</h2>
            <div id="results"></div>
        </div>
    </div>

    <script>
        document.getElementById('anovaForm').addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent form submission

            var formData = new FormData(this); // Get form data

            fetch('/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Update the results section
                document.getElementById('results').innerHTML = `
                    <h3 class="title">Results</h3>
                    <p><strong>SS Rows (Factor 1):</strong> ${data['SS Rows (Factor 1)'].toFixed(4)}</p>
                    <p><strong>SS Columns (Factor 2):</strong> ${data['SS Columns (Factor 2)'].toFixed(4)}</p>
                    <p><strong>SS Interaction:</strong> ${data['SS Interaction'].toFixed(4)}</p>
                    <p><strong>SS Within:</strong> ${data['SS Within'].toFixed(4)}</p>
                    <p><strong>SS Total:</strong> ${data['SS Total'].toFixed(4)}</p>
                    <p><strong>df Rows (Factor 1):</strong> ${data['df Rows (Factor 1)']}</p>
                    <p><strong>df Columns (Factor 2):</strong> ${data['df Columns (Factor 2)']}</p>
                    <p><strong>df Interaction:</strong> ${data['df Interaction']}</p>
                    <p><strong>df Within:</strong> ${data['df Within']}</p>
                    <p><strong>df Total:</strong> ${data['df Total']}</p>
                    <p><strong>MS Rows (Factor 1):</strong> ${data['MS Rows (Factor 1)'].toFixed(4)}</p>
                    <p><strong>MS Columns (Factor 2):</strong> ${data['MS Columns (Factor 2)'].toFixed(4)}</p>
                    <p><strong>MS Interaction:</strong> ${data['MS Interaction'].toFixed(4)}</p>
                    <p><strong>MS Within:</strong> ${data['MS Within'].toFixed(4)}</p>
                    <p><strong>F-statistic Rows (Factor 1):</strong> ${data['F-statistic Rows (Factor 1)'].toFixed(4)}</p>
                    <p><strong>F-statistic Columns (Factor 2):</strong> ${data['F-statistic Columns (Factor 2)'].toFixed(4)}</p>
                    <p><strong>F-statistic Interaction:</strong> ${data['F-statistic Interaction'].toFixed(4)}</p>
                    <p><strong>P-value Rows (Factor 1):</strong> ${data['P-value Rows (Factor 1)'].toFixed(10)}</p>
                    <p><strong>P-value Columns (Factor 2):</strong> ${data['P-value Columns (Factor 2)'].toFixed(10)}</p>
                    <p><strong>P-value Interaction:</strong> ${data['P-value Interaction'].toFixed(10)}</p>
                    <p><strong>F-crit Rows (Factor 1):</strong> ${data['F-crit Rows (Factor 1)'].toFixed(4)}</p>
                    <p><strong>F-crit Columns (Factor 2):</strong> ${data['F-crit Columns (Factor 2)'].toFixed(4)}</p>
                    <p><strong>F-crit Interaction:</strong> ${data['F-crit Interaction'].toFixed(4)}</p>

                    <h3 class="title">Analysis of Results</h3>

                    <h4>Effect of Factor 1 on the Dependent Variable</h4>
                    ${data['P-value Rows (Factor 1)'] < 0.05 ? 
                        `<p><strong>Statistically Significant:</strong> Yes (p = ${data['P-value Rows (Factor 1)'].toFixed(4)})</p>
                        <p>Changes in Factor 1 lead to meaningful variations in the outcome. We reject the null hypothesis that Factor 1 has no effect.</p>` :
                        `<p><strong>Statistically Significant:</strong> No (p = ${data['P-value Rows (Factor 1)'].toFixed(4)})</p>
                        <p>Any observed variations due to Factor 1 may be due to random chance. We fail to reject the null hypothesis.</p>`}

                    <h4>Effect of Factor 2 on the Dependent Variable</h4>
                    ${data['P-value Columns (Factor 2)'] < 0.05 ? 
                        `<p><strong>Statistically Significant:</strong> Yes (p = ${data['P-value Columns (Factor 2)'].toFixed(4)})</p>
                        <p>Variations in Factor 2 contribute significantly to differences in the outcome. The null hypothesis is rejected.</p>` :
                        `<p><strong>Statistically Significant:</strong> No (p = ${data['P-value Columns (Factor 2)'].toFixed(4)})</p>
                        <p>Factor 2 does not play a crucial role in influencing the outcome. We fail to reject the null hypothesis.</p>`}

                    <h4>Interaction Between Factor 1 and Factor 2</h4>
                    ${data['P-value Interaction'] < 0.05 ? 
                        `<p><strong>Statistically Significant:</strong> Yes (p = ${data['P-value Interaction'].toFixed(4)})</p>
                        <p>The effect of one factor depends on the level of the other factor. The influence of Factor 1 on the dependent variable is not consistent across different levels of Factor 2, and vice versa. This suggests that the two factors interact in a way that impacts the outcome beyond their individual effects.</p>` :
                        `<p><strong>Statistically Significant:</strong> No (p = ${data['P-value Interaction'].toFixed(4)})</p>
                        <p>The two factors act independently. The effect of one factor does not change depending on the level of the other factor.</p>`}

                    <h4>Overall Implications</h4>
                    <p>The analysis reveals that:</p>
                    <ul>
                        <li>${data['P-value Rows (Factor 1)'] < 0.05 ? 'Factor 1 has a significant effect on the outcome.' : 'Factor 1 does not have a significant effect on the outcome.'}</li>
                        <li>${data['P-value Columns (Factor 2)'] < 0.05 ? 'Factor 2 has a significant effect on the outcome.' : 'Factor 2 does not have a significant effect on the outcome.'}</li>
                        <li>${data['P-value Interaction'] < 0.05 ? 'There is a significant interaction between Factor 1 and Factor 2, indicating that their combined effect is more complex than their individual contributions.' : 'There is no significant interaction between Factor 1 and Factor 2, meaning they act independently.'}</li>
                    </ul>
                `;

                // Show the result container
                document.getElementById('resultContainer').style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    </script>
</body>
</html>
"""

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
                return jsonify({"error": "One or more specified columns do not exist in the CSV file."})

            # Perform two-way ANOVA calculations
            result, p_factor1, p_factor2, p_interaction = two_way_anova_with_replication(df, factor1, factor2, dependent_var)

            # Delete the file after processing
            os.remove(filepath)

            return jsonify(result)

        else:
            return jsonify({"error": "Please upload a valid CSV file."})

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
