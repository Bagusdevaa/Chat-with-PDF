# filepath: PDFChat/src/htmlTemplates.py
css = """
<style>
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 20px;
}
.header {
    text-align: center;
    margin-bottom: 20px;
}
.user-message {
    background-color: #d1e7dd;
    border-radius: 5px;
    padding: 10px;
    margin: 5px 0;
}
.bot-message {
    background-color: #f8d7da;
    border-radius: 5px;
    padding: 10px;
    margin: 5px 0;
}
</style>
"""

bot_template = """
<div class="bot-message">
    {{MSG}}
</div>
"""

user_template = """
<div class="user-message">
    {{MSG}}
</div>
"""