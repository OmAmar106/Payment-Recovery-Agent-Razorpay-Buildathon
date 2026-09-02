const RAZORPAY_KEY_ID = "rzp_test_TWZ4T6BykEuzlu";

const BACKEND_URL = "http://127.0.0.1:8000";

let socket = null;
let currentOrderId = null;
let retryCount = 0;
let maxRetries = 2;

function connectWebSocket(orderId) {
    if (socket) {
        socket.close();
        socket = null;
    }

    socket = new WebSocket(
        `ws://127.0.0.1:8000/ws/${orderId}`
    );

    socket.onopen = function () {
        console.log(
            "WebSocket connected:",
            orderId
        );
    };

    socket.onmessage = function (event) {
        console.log(
            "Recovery message:",
            event.data
        );

        try {
            const data = JSON.parse(event.data);

            handleRecoveryAction(data);
        } catch (error) {
            console.error(
                "Invalid WebSocket message:",
                error
            );
        }
    };

    socket.onerror = function (error) {
        console.error(
            "WebSocket error:",
            error
        );
    };

    socket.onclose = function () {
        console.log(
            "WebSocket disconnected"
        );

        socket = null;
    };
}

function handleRecoveryAction(data) {
    const action = data.action;

    if (action === "RETRY") {
        const delay =
            Number(data.delay || 10);

        if (retryCount >= maxRetries) {
            showStatus(
                "failure",
                "Payment could not be recovered",
                "We tried the available recovery options. Please try again manually."
            );

            resetButton();

            return;
        }

        retryCount++;

        showStatus(
            "failure",
            "Recovering your payment",
            `We'll retry your payment in ${delay} seconds.`
        );

        setTimeout(function () {
            startPayment(true);
        }, delay * 1000);

        return;
    }

    if (action === "WAIT") {
        const delay =
            Number(data.delay || 10);

        showStatus(
            "failure",
            "Payment recovery in progress",
            `We're waiting ${delay} seconds before trying the next step.`
        );

        return;
    }

    if (action === "SEND_MESSAGE") {
        showStatus(
            "failure",
            "Payment issue detected",
            data.message ||
            "We've sent you instructions to complete your payment."
        );

        resetButton();

        return;
    }

    if (action === "PAYMENT_LINK") {
        showStatus(
            "failure",
            "New payment link generated",
            data.message ||
            "We've generated a new payment link for you."
        );

        if (data.url) {
            setTimeout(function () {
                window.location.href = data.url;
            }, 1500);
        }

        return;
    }

    if (action === "HUMAN") {
        showStatus(
            "failure",
            "Support agent notified",
            data.message ||
            "A human support agent will help you complete your payment."
        );

        resetButton();

        return;
    }

    console.warn(
        "Unknown recovery action:",
        action
    );
}

async function startPayment(isRetry = false) {
    const name =
        document
            .getElementById("name")
            .value
            .trim();

    const email =
        document
            .getElementById("email")
            .value
            .trim();

    const phone =
        document
            .getElementById("phone")
            .value
            .trim();

    if (!isRetry) {
        if (!name) {
            alert("Please enter your name.");
            return;
        }

        if (!email) {
            alert("Please enter your email.");
            return;
        }

        if (!phone) {
            alert("Please enter your phone number.");
            return;
        }

        retryCount = 0;
    }

    const button =
        document.getElementById(
            "payButton"
        );

    button.disabled = true;

    button.innerText =
        isRetry
            ? "Retrying payment..."
            : "Creating secure order...";

    try {
        const response =
            await fetch(
                `${BACKEND_URL}/create-order`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        email: email,
                        phone: phone
                    })
                }
            );

        if (!response.ok) {
            throw new Error(
                "Could not create Razorpay order."
            );
        }

        const order =
            await response.json();

        currentOrderId =
            order.id;

        connectWebSocket(
            currentOrderId
        );

        const options = {
            key: RAZORPAY_KEY_ID,

            amount: order.amount,

            currency: order.currency,

            name: "PayFlow",

            description:
                "Payment Recovery Agent Demo",

            order_id: order.id,

            prefill: {
                name: name,
                email: email,
                contact: phone
            },

            theme: {
                color: "#2563eb"
            },

            handler: function (response) {
                console.log(
                    "Payment successful:",
                    response
                );

                showStatus(
                    "success",
                    "Payment successful",
                    "Your payment was completed successfully. Payment ID: " +
                    response.razorpay_payment_id
                );

                retryCount = 0;

                disconnectWebSocket();
            },

            modal: {
                ondismiss: function () {
                    resetButton();
                }
            }
        };

        const razorpay =
            new Razorpay(options);

        razorpay.on(
            "payment.failed",
            function (response) {
                console.log(
                    "Payment failed:",
                    response.error
                );

                showStatus(
                    "failure",
                    "Payment failed",
                    response.error.description ||
                    "The payment could not be completed. Our recovery system is analyzing the failure."
                );

                resetButton();
            }
        );

        razorpay.open();

        resetButton();

    } catch (error) {
        console.error(error);

        showStatus(
            "failure",
            "Something went wrong",
            error.message
        );

        resetButton();
    }
}

function disconnectWebSocket() {
    if (socket) {
        socket.close();
        socket = null;
    }
}

function resetButton() {
    const button =
        document.getElementById(
            "payButton"
        );

    button.disabled = false;

    button.innerText =
        "Pay ₹500";
}

function showStatus(
    type,
    title,
    message
) {
    const overlay =
        document.getElementById(
            "statusOverlay"
        );

    const icon =
        document.getElementById(
            "statusIcon"
        );

    const titleElement =
        document.getElementById(
            "statusTitle"
        );

    const messageElement =
        document.getElementById(
            "statusMessage"
        );

    icon.className =
        "status-icon " + type;

    if (type === "success") {
        icon.innerText = "✓";
    } else {
        icon.innerText = "×";
    }

    titleElement.innerText =
        title;

    messageElement.innerText =
        message;

    overlay.classList.add(
        "show"
    );
}

function closeStatus() {
    document
        .getElementById("statusOverlay")
        .classList
        .remove("show");
}