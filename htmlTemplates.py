css = '''
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 10px;
    max-height: 60vh;
    overflow-y: auto;
    border-radius: 10px;
    background-color: #f9f9f9;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.chat-message {
    display: flex;
    padding: 1.5rem;
    border-radius: 0.8rem;
    margin-bottom: 10px;
    position: relative;
    animation: fadeIn 0.5s;
}

.chat-message.user {
    background-color: #2b313e;
    color: #fff;
    border-bottom-right-radius: 0;
    margin-left: 40px;
    margin-right: 10px;
}

.chat-message.bot {
    background-color: #475063;
    color: #fff;
    border-bottom-left-radius: 0;
    margin-right: 40px;
    margin-left: 10px;
}

.chat-message .avatar {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    object-fit: cover;
    position: absolute;
    top: -15px;
}

.chat-message.user .avatar {
    right: -15px;
    background-color: #2b313e;
    display: flex;
    align-items: center;
    justify-content: center;
}

.chat-message.bot .avatar {
    left: -15px;
    background-color: #475063;
    display: flex;
    align-items: center;
    justify-content: center;
}

.chat-message .message {
    width: 100%;
    padding: 0;
    color: #fff;
}

.chat-message .time {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.7);
    margin-top: 5px;
    text-align: right;
}

/* Animasi untuk pesan baru */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.stTextInput {
    position: sticky;
    bottom: 0;
    background-color: white;
    padding: 10px 0;
    z-index: 100;
}

/* Tombol process lebih menonjol */
.stButton button {
    width: 100%;
    background-color: #4CAF50 !important;
    color: white !important;
    font-weight: bold !important;
}

</style>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">👤</div>
    <div class="message">{{MSG}}</div>
    <div class="time">{{TIME}}</div>
</div>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">🤖</div>
    <div class="message">{{MSG}}</div>
    <div class="time">{{TIME}}</div>
</div>
'''