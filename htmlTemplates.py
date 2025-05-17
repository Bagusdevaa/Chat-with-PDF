css = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Custom background color for the main content area with gradient */
.stApp {
    background: linear-gradient(135deg, #3C2A21 0%, #1a1410 100%);
    font-family: 'Poppins', sans-serif;
}

/* Custom styles for the sidebar with modern look */
.css-1d391kg, .css-163ttbj, section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2D2016 0%, #1a1410 100%);
    border-right: 1px solid rgba(210, 180, 140, 0.2);
}

/* Improved header styling */
h1, h2, h3 {
    font-family: 'Poppins', sans-serif;
    letter-spacing: 0.5px;
}

/* Custom styles for input fields with animations */
.stTextInput > div > div > input {
    background-color: rgba(93, 64, 55, 0.7);
    color: #FFF8DC;
    border: 1px solid #8D6E63;
    border-radius: 8px;
    padding: 12px 16px;
    transition: all 0.3s ease;
    font-size: 16px;
}

.stTextInput > div > div > input:focus {
    border-color: #D2B48C;
    box-shadow: 0 0 0 2px rgba(210, 180, 140, 0.3);
    background-color: rgba(93, 64, 55, 0.9);
}

/* Custom styles for buttons with modern look and animations */
.stButton button {
    background: linear-gradient(to right, #8D6E63, #A67F5D);
    color: #FFF8DC;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 500;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.stButton button:hover {
    background: linear-gradient(to right, #A67F5D, #D2B48C);
    color: #2D2016;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.stButton button:active {
    transform: translateY(0);
    box-shadow: 0 2px 3px rgba(0, 0, 0, 0.2);
}

/* Improved file uploader styling */
.stFileUploader > div:first-child {
    background-color: rgba(93, 64, 55, 0.7);
    border: 1px dashed #8D6E63;
    border-radius: 8px;
    color: #FFF8DC;
    transition: all 0.3s ease;
    padding: 16px;
}

.stFileUploader > div:first-child:hover {
    background-color: rgba(109, 80, 71, 0.8);
    border-color: #D2B48C;
    box-shadow: 0 0 10px rgba(210, 180, 140, 0.3);
}

.stFileUploader > div:last-child {
    background-color: rgba(45, 32, 22, 0.7);
    color: #FFF8DC;
    border-radius: 8px;
    margin-top: 8px;
    padding: 12px;
}

/* Success message styling with animations */
.stAlert {
    background-color: rgba(93, 64, 55, 0.4);
    color: #FFF8DC;
    border-radius: 8px;
    border-left: 4px solid #8D6E63;
    padding: 12px 16px;
    animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.stSuccess {
    color: #D2B48C;
    font-weight: 500;
}

/* Enhanced success message in sidebar */
.pdf-success {
    background: linear-gradient(to right, rgba(141, 110, 99, 0.7), rgba(166, 127, 93, 0.7));
    color: #FFF8DC;
    padding: 16px;
    border-radius: 8px;
    margin-top: 16px;
    text-align: center;
    border-left: 4px solid #D2B48C;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    animation: slideIn 0.5s ease-in-out;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Enhanced message styling with shadows and animations */
.chat-message {
    padding: 1.5rem; 
    border-radius: 12px; 
    margin-bottom: 1.5rem; 
    display: flex;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
    animation: fadeIn 0.5s ease-in-out;
    transition: all 0.3s ease;
    overflow: hidden;
}

.chat-message:hover {
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    transform: translateY(-2px);
}

.chat-message.user {
    background: linear-gradient(135deg, #5D4037 0%, #4A332D 100%);
    margin-right: 24px;
}

.chat-message.bot {
    background: linear-gradient(135deg, #8D6E63 0%, #7D5E53 100%);
    margin-left: 24px;
}

.chat-message .avatar {
    width: 15%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.chat-message .avatar img {
    max-width: 60px;
    max-height: 60px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
    border: 2px solid #D2B48C;
}

.chat-message .message {
    width: 85%;
    padding: 0 1.5rem;
    color: #FFF8DC;
    font-size: 16px;
    line-height: 1.6;
}

.chat-message .message p {
    margin-bottom: 10px;
}

.timestamp {
    font-size: 12px;
    color: #D2B48C;
    text-align: right;
    margin-top: 8px;
    font-style: italic;
    opacity: 0.8;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(45, 32, 22, 0.6);
}

::-webkit-scrollbar-thumb {
    background: #8D6E63;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #A67F5D;
}

/* Loading spinner customization */
.stSpinner > div {
    border-color: #D2B48C transparent transparent transparent !important;
}

/* Better responsive design for mobile */
@media (max-width: 768px) {
    .chat-message {
        flex-direction: column;
    }
    
    .chat-message .avatar {
        width: 100%;
        margin-bottom: 10px;
    }
    
    .chat-message .message {
        width: 100%;
        padding: 0;
    }
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png">
    </div>
    <div class="message">
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="font-weight: 600; color: #D2B48C; margin-right: 8px;">AI Assistant</div>
            <div style="height: 8px; width: 8px; background-color: #4CAF50; border-radius: 50%;"></div>
        </div>
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
        <div style="font-weight: 600; color: #D2B48C; margin-bottom: 5px;">You</div>
        {{MSG}}
        <div class="timestamp">{{TIME}}</div>
    </div>
</div>
'''

pdf_success_template = '''
<div class="pdf-success">
    <div style="font-size:32px; margin-bottom:8px">✅</div>
    <div style="font-weight: 600; font-size: 18px; margin-bottom: 5px;">PDF Berhasil Diproses!</div>
    <div style="font-size:14px; margin-top:8px; opacity:0.8">Waktu: {{TIME}}</div>
</div>
'''
