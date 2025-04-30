const sendText = async (to, message) => {
  try {
    const res = await fetch('http://localhost:5000/send-sms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to, message })
    });

    const data = await res.json();
    return data;
  } catch (error) {
    console.error('Send Text Error:', error);
    return { success: false, error: error.message };
  }
};

export default sendText;
