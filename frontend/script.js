/* =========================================
   INQUISITORS AI ASSISTANT
   Frontend + FastAPI + SQLite Session Memory
========================================= */


/* =========================================
   CONFIGURATION
========================================= */

const USE_API = true;

const API_BASE_URL =
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:8000"
        : "";

const CHAT_API_URL =
    `${API_BASE_URL}/api/chat`;

const HISTORY_API_URL =
    `${API_BASE_URL}/api/history`;

const SESSION_STORAGE_KEY =
    "inquisitors_chat_session_id";


/* =========================================
   DOM ELEMENTS
========================================= */

const chatOverlay =
    document.getElementById("chat-overlay");

const chatMessages =
    document.getElementById("chat-messages");

const userInput =
    document.getElementById("user-input");

const voiceInputButton =
    document.getElementById("voice-input-btn");

const voiceStatus =
    document.getElementById("voice-status");

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

let speechRecognition = null;

let isListening = false;

let speechEnabled = true;


/* =========================================
   HISTORY STATE
========================================= */

/*
   IMPORTANT:

   This prevents SQLite history from being
   loaded repeatedly every time openChat()
   is called.
*/

let historyLoaded = false;


/* =========================================
   SESSION MANAGEMENT
========================================= */

function createSessionId() {

    return (
        "web-" +
        Date.now() +
        "-" +
        Math.random()
            .toString(36)
            .substring(2, 10)
    );

}


/* =========================================
   GET CURRENT SESSION ID
========================================= */

function getSessionId() {

    let sessionId =
        localStorage.getItem(
            SESSION_STORAGE_KEY
        );


    if (!sessionId) {

        sessionId =
            createSessionId();

        localStorage.setItem(
            SESSION_STORAGE_KEY,
            sessionId
        );

    }


    return sessionId;

}


/* =========================================
   CURRENT SESSION
========================================= */

let SESSION_ID =
    getSessionId();


/* =========================================
   VOICE FEATURES
========================================= */

function setVoiceStatus(message) {

    if (voiceStatus) {

        voiceStatus.textContent = message || "";

    }

}


function initializeVoiceInput() {

    if (!SpeechRecognition) {

        if (voiceInputButton) {

            voiceInputButton.disabled = true;
            voiceInputButton.title = "Voice input is not supported in this browser";

        }

        setVoiceStatus("Voice input is unavailable in this browser.");

        return;

    }

    speechRecognition = new SpeechRecognition();
    speechRecognition.lang = "en-US";
    speechRecognition.interimResults = true;
    speechRecognition.continuous = false;

    speechRecognition.onstart = function () {

        isListening = true;

        if (voiceInputButton) {

            voiceInputButton.classList.add("listening");
            voiceInputButton.textContent = "⏹";

        }

        setVoiceStatus("Listening... speak your question.");

    };

    speechRecognition.onresult = function (event) {

        let transcript = "";

        for (let index = event.resultIndex; index < event.results.length; index += 1) {

            transcript += event.results[index][0].transcript;

        }

        if (userInput) {

            userInput.value = transcript.trim();

        }

    };

    speechRecognition.onerror = function (event) {

        setVoiceStatus(
            event.error === "not-allowed"
                ? "Microphone permission was denied."
                : "Voice input could not be completed."
        );

    };

    speechRecognition.onend = function () {

        isListening = false;

        if (voiceInputButton) {

            voiceInputButton.classList.remove("listening");
            voiceInputButton.textContent = "🎙";

        }

        if (userInput && userInput.value.trim()) {

            setVoiceStatus("Voice captured. Press send to ask.");

        } else {

            setVoiceStatus("");

        }

    };

}


function toggleVoiceInput() {

    if (!speechRecognition) {

        setVoiceStatus("Voice input is unavailable in this browser.");
        return;

    }

    if (isListening) {

        speechRecognition.stop();

    } else {

        speechRecognition.start();

    }

}


function toggleSpeechOutput(button, message) {

    if (!window.speechSynthesis) {

        setVoiceStatus("Voice output is unavailable in this browser.");
        return;

    }

    if (window.speechSynthesis.speaking) {

        window.speechSynthesis.cancel();
        button.textContent = "🔊";
        return;

    }

    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = "en-US";
    utterance.rate = 0.95;
    utterance.onend = function () {
        button.textContent = "🔊";
    };

    button.textContent = "⏹";
    window.speechSynthesis.speak(utterance);

}


initializeVoiceInput();


/* =========================================
   OPEN CHAT
========================================= */

function openChat() {

    if (!chatOverlay) {

        console.error(
            "Chat overlay element not found."
        );

        return;

    }


    chatOverlay.classList.add(
        "active"
    );


    setTimeout(() => {

        if (userInput) {

            userInput.focus();

        }

    }, 200);


    /*
       Load SQLite history only once.
    */

    loadChatHistory();

}


/* =========================================
   CLOSE CHAT
========================================= */

function closeChat() {

    if (!chatOverlay) {

        return;

    }


    chatOverlay.classList.remove(
        "active"
    );

}


/* =========================================
   CLOSE CHAT WHEN CLICKING OUTSIDE
========================================= */

if (chatOverlay) {

    chatOverlay.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                chatOverlay
            ) {

                closeChat();

            }

        }
    );

}


/* =========================================
   ENTER KEY
========================================= */

if (userInput) {

    userInput.addEventListener(
        "keydown",
        function (event) {

            /*
               Enter sends message.

               Shift + Enter can be used
               for a new line.
            */

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );

}


/* =========================================
   SEND MESSAGE
========================================= */

async function sendMessage() {

    if (!userInput) {

        return;

    }


    const message =
        userInput.value.trim();


    /*
       Do nothing for empty messages.
    */

    if (!message) {

        return;

    }


    /*
       Display user message immediately.
    */

    addUserMessage(
        message
    );


    /*
       Clear input.
    */

    userInput.value = "";


    /*
       Disable input while
       backend is processing.
    */

    setInputState(
        false
    );


    /*
       Show loading message.
    */

    const loadingId =
        addBotMessage(
            "Thinking..."
        );


    try {

        let data;


        /* =====================================
           DEMO MODE
        ===================================== */

        if (!USE_API) {

            const answer =
                await getDemoResponse(
                    message
                );


            data = {

                answer: answer,

                sources: [],

                session_id:
                    SESSION_ID

            };

        }


        /* =====================================
           REAL FASTAPI BACKEND
        ===================================== */

        else {

            data =
                await getAPIResponse(
                    message
                );

        }


        /*
           Remove Thinking...
        */

        removeMessage(
            loadingId
        );


        /*
           Validate answer before displaying.
        */

        if (
            !data ||
            typeof data.answer !==
            "string" ||
            !data.answer.trim()
        ) {

            throw new Error(
                "Backend returned an empty answer."
            );

        }


        /*
           Display ONLY the answer returned
           by the backend.

           We do NOT display:
           - system prompt
           - RAG prompt
           - knowledge context
           - instructions
           - internal data
        */

        addBotMessage(
            data.answer
        );


        /*
           Update session ID if backend
           sends one.
        */

        if (
            data.session_id &&
            typeof data.session_id ===
            "string"
        ) {

            SESSION_ID =
                data.session_id.trim();


            localStorage.setItem(
                SESSION_STORAGE_KEY,
                SESSION_ID
            );

        }

    }

    catch (error) {

        console.error(
            "Chat error:",
            error
        );


        /*
           Remove Thinking...
        */

        removeMessage(
            loadingId
        );


        /*
           Show user-friendly error.
        */

        addBotMessage(
            "Sorry, I couldn't connect to the AI service. Please make sure the FastAPI backend is running."
        );

    }

    finally {

        /*
           Re-enable input.
        */

        setInputState(
            true
        );


        if (userInput) {

            userInput.focus();

        }

    }

}


/* =========================================
   GET RESPONSE FROM FASTAPI
========================================= */

async function getAPIResponse(
    message
) {

    const response =
        await fetch(
            CHAT_API_URL,
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json",

                    "Accept":
                        "application/json"

                },

                body:
                    JSON.stringify({

                        message:
                            message,

                        session_id:
                            SESSION_ID

                    })

            }
        );


    /*
       Check HTTP status.
    */

    if (!response.ok) {

        let errorMessage =
            `API Error ${response.status}`;


        try {

            const errorData =
                await response.json();


            if (
                errorData &&
                errorData.detail
            ) {

                errorMessage +=
                    `: ${errorData.detail}`;

            }

        }

        catch (jsonError) {

            console.warn(
                "Could not parse API error response.",
                jsonError
            );

        }


        throw new Error(
            errorMessage
        );

    }


    /*
       Parse JSON.
    */

    const data =
        await response.json();


    console.log(
        "Chat API response:",
        data
    );


    /*
       Validate backend response.

       Expected:

       {
           answer: "...",
           sources: [...],
           session_id: "..."
       }
    */

    if (
        !data ||
        typeof data !== "object"
    ) {

        throw new Error(
            "Backend returned invalid JSON."
        );

    }


    if (
        typeof data.answer !==
        "string"
    ) {

        throw new Error(
            "Backend response does not contain a valid answer."
        );

    }


    return data;

}


/* =========================================
   LOAD CHAT HISTORY
========================================= */

async function loadChatHistory() {

    /*
       IMPORTANT:

       Prevent repeated history loading.
    */

    if (historyLoaded) {

        return;

    }


    /*
       Mark as loaded immediately.

       This prevents multiple simultaneous
       openChat() calls from triggering
       multiple requests.
    */

    historyLoaded = true;


    try {

        const response =
            await fetch(
                `${HISTORY_API_URL}/${encodeURIComponent(SESSION_ID)}`
            );


        /*
           HTTP error.
        */

        if (!response.ok) {

            console.warn(
                "Could not load chat history:",
                response.status
            );

            return;

        }


        /*
           Parse JSON.
        */

        const data =
            await response.json();


        console.log(
            "SQLite history response:",
            data
        );


        /*
           Backend currently returns:

           {
               session_id: "...",
               messages: [...]
           }

           But we also support "history"
           for compatibility.
        */

        const history =
            data.messages ||
            data.history ||
            [];


        /*
           No previous conversation.
        */

        if (
            !Array.isArray(history) ||
            history.length === 0
        ) {

            console.log(
                "No previous conversation found."
            );

            return;

        }


        /*
           Clear frontend messages ONLY
           when actual SQLite history exists.

           This prevents the welcome message
           from mixing with old history.
        */

        if (chatMessages) {

            chatMessages.innerHTML = "";

        }


        /*
           Rebuild conversation from SQLite.
        */

        history.forEach(
            function (message) {

                if (
                    !message ||
                    typeof message !==
                    "object"
                ) {

                    return;

                }


                /*
                   USER MESSAGE
                */

                if (
                    message.role ===
                    "user"
                ) {

                    addUserMessage(
                        message.content || ""
                    );

                }


                /*
                   ASSISTANT MESSAGE
                */

                else if (
                    message.role ===
                    "assistant"
                ) {

                    addBotMessage(
                        message.content || ""
                    );

                }

            }
        );


        scrollChat();


        console.log(
            `Loaded ${history.length} messages from SQLite.`
        );

    }

    catch (error) {

        console.error(
            "History loading error:",
            error
        );

    }

}


/* =========================================
   USER MESSAGE
========================================= */

function addUserMessage(
    message
) {

    if (!chatMessages) {

        return;

    }


    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        "message user-message";


    /*
       Use textContent instead of
       innerHTML for user content.

       This prevents HTML injection.
    */

    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";


    const paragraph =
        document.createElement(
            "p"
        );


    paragraph.textContent =
        message ?? "";


    content.appendChild(
        paragraph
    );


    wrapper.appendChild(
        content
    );


    chatMessages.appendChild(
        wrapper
    );


    scrollChat();

}


/* =========================================
   BOT MESSAGE
========================================= */

function addBotMessage(
    message
) {

    if (!chatMessages) {

        return null;

    }


    const id =
        "message-" +
        Date.now() +
        "-" +
        Math.random()
            .toString(36)
            .substring(2, 7);


    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        "message bot-message";


    wrapper.id =
        id;


    wrapper.innerHTML = `
        <div class="message-avatar">

            <img
                src="assets/logo.png"
                alt="Inquisitors AI"
            >

        </div>

        <div class="message-content">

            <p class="bot-response"></p>

            <button
                class="speak-btn"
                type="button"
                title="Read response aloud"
                aria-label="Read response aloud"
            >
                🔊
            </button>

        </div>
    `;


    /*
       IMPORTANT:

       We use textContent after creating
       the HTML structure.

       This means even if the LLM returns
       HTML/JavaScript, it will NOT execute.
    */

    const paragraph =
        wrapper.querySelector(
            ".bot-response"
        );


    if (paragraph) {

        paragraph.innerHTML =
            formatResponse(message);

        const speakButton =
            wrapper.querySelector(".speak-btn");

        if (speakButton) {

            speakButton.addEventListener(
                "click",
                function () {
                    toggleSpeechOutput(
                        speakButton,
                        stripFormatting(message)
                    );
                }
            );

            speakButton.disabled = !speechEnabled || !window.speechSynthesis;

        }

    }


    chatMessages.appendChild(
        wrapper
    );


    scrollChat();


    return id;

}


/* =========================================
   DISPLAY SOURCES
========================================= */

function addSources(
    sources
) {

    if (
        !chatMessages ||
        !Array.isArray(sources) ||
        sources.length === 0
    ) {

        return;

    }


    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        "message bot-message source-message";


    wrapper.innerHTML = `
        <div class="message-avatar">

            <img
                src="assets/logo.png"
                alt="Inquisitors AI"
            >

        </div>

        <div class="message-content">

            <small>
                Knowledge sources
            </small>

            <ul class="source-list"></ul>

        </div>
    `;


    const list =
        wrapper.querySelector(
            ".source-list"
        );


    sources.forEach(
        function (source) {

            const li =
                document.createElement(
                    "li"
                );


            li.textContent =
                source ?? "";


            list.appendChild(
                li
            );

        }
    );


    chatMessages.appendChild(
        wrapper
    );


    scrollChat();

}


/* =========================================
   REMOVE MESSAGE
========================================= */

function removeMessage(
    id
) {

    if (!id) {

        return;

    }


    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.remove();

    }

}


/* =========================================
   CLEAR / NEW CHAT
========================================= */

async function clearChatSession() {

    /*
       IMPORTANT:

       Allow history loading again
       for the new session.
    */

    historyLoaded = false;


    /*
       Store old session before replacing it.
    */

    const oldSessionId =
        SESSION_ID;


    /* =====================================
       DELETE OLD SQLITE HISTORY
    ===================================== */

    try {

        const response =
            await fetch(
                `${HISTORY_API_URL}/${encodeURIComponent(oldSessionId)}`,
                {
                    method: "DELETE",

                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        if (!response.ok) {

            console.warn(
                "SQLite history could not be deleted:",
                response.status
            );

        }

        else {

            console.log(
                "Old SQLite conversation deleted:",
                oldSessionId
            );

        }

    }

    catch (error) {

        console.warn(
            "Clear history error:",
            error
        );

    }


    /* =====================================
       CREATE COMPLETELY NEW SESSION
    ===================================== */

    SESSION_ID =
        createSessionId();


    localStorage.setItem(
        SESSION_STORAGE_KEY,
        SESSION_ID
    );


    console.log(
        "New chat session:",
        SESSION_ID
    );


    /* =====================================
       CLEAR FRONTEND CHAT
    ===================================== */

    if (chatMessages) {

        chatMessages.innerHTML = "";

    }


    /* =====================================
       SHOW WELCOME MESSAGE
    ===================================== */

    addBotMessage(
        "Hello! 👋 I'm the Inquisitors AI Assistant. How can I help you?"
    );

}


/* =========================================
   SUGGESTION BUTTON
========================================= */

function askQuestion(
    question
) {

    if (!userInput) {

        return;

    }


    userInput.value =
        question;


    sendMessage();

}


/* =========================================
   CONTACT SUPPORT
========================================= */

function contactSupport() {

    const supportMessage = `
Inquisitors Society Support Contact

📞 Phone: +92 309 6888664
📧 Email: contact@inquisitors.com
⏰ Hours: Monday-Friday, 9AM-5PM

You can also reach us on:
🌐 Instagram: @inquisitors_society
📘 Facebook: Inquisitors Society Official
💼 LinkedIn: Inquisitors Society

For urgent matters, please call directly.
    `.trim();

    addBotMessage(supportMessage);

}


/* =========================================
   INPUT STATE
========================================= */

function setInputState(
    enabled
) {

    if (userInput) {

        userInput.disabled =
            !enabled;

    }


    /*
       Find send button.

       If your HTML has a specific ID,
       you can use that instead.
    */

    const sendButton =
        document.querySelector(
            ".chat-input-area button"
        );


    if (sendButton) {

        sendButton.disabled =
            !enabled;


        sendButton.style.opacity =
            enabled
                ? "1"
                : "0.6";

    }

}


/* =========================================
   SCROLL CHAT
========================================= */

function scrollChat() {

    if (!chatMessages) {

        return;

    }


    /*
       Small timeout makes scrolling
       reliable after DOM rendering.
    */

    setTimeout(
        () => {

            chatMessages.scrollTop =
                chatMessages.scrollHeight;

        },
        0
    );

}


/* =========================================
   SECTION SCROLL
========================================= */

function scrollToSection(
    id
) {

    const section =
        document.getElementById(
            id
        );


    if (section) {

        section.scrollIntoView({

            behavior:
                "smooth"

        });

    }

}


/* =========================================
   DEMO RESPONSE
========================================= */

async function getDemoResponse(
    message
) {

    await delay(
        500
    );


    return `
Demo mode is currently active.

Please enable the FastAPI backend
to use the real RAG + SQLite chatbot.
`;

}


/* =========================================
   DELAY
========================================= */

function delay(
    ms
) {

    return new Promise(
        resolve =>
            setTimeout(
                resolve,
                ms
            )
    );

}


/* =========================================
   HTML ESCAPING
========================================= */

function escapeHTML(
    text
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        text ?? "";


    return div.innerHTML;

}


/* =========================================
   FORMAT AI RESPONSE
========================================= */

function formatResponse(
    text
) {

    if (!text) {

        return "";

    }


    const escaped = escapeHTML(text);

    return escaped
        .replace(
            /\r?\n/g,
            "<br>"
        )
        .replace(
            /\*\*(.+?)\*\*/g,
            "<strong>$1</strong>"
        )
        .replace(
            /`([^`]+)`/g,
            "<code>$1</code>"
        )
        .replace(
            /(^|<br>)\s*[-*]\s+/g,
            "$1&#8226; "
        )
        .replace(
            /(https?:\/\/[^\s<]+)/g,
            function (url) {
                const cleanUrl = url.replace(/[.,!?;:]+$/, "");
                const trailing = url.slice(cleanUrl.length);

                return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer">${cleanUrl}</a>${trailing}`;
            }
        );

}


function stripFormatting(text) {

    return String(text ?? "")
        .replace(/[*_`#]/g, "")
        .replace(/https?:\/\/\S+/g, "official link")
        .replace(/\s+/g, " ")
        .trim();

}


/* =========================================
   HERO DEPTH INTERACTION
========================================= */

const tiltCard = document.querySelector("[data-tilt-card]");

if (tiltCard && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {

    tiltCard.addEventListener("pointermove", function (event) {

        const bounds = tiltCard.getBoundingClientRect();
        const x = (event.clientX - bounds.left) / bounds.width - 0.5;
        const y = (event.clientY - bounds.top) / bounds.height - 0.5;

        tiltCard.style.transform =
            `rotateX(${y * -5}deg) rotateY(${x * 5}deg)`;

    });

    tiltCard.addEventListener("pointerleave", function () {

        tiltCard.style.transform = "rotateX(0deg) rotateY(0deg)";

    });

}


/* =========================================
   INITIALIZATION
========================================= */

console.log(
    "======================================"
);

console.log(
    "Inquisitors AI Assistant"
);

console.log(
    "Session ID:",
    SESSION_ID
);

console.log(
    "Backend:",
    CHAT_API_URL
);

console.log(
    "SQLite session memory: ENABLED"
);

console.log(
    "History loader: ENABLED"
);

console.log(
    "======================================"
);