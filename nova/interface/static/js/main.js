// main.js - Script principal para Nova

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const messagesContainer = document.getElementById('messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');
    const voiceButton = document.getElementById('voice-btn');
    const voiceIndicator = document.getElementById('voice-indicator');
    const audioPlayer = document.getElementById('audio-player');
    
    // Ocultar el indicador de voz inicialmente
    voiceIndicator.style.display = 'none';
    
    // Intentar conectar primero a localhost, si falla, usar la IP alternativa
    let socket;
    let serverUrl = 'http://localhost:5000';
    const fallbackUrl = 'http://192.168.1.14:5000';
    
    // Función para conectar al socket
    function connectSocket(url) {
        try {
            console.log(`Intentando conectar a: ${url}`);
            socket = io(url);
            
            // Eventos del socket
            socket.on('connect', function() {
                console.log('Conectado al servidor');
                addSystemMessage('Conectado al servidor');
            });
            
            socket.on('connect_error', function(error) {
                console.error('Error de conexión:', error);
                
                // Si estamos usando localhost y hay error, intentar con la IP alternativa
                if (url === serverUrl && serverUrl === 'http://localhost:5000') {
                    console.log('Intentando conectar a la IP alternativa...');
                    serverUrl = fallbackUrl;
                    socket.close();
                    connectSocket(fallbackUrl);
                }
            });
            
            socket.on('status', function(data) {
                console.log('Estado:', data);
            });
            
            socket.on('nova_response', function(data) {
                addNovaMessage(data.response);
                
                // Reproducir audio si está disponible
                if (data.audio_url) {
                    audioPlayer.src = data.audio_url;
                    audioPlayer.play();
                }
            });
            
            socket.on('speech_detected', function(data) {
                userInput.value = data.text;
            });
            
            socket.on('disconnect', function() {
                console.log('Desconectado del servidor');
                addSystemMessage('Desconectado del servidor');
            });
            
            return true;
        } catch (error) {
            console.error('Error al crear la conexión:', error);
            return false;
        }
    }
    
    // Iniciar la conexión
    connectSocket(serverUrl);
    
    // Función para enviar mensaje
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Añadir mensaje del usuario a la interfaz
        addUserMessage(message);
        
        // Mostrar indicador de procesamiento
        addSystemMessage('Nova está pensando...');
        
        // Enviar mensaje al servidor
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Eliminar el mensaje de "pensando"
            const thinkingMessage = Array.from(messagesContainer.getElementsByClassName('message')).find(el => el.textContent === 'Nova está pensando...');
            if (thinkingMessage) {
                messagesContainer.removeChild(thinkingMessage);
            }
            
            // Añadir respuesta de Nova a la interfaz
            addNovaMessage(data.response);
            
            // Reproducir audio si está disponible
            if (data.audio_url) {
                audioPlayer.src = data.audio_url;
                audioPlayer.play();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addSystemMessage('Error al enviar el mensaje. Por favor, verifica tu conexión y vuelve a intentarlo.');
        });
        
        // Limpiar el campo de entrada
        userInput.value = '';
    }
    
    // Función para iniciar/detener la escucha de voz
    let isListening = false;
    function toggleVoiceListening() {
        if (isListening) {
            // Detener la escucha
            fetch('/api/stop_listening', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                console.log('Escucha detenida:', data);
                isListening = false;
                voiceIndicator.style.display = 'none';
                voiceButton.textContent = '🎤';
            })
            .catch(error => {
                console.error('Error al detener la escucha:', error);
            });
        } else {
            // Iniciar la escucha
            fetch('/api/start_listening', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                console.log('Escucha iniciada:', data);
                if (data.status === 'started') {
                    isListening = true;
                    voiceIndicator.style.display = 'block';
                    voiceButton.textContent = '⏹️';
                }
            })
            .catch(error => {
                console.error('Error al iniciar la escucha:', error);
                alert('Error: No se puede iniciar la escucha. Modelo no disponible. Por favor, verifica la configuración del sistema y vuelve a intentarlo.');
            });
        }
    }
    
    // Función para añadir mensaje del usuario a la interfaz
    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Función para añadir mensaje de Nova a la interfaz
    function addNovaMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message nova-message';
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Función para añadir mensaje del sistema a la interfaz
    function addSystemMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    
    voiceButton.addEventListener('click', toggleVoiceListening);
});