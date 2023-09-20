require("dotenv").config();
const axios = require("axios");
async function sendTextToApi(message, userId, username) {
  try {
    const response = await axios.post(
      `${process.env.BOT_API_URL}/generate_response_llm`,
      { message: message, user_id: userId.toString(), user_name: username }
    );
    return response.data.message;
  } catch (err) {
    console.error("Error sending audio data to the API:", err);
  }
  // Use axios to send the audio data directly to your API
}

async function sendVoiceToApi(filePath, userId, username) {
  try {
    const response = await axios.post(
      `${process.env.BOT_API_URL}/generate_response_llm_audio`,
      {
        audio_file_path: filePath,
        user_id: userId.toString(),
        user_name: username,
      }
    );
    return response.data.message;
  } catch (err) {
    console.error("Error sending audio data to the API:", err);
  }
  // Use axios to send the audio data directly to your API
}
function userInfo(message) {
  const username = message.from.username;
  const userId = message.from.id;
  const chatId = message.chat.id;

  return { chatId, userId, username };
}

async function sendBalanceCommandToApi(userId, username) {
  try {
    const response = await axios.post(
      `${process.env.BOT_API_URL}/generate_response_llm_audio`,
      { user_id: userId.toString(), user_name: username }
    );
    return response.data.message;
  } catch (err) {
    console.error("Error sending audio data to the API:", err);
  }
  // Use axios to send the audio data directly to your API
}

async function sendClearCommandToApi(userId, username) {
  try {
    const response = await axios.post(
      `${process.env.BOT_API_URL}/generate_response_llm_audio`,
      { user_id: userId.toString(), user_name: username }
    );
    return response.data.message;
  } catch (err) {
    console.error("Error sending audio data to the API:", err);
  }
  // Use axios to send the audio data directly to your API
}

module.exports = {
  sendTextToApi,
  sendVoiceToApi,
  userInfo,
  sendClearCommandToApi,
  sendBalanceCommandToApi,
};
