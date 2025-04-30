css = '''
<style>
/* Custom background color for the main content area */
.stApp {
    background-color: #3C2A21;
}

/* Custom styles for the sidebar */
.css-1d391kg, .css-163ttbj, section[data-testid="stSidebar"] {
    background-color: #2D2016;
}

/* Custom styles for input fields */
.stTextInput > div > div > input {
    background-color: #5D4037;
    color: #FFF8DC;
    border-color: #8D6E63;
}

/* Custom styles for buttons */
.stButton button {
    background-color: #8D6E63;
    color: #FFF8DC;
    border-color: #D2B48C;
}

.stButton button:hover {
    background-color: #D2B48C;
    color: #2D2016;
}

/* File uploader styling */
.stFileUploader > div:first-child {
    background-color: #5D4037;
    border-color: #8D6E63;
    color: #FFF8DC;
}

.stFileUploader > div:first-child:hover {
    background-color: #6D5047;
    border-color: #D2B48C;
}

.stFileUploader > div:last-child {
    background-color: #2D2016;
    color: #FFF8DC;
}

/* Success message styling */
.stAlert {
    background-color: rgba(93, 64, 55, 0.4);
    color: #FFF8DC;
}

.stSuccess {
    color: #D2B48C;
}

/* Custom success message in sidebar */
.pdf-success {
    background-color: rgba(141, 110, 99, 0.7);
    color: #FFF8DC;
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
    text-align: center;
    border-left: 4px solid #D2B48C;
}

/* Message styling */
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #5D4037
}
.chat-message.bot {
    background-color: #8D6E63
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #FFF8DC;
}
.timestamp {
  font-size: 12px;
  color: #D2B48C;
  text-align: right;
  margin-top: 5px;
  font-style: italic;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">
        {{MSG}}
        <div class="timestamp">{{TIME}}</div>
    </div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.ibb.co/rdZC7LZ/Photo-logo-1.png">
    </div>    
    <div class="message">
        {{MSG}}
        <div class="timestamp">{{TIME}}</div>
    </div>
</div>
'''

pdf_success_template = '''
<div class="pdf-success">
    <div style="font-size:24px; margin-bottom:5px">✅</div>
    <div>PDF berhasil diproses!</div>
    <div style="font-size:12px; margin-top:5px; opacity:0.8">{{TIME}}</div>
</div>
'''
